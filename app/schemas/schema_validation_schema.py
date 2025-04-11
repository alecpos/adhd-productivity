"""Schema validation utilities and schemas."""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel


T = TypeVar("T")
CallableT = TypeVar("CallableT", bound=Callable)


class ValidationError(Exception):
    """Custom validation error."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ValidationRule(BaseModel):
    """Base class for validation rules."""

    field_name: str
    validation_func: Optional[Callable[[Any], bool]] = None
    error_message: str = ""

    def validate(self, value: Any) -> bool:
        """Validate a value using the validation function."""
        if self.validation_func:
            return self.validation_func(value)
        return True  # Base validation always passes if no function provided


class RequiredFieldRule(ValidationRule):
    """Validation rule for required fields."""

    def __init__(self, field_name: str, error_message: str):
        super().__init__(field_name=field_name, error_message=error_message)

    def validate(self, value: Any) -> bool:
        """Validate that a field is not None or empty."""
        return value is not None and value != ""


class DateRangeRule(ValidationRule):
    """Validation rule for date ranges."""

    start_field: str
    end_field: str

    def __init__(self, start_field: str, end_field: str, error_message: str):
        super().__init__(field_name=f"{start_field},{end_field}", error_message=error_message)
        self.start_field = start_field
        self.end_field = end_field

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate that start date is before end date."""
        start = data.get(self.start_field)
        end = data.get(self.end_field)
        return bool(start and end and start < end)


class UniqueFieldRule(ValidationRule):
    """Validation rule for unique fields."""

    def __init__(self, field_name: str, error_message: str):
        super().__init__(field_name=field_name, error_message=error_message)

    def validate(self, value: Any, existing_values: Optional[List[Any]] = None) -> bool:
        """Validate that a field value is unique."""
        if existing_values is None:
            return True
        return value not in existing_values


def create_validation_rule(
    field_name: str, validation_func: Callable[[Any], bool], error_message: str
) -> ValidationRule:
    """Factory function to create custom validation rules."""
    return ValidationRule(
        field_name=field_name, validation_func=validation_func, error_message=error_message
    )


class SchemaValidator(BaseModel):
    """Schema validator class."""

    rules: Dict[str, List[ValidationRule]] = {}

    def add_rule(self, schema_name: str, rule: ValidationRule) -> None:
        """Add a validation rule for a schema."""
        if schema_name not in self.rules:
            self.rules[schema_name] = []
        self.rules[schema_name].append(rule)

    def validate(self, schema_name: str, data: Dict[str, Any]) -> bool:
        """Validate data against all rules for a schema."""
        if schema_name not in self.rules:
            return True

        for rule in self.rules[schema_name]:
            if not rule.validate(data.get(rule.field_name)):
                raise ValidationError(rule.error_message)
        return True


def validate_schema(schema_class: Type[BaseModel]) -> Callable[[CallableT], CallableT]:
    """Decorator for schema validation."""

    def decorator(func: CallableT) -> CallableT:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract data to validate
            data = kwargs.get("data") or args[-1]

            # Validate against schema
            try:
                validated_data = schema_class(**data)
                kwargs["data"] = validated_data
                return await func(*args, **kwargs)
            except Exception as e:
                raise ValidationError(str(e))

        return wrapper  # type: ignore

    return decorator


__all__ = [
    "ValidationRule",
    "RequiredFieldRule",
    "DateRangeRule",
    "UniqueFieldRule",
    "create_validation_rule",
    "SchemaValidator",
    "validate_schema",
    "ValidationError",
]
