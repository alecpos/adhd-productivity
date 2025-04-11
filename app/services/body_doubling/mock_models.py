"""Mock models for testing the Body Doubling Service.

This module contains simplified mock versions of models that are required
by SQLAlchemy relationships but might not be needed for actual testing.
"""

from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime

# Mock base model
class MockBaseModel:
    """Base model for all mock models."""

    id: UUID = uuid4()
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

# Mock TaskCategoryModel
class MockTaskCategoryModel(MockBaseModel):
    """Mock TaskCategoryModel for testing.

    This allows UserModel to load without requiring the actual TaskCategoryModel.
    """

    def __init__(self, user_id: UUID, name: str, description: Optional[str] = None):
        """Initialize the mock task category.

        Args:
            user_id: ID of the user who owns the category
            name: Name of the category
            description: Optional description
        """
        self.user_id = user_id
        self.name = name
        self.description = description

    # Mock relationship
    user = None
