"""Schema utility functions and types."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union
from uuid import UUID
from pydantic import BaseModel, Field, create_model

from app.schemas.base_schema import BaseSchema

T = TypeVar("T", bound=BaseModel)
S = TypeVar("S", bound=BaseModel)


def merge_schemas(*schemas: Type[BaseModel], name: str = "MergedSchema") -> Type[BaseModel]:
    """Merge multiple schemas into a single schema with proper field handling."""
    fields: Dict[str, Any] = {}

    for schema in schemas:
        # Merge fields with their metadata
        for field_name, field in schema.model_fields.items():
            if field_name not in fields:
                field_kwargs = {
                    "default": field.default if field.default is not None else ...,
                    "description": field.description,
                }

                # Handle extra schema attributes if they exist
                if field.json_schema_extra:
                    field_kwargs.update(field.json_schema_extra)

                fields[field_name] = (
                    field.annotation,
                    Field(**field_kwargs),
                )

    # Create and return the merged schema
    return type(
        name,
        (BaseModel,),
        {
            "__annotations__": {k: v[0] for k, v in fields.items()},
            **{k: v[1] for k, v in fields.items()},
        },
    )


def create_schema_subset(
    base_schema: Type[BaseModel], fields_to_include: List[str], name: str = "SubsetSchema"
) -> Type[BaseModel]:
    """Create a new schema with only specified fields from base schema."""
    fields: Dict[str, Any] = {}

    for field_name in fields_to_include:
        if field_name in base_schema.model_fields:
            field = base_schema.model_fields[field_name]
            field_kwargs = {
                "default": field.default if field.default is not None else ...,
                "description": field.description,
            }

            # Handle extra schema attributes if they exist
            if field.json_schema_extra:
                field_kwargs.update(field.json_schema_extra)

            fields[field_name] = (
                field.annotation,
                Field(**field_kwargs),
            )
        else:
            raise ValueError(f"Field {field_name} not found in base schema")

    # Create and return the subset schema
    return type(
        name,
        (BaseModel,),
        {
            "__annotations__": {k: v[0] for k, v in fields.items()},
            **{k: v[1] for k, v in fields.items()},
        },
    )


def schema_to_dict(schema: BaseModel, exclude_none: bool = True) -> Dict[str, Any]:
    """Convert a schema instance to a dictionary with proper type handling."""

    def convert_value(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, BaseModel):
            return schema_to_dict(value, exclude_none)
        if isinstance(value, list):
            return [convert_value(item) for item in value]
        if isinstance(value, dict):
            return {k: convert_value(v) for k, v in value.items()}
        if isinstance(value, set):
            return [convert_value(item) for item in value]
        return value

    data = schema.model_dump(exclude_none=exclude_none)
    return {key: convert_value(value) for key, value in data.items()}


def dict_to_schema(data: Dict[str, Any], schema_class: Type[T]) -> T:
    """Convert a dictionary to a schema instance with proper type handling."""

    def convert_value(value: Any, expected_type: Type) -> Any:
        if value is None:
            return None

        if isinstance(expected_type, type) and issubclass(expected_type, BaseModel):
            return dict_to_schema(value, expected_type)

        if expected_type == datetime and isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        if expected_type == UUID and isinstance(value, str):
            return UUID(value)

        # Handle generic types
        origin = getattr(expected_type, "__origin__", None)
        if origin is not None:
            args = getattr(expected_type, "__args__", [])
            if origin == list:
                return [convert_value(item, args[0]) for item in value]
            if origin == set:
                return {convert_value(item, args[0]) for item in value}
            if origin == dict:
                return {
                    convert_value(k, args[0]): convert_value(v, args[1]) for k, v in value.items()
                }

        return value

    converted_data = {}
    for field_name, field in schema_class.model_fields.items():
        if field_name in data:
            converted_data[field_name] = convert_value(data[field_name], field.annotation)

    return schema_class(**converted_data)


__all__ = [
    "merge_schemas",
    "create_schema_subset",
    "schema_to_dict",
    "dict_to_schema",
]
