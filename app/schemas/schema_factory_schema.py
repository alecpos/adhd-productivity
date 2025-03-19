"""Schema factory for dynamic schema creation."""
from typing import Any, Dict, Optional, Type, TypeVar

from pydantic import BaseModel, Field, create_model

from app.schemas.base_schema import BaseSchema, TimestampedSchema
from app.core.types import NoneSchema

T = TypeVar("T", bound=BaseSchema)

class SchemaFactory(BaseModel):
    """Factory for creating dynamic schemas."""

    _schema_registry: Dict[str, Type[BaseSchema]] = {}

    @classmethod
    def register_schema(cls, name: str, schema_class: Type[T]) -> NoneSchema:
        """Register a schema class with the factory."""
        if name in cls._schema_registry:
            raise ValueError(f"Schema {name} is already registered")
        cls._schema_registry[name] = schema_class

    @classmethod
    def get_schema(cls, name: str) -> Optional[Type[BaseSchema]]:
        """Retrieve a registered schema class by name."""
        return cls._schema_registry.get(name)

    @classmethod
    def create_schema(
        cls, name: str, fields: Dict[str, Any], base_class: Type[T] = BaseSchema
    ) -> Type[T]:
        """Create a new schema class with the given fields and base class."""
        if name in cls._schema_registry:
            raise ValueError(f"Schema {name} is already registered")

        schema_class = create_model(name, __base__=base_class, **fields)

        cls._schema_registry[name] = schema_class

    @classmethod
    def create_timestamped_schema(
        cls, name: str, fields: Dict[str, Any]
    ) -> Type[TimestampedSchema]:
        """Create a new timestamped schema class."""
        return cls.create_schema(name, fields, base_class=TimestampedSchema)

    @classmethod
    def list_schemas(cls) -> Dict[str, Type[BaseSchema]]:
        """List all registered schemas."""
        return cls._schema_registry.copy()

__all__ = ["SchemaFactory"]
