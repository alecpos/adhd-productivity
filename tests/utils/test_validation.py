"""
Tests for validation utilities.

This module contains tests for the enhanced validation utilities.
"""

import pytest
import re
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError, validator, BaseModel

from app.utils.validation import (
    validate_email_address,
    ValidatorRegistry,
    add_validator_to_model,
    BaseModelWithValidators,
    validate_at_least_one_field_present,
    validate_dependent_fields,
    validate_mutually_exclusive_fields,
)

# Mock the validate_email_address function to bypass actual email validation
# which may have issues with network connectivity or library version differences
def mock_validate_email_address(email: str) -> str:
    """Mock of validate_email_address for testing."""
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Invalid email format")
    return email


def test_password_validator_valid():
    """Test password_validator function with valid password."""
    valid_password = "Password123!"
    result = ValidatorRegistry.password_validator(valid_password)
    assert result == valid_password


def test_password_validator_too_short():
    """Test password_validator function with password that's too short."""
    short_password = "Pass1!"
    with pytest.raises(ValueError) as excinfo:
        ValidatorRegistry.password_validator(short_password)
    assert "at least 8 characters" in str(excinfo.value)


def test_password_validator_no_uppercase():
    """Test password_validator function with password missing uppercase."""
    password = "password123!"
    with pytest.raises(ValueError) as excinfo:
        ValidatorRegistry.password_validator(password)
    assert "uppercase letter" in str(excinfo.value)


def test_password_validator_no_lowercase():
    """Test password_validator function with password missing lowercase."""
    password = "PASSWORD123!"
    with pytest.raises(ValueError) as excinfo:
        ValidatorRegistry.password_validator(password)
    assert "lowercase letter" in str(excinfo.value)


def test_password_validator_no_digit():
    """Test password_validator function with password missing digit."""
    password = "Password!"
    with pytest.raises(ValueError) as excinfo:
        ValidatorRegistry.password_validator(password)
    assert "digit" in str(excinfo.value)


def test_password_validator_no_special():
    """Test password_validator function with password missing special character."""
    password = "Password123"
    with pytest.raises(ValueError) as excinfo:
        ValidatorRegistry.password_validator(password)
    assert "special character" in str(excinfo.value)


def test_future_date_validator_valid():
    """Test future_date_validator function with valid future date."""
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    result = ValidatorRegistry.future_date_validator(future_date)
    assert result == future_date


def test_future_date_validator_past():
    """Test future_date_validator function with past date."""
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    with pytest.raises(ValueError) as excinfo:
        ValidatorRegistry.future_date_validator(past_date)
    assert "future" in str(excinfo.value)


def test_past_date_validator_valid():
    """Test past_date_validator function with valid past date."""
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    result = ValidatorRegistry.past_date_validator(past_date)
    assert result == past_date


def test_past_date_validator_future():
    """Test past_date_validator function with future date."""
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    with pytest.raises(ValueError) as excinfo:
        ValidatorRegistry.past_date_validator(future_date)
    assert "past" in str(excinfo.value)


def test_positive_number_validator_valid():
    """Test positive_number_validator function with valid positive number."""
    value = 10
    result = ValidatorRegistry.positive_number_validator(value)
    assert result == value


def test_positive_number_validator_zero():
    """Test positive_number_validator function with zero."""
    value = 0
    with pytest.raises(ValueError) as excinfo:
        ValidatorRegistry.positive_number_validator(value)
    assert "positive" in str(excinfo.value)


def test_positive_number_validator_negative():
    """Test positive_number_validator function with negative number."""
    value = -5
    with pytest.raises(ValueError) as excinfo:
        ValidatorRegistry.positive_number_validator(value)
    assert "positive" in str(excinfo.value)


def test_non_negative_number_validator_valid():
    """Test non_negative_number_validator function with valid non-negative number."""
    value = 0
    result = ValidatorRegistry.non_negative_number_validator(value)
    assert result == value


def test_non_negative_number_validator_positive():
    """Test non_negative_number_validator function with positive number."""
    value = 5
    result = ValidatorRegistry.non_negative_number_validator(value)
    assert result == value


def test_non_negative_number_validator_negative():
    """Test non_negative_number_validator function with negative number."""
    value = -5
    with pytest.raises(ValueError) as excinfo:
        ValidatorRegistry.non_negative_number_validator(value)
    assert "non-negative" in str(excinfo.value)


def test_priority_validator_valid():
    """Test priority_validator function with valid priority."""
    priorities = ["low", "medium", "high"]
    for priority in priorities:
        result = ValidatorRegistry.priority_validator(priority)
        assert result == priority


def test_priority_validator_invalid():
    """Test priority_validator function with invalid priority."""
    priority = "invalid"
    with pytest.raises(ValueError) as excinfo:
        ValidatorRegistry.priority_validator(priority)
    assert "Priority must be one of" in str(excinfo.value)


def test_phone_number_validator_valid():
    """Test phone_number_validator function with valid phone number."""
    phone = "1234567890"  # 10 digits, assumed US
    result = ValidatorRegistry.phone_number_validator(phone)
    assert result == "+1" + phone


def test_phone_number_validator_formatted():
    """Test phone_number_validator function with formatted phone number."""
    phone = "(123) 456-7890"
    result = ValidatorRegistry.phone_number_validator(phone)
    assert result == "+11234567890"


def test_phone_number_validator_international():
    """Test phone_number_validator function with international phone number."""
    phone = "+447911123456"  # UK mobile
    result = ValidatorRegistry.phone_number_validator(phone)
    assert result == phone


def test_phone_number_validator_too_short():
    """Test phone_number_validator function with too short phone number."""
    phone = "123456"
    with pytest.raises(ValueError) as excinfo:
        ValidatorRegistry.phone_number_validator(phone)
    assert "must be between 10 and 15 digits" in str(excinfo.value)


class SimpleTestModel(BaseModel):
    """Simple test model for manual validation."""
    field: str
    
    @validator('field')
    def validate_field(cls, v):
        if v != "test":
            raise ValueError("Value must be 'test'")
        return v


def test_simple_validation():
    """Test simple validation with a basic Pydantic model."""
    # Test with valid value
    model = SimpleTestModel(field="test")
    assert model.field == "test"
    
    # Test with invalid value
    with pytest.raises(Exception) as excinfo:
        SimpleTestModel(field="invalid")
    assert "Value must be 'test'" in str(excinfo.value)


def test_validate_at_least_one_field_present():
    """Test validate_at_least_one_field_present function."""
    fields = ["field1", "field2"]
    validator_fn = validate_at_least_one_field_present(fields)
    
    # Create a model with the validator
    class TestModel(BaseModel):
        field1: str = None
        field2: str = None
        
        _validate_fields = validator_fn
    
    # Test with one field present
    model = TestModel(field1="value")
    assert model.field1 == "value"
    
    # Test with both fields present
    model = TestModel(field1="value1", field2="value2")
    assert model.field1 == "value1"
    assert model.field2 == "value2"
    
    # Test with no fields present
    with pytest.raises(Exception) as excinfo:
        TestModel()
    assert "At least one of these fields must be provided" in str(excinfo.value)


def test_validate_dependent_fields():
    """Test validate_dependent_fields function."""
    main_field = "main"
    dependent_fields = ["dependent1", "dependent2"]
    validator_fn = validate_dependent_fields(main_field, dependent_fields)
    
    # Create a model with the validator
    class TestModel(BaseModel):
        main: str = None
        dependent1: str = None
        dependent2: str = None
        
        _validate_fields = validator_fn
    
    # Test with main field not present
    model = TestModel()
    assert model.main is None
    
    # Test with main field and all dependent fields present
    model = TestModel(main="value", dependent1="value1", dependent2="value2")
    assert model.main == "value"
    assert model.dependent1 == "value1"
    assert model.dependent2 == "value2"
    
    # Test with main field present but dependent field missing
    with pytest.raises(Exception) as excinfo:
        TestModel(main="value", dependent1="value1")
    assert "is required when" in str(excinfo.value)


def test_validate_mutually_exclusive_fields():
    """Test validate_mutually_exclusive_fields function."""
    fields = ["field1", "field2"]
    validator_fn = validate_mutually_exclusive_fields(fields)
    
    # Create a model with the validator
    class TestModel(BaseModel):
        field1: str = None
        field2: str = None
        
        _validate_fields = validator_fn
    
    # Test with one field present
    model = TestModel(field1="value")
    assert model.field1 == "value"
    
    # Test with no fields present
    model = TestModel()
    assert model.field1 is None
    assert model.field2 is None
    
    # Test with both fields present
    with pytest.raises(Exception) as excinfo:
        TestModel(field1="value1", field2="value2")
    assert "Only one of these fields can be provided" in str(excinfo.value) 