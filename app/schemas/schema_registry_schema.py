"""Schema registry for managing and validating schemas."""

from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.schemas.schema_factory_schema import SchemaFactory


T = TypeVar("T", bound=BaseModel)


class SchemaRegistry(BaseModel):
    """Registry for managing and validating schemas."""

    factory: SchemaFactory = Field(default_factory=SchemaFactory)
    validation_rules: Dict[str, List[tuple[Callable[[Any], bool], str]]] = Field(
        default_factory=dict, description="Validation rules for each schema"
    )
    schema_versions: Dict[str, str] = Field(
        default_factory=dict, description="Version information for each schema"
    )
    schema_dependencies: Dict[str, List[str]] = Field(
        default_factory=dict, description="Dependencies between schemas"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

    def register_validation_rule(
        self, schema_name: str, rule: Callable[[Any], bool], error_message: str
    ) -> None:
        """Register a validation rule for a specific schema.

        Args:
            schema_name: Name of the schema to add the rule to
            rule: Validation function that returns True if valid
            error_message: Message to show if validation fails
        """
        if schema_name not in self.validation_rules:
            self.validation_rules[schema_name] = []
        self.validation_rules[schema_name].append((rule, error_message))

    def register_schema_version(self, schema_name: str, version: str) -> None:
        """Register a schema version.

        Args:
            schema_name: Name of the schema
            version: Version string (e.g. "1.0.0")
        """
        self.schema_versions[schema_name] = version

    def register_schema_dependencies(self, schema_name: str, dependencies: List[str]) -> None:
        """Register dependencies for a schema.

        Args:
            schema_name: Name of the schema
            dependencies: List of schema names this schema depends on
        """
        self.schema_dependencies[schema_name] = dependencies

    def validate_schema(self, schema_name: str, data: dict) -> bool:
        """Validate data against a schema's rules.

        Args:
            schema_name: Name of the schema to validate against
            data: Data to validate

        Returns:
            True if validation passes

        Raises:
            ValueError: If schema not found or validation fails
        """
        schema_class = self.factory.get_schema(schema_name)
        if not schema_class:
            raise ValueError(f"Schema {schema_name} not found")

        # First validate against the Pydantic model
        try:
            instance = schema_class(**data)
        except ValidationError as e:
            raise ValueError(f"Data validation failed: {str(e)}")

        # Then run custom validation rules
        rules = self.validation_rules.get(schema_name, [])
        for rule, error_message in rules:
            if not rule(instance):
                raise ValueError(error_message)

        # Validate dependencies if any
        dependencies = self.schema_dependencies.get(schema_name, [])
        for dep in dependencies:
            if not self.factory.get_schema(dep):
                raise ValueError(f"Required dependency schema {dep} not found")

        return True

    def create_schema_instance(self, schema_name: str, data: dict) -> T:
        """Create and validate a schema instance.

        Args:
            schema_name: Name of the schema to create
            data: Data to create the instance with

        Returns:
            Validated schema instance

        Raises:
            ValueError: If validation fails
        """
        if self.validate_schema(schema_name, data):
            schema_class = self.factory.get_schema(schema_name)
            return schema_class(**data)  # type: ignore
        raise ValueError("Schema validation failed")

    def get_schema_metadata(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a registered schema.

        Args:
            schema_name: Name of the schema

        Returns:
            Dictionary containing schema metadata or None if not found
        """
        schema_class = self.factory.get_schema(schema_name)
        if not schema_class:
            return None

        return {
            "version": self.schema_versions.get(schema_name, "1.0.0"),
            "description": getattr(schema_class, "__doc__", ""),
            "fields": schema_class.model_json_schema()["properties"],
            "dependencies": self.schema_dependencies.get(schema_name, []),
        }

    def list_registered_schemas(self) -> Dict[str, Dict[str, Any]]:
        """List all registered schemas with their metadata.

        Returns:
            Dictionary mapping schema names to their metadata
        """
        schemas = self.factory.list_schemas()
        return {
            name: {
                "class": schema_class,
                "version": self.schema_versions.get(name, "1.0.0"),
                "dependencies": self.schema_dependencies.get(name, []),
                "validation_rules": len(self.validation_rules.get(name, [])),
            }
            for name, schema_class in schemas.items()
        }


__all__ = ["SchemaRegistry"]
