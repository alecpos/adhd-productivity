"""
Validation Utilities

This module provides enhanced validation utilities for Pydantic models
to ensure consistent validation across the API.
"""

import re
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, get_type_hints

from datetime import datetime, timezone
from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, Field, validator, root_validator

# Type variable for generic models
T = TypeVar('T', bound=BaseModel)


def validate_email_address(email: str) -> str:
    """
    Validate an email address using email-validator.

    Args:
        email: The email address to validate

    Returns:
        The normalized email address if valid

    Raises:
        ValueError: If the email is invalid
    """
    try:
        # Skip MX validation for testing purposes and common domains
        valid = validate_email(email, mode='skip_mx')
        return valid.email
    except EmailNotValidError as e:
        raise ValueError(f"Invalid email address: {str(e)}")


class ValidatorRegistry:
    """Registry of common validators for Pydantic models."""

    @staticmethod
    def password_validator(password: str) -> str:
        """
        Validate password strength.

        Args:
            password: The password to validate

        Returns:
            The password if valid

        Raises:
            ValueError: If the password is invalid
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r'[0-9]', password):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain at least one special character")

        return password

    @staticmethod
    def future_date_validator(date: datetime) -> datetime:
        """
        Validate that a date is in the future.

        Args:
            date: The date to validate

        Returns:
            The date if valid

        Raises:
            ValueError: If the date is not in the future
        """
        now = datetime.now(timezone.utc)
        if date <= now:
            raise ValueError("Date must be in the future")
        return date

    @staticmethod
    def past_date_validator(date: datetime) -> datetime:
        """
        Validate that a date is in the past.

        Args:
            date: The date to validate

        Returns:
            The date if valid

        Raises:
            ValueError: If the date is not in the past
        """
        now = datetime.now(timezone.utc)
        if date >= now:
            raise ValueError("Date must be in the past")
        return date

    @staticmethod
    def positive_number_validator(value: Union[int, float]) -> Union[int, float]:
        """
        Validate that a number is positive.

        Args:
            value: The number to validate

        Returns:
            The number if valid

        Raises:
            ValueError: If the number is not positive
        """
        if value <= 0:
            raise ValueError("Value must be positive")
        return value

    @staticmethod
    def non_negative_number_validator(value: Union[int, float]) -> Union[int, float]:
        """
        Validate that a number is non-negative.

        Args:
            value: The number to validate

        Returns:
            The number if valid

        Raises:
            ValueError: If the number is negative
        """
        if value < 0:
            raise ValueError("Value must be non-negative")
        return value

    @staticmethod
    def priority_validator(priority: str) -> str:
        """
        Validate task priority.

        Args:
            priority: The priority to validate

        Returns:
            The priority if valid

        Raises:
            ValueError: If the priority is invalid
        """
        valid_priorities = ["low", "medium", "high"]
        if priority.lower() not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return priority.lower()

    @staticmethod
    def phone_number_validator(phone: str) -> str:
        """
        Validate phone number format.

        Args:
            phone: The phone number to validate

        Returns:
            The normalized phone number if valid

        Raises:
            ValueError: If the phone number is invalid
        """
        # Remove all non-numeric characters
        clean_phone = re.sub(r'\D', '', phone)

        # Check if it's a valid phone number length
        if len(clean_phone) < 10 or len(clean_phone) > 15:
            raise ValueError("Phone number must be between 10 and 15 digits")

        # Format the phone number
        if len(clean_phone) == 10:
            return f"+1{clean_phone}"  # Assume US number
        elif len(clean_phone) > 10:
            return f"+{clean_phone}"

        return clean_phone


def add_validator_to_model(
    model_class: Type[T], field_name: str, validator_fn: Callable[[Any], Any]
) -> Type[T]:
    """
    Dynamically add a validator to a Pydantic model class.

    Args:
        model_class: The Pydantic model class to modify
        field_name: The field to validate
        validator_fn: The validator function

    Returns:
        The modified model class
    """
    validator_name = f"validate_{field_name}"

    # For newer versions of Pydantic, we need to use decorator with field_validators
    def dynamic_validator(cls, v, info):
        try:
            return validator_fn(v)
        except ValueError as e:
            raise ValueError(str(e))

    # Add the validator to the model
    setattr(model_class, validator_name, dynamic_validator)

    # Update the model's validators dict to include this validator
    if not hasattr(model_class, "model_config"):
        model_class.model_config = {}

    if not hasattr(model_class, "validate_" + field_name):
        model_class.validate_assignment = True

    return model_class


def validate_at_least_one_field_present(fields: List[str]) -> Callable:
    """
    Create a root validator that ensures at least one of the specified fields is present.

    Args:
        fields: List of field names to check

    Returns:
        A root validator function
    """
    @root_validator(pre=True)
    def validate_fields(cls, values):
        if not any(field in values and values[field] is not None for field in fields):
            raise ValueError(f"At least one of these fields must be provided: {', '.join(fields)}")
        return values

    return validate_fields


def validate_dependent_fields(
    main_field: str, dependent_fields: List[str], check_value: Any = None
) -> Callable:
    """
    Create a root validator that ensures dependent fields are present if the main field is present.

    Args:
        main_field: The main field
        dependent_fields: Fields that must be present if the main field is present
        check_value: If provided, the dependent fields are only required when the main field
                     has this specific value

    Returns:
        A root validator function
    """
    @root_validator(pre=True)
    def validate_fields(cls, values):
        if main_field in values and values[main_field] is not None:
            # If check_value is provided, only validate when main field matches the check_value
            if check_value is not None and values[main_field] != check_value:
                return values

            for field in dependent_fields:
                if field not in values or values[field] is None:
                    raise ValueError(f"{field} is required when {main_field} is provided")
        return values

    return validate_fields


def validate_mutually_exclusive_fields(fields: List[str]) -> Callable:
    """
    Create a root validator that ensures only one of the specified fields is present.

    Args:
        fields: List of field names that should be mutually exclusive

    Returns:
        A root validator function
    """
    @root_validator(pre=True)
    def validate_fields(cls, values):
        present_fields = [field for field in fields if field in values and values[field] is not None]
        if len(present_fields) > 1:
            raise ValueError(f"Only one of these fields can be provided: {', '.join(fields)}")
        return values

    return validate_fields


# Example BaseModel with common validators
class BaseModelWithValidators(BaseModel):
    """Base model with common validators."""

    # Override __init_subclass__ to add validators automatically
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Get type hints for the class
        hints = get_type_hints(cls)

        # For Pydantic v2, we need to use model_config
        if not hasattr(cls, "model_config"):
            cls.model_config = {}

        # Add validators based on field names and types
        for field_name, field_type in hints.items():
            # Skip private fields and fields without validators
            if field_name.startswith('_'):
                continue

            # Add email validator for email fields
            if field_name in ('email', 'email_address'):
                add_validator_to_model(cls, field_name, validate_email_address)

            # Add password validator for password fields
            if field_name in ('password', 'new_password'):
                add_validator_to_model(cls, field_name, ValidatorRegistry.password_validator)

            # Add date validators
            if field_name.endswith('_date') or field_name.endswith('_at'):
                if field_name.startswith('due_') or field_name.startswith('future_'):
                    add_validator_to_model(cls, field_name, ValidatorRegistry.future_date_validator)
                if field_name.startswith('birth_') or field_name.startswith('past_'):
                    add_validator_to_model(cls, field_name, ValidatorRegistry.past_date_validator)

            # Add number validators
            if any(field_name.endswith(suffix) for suffix in ('_count', '_amount', '_duration')):
                add_validator_to_model(cls, field_name, ValidatorRegistry.non_negative_number_validator)

            # Add priority validator
            if field_name == 'priority':
                add_validator_to_model(cls, field_name, ValidatorRegistry.priority_validator)

            # Add phone validator
            if field_name in ('phone', 'phone_number', 'mobile'):
                add_validator_to_model(cls, field_name, ValidatorRegistry.phone_number_validator)
