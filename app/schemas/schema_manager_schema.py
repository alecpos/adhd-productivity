from typing import Dict, Any, Type, Optional, Callable
from pydantic import Field, ConfigDict

from app.schemas.base_schema import BaseSchema, TimestampedSchema
from app.schemas.schema_registry_schema import SchemaRegistry
from app.schemas.schema_factory_schema import SchemaFactory
from app.schemas.schema_validation_schema import RequiredFieldRule, ValidationRule


class NoneSchema(BaseSchema):
    """Schema for None type returns."""
    pass


class DictSchema(BaseSchema):
    """Schema for dictionary returns."""
    data: Dict[str, Any] = Field(default_factory=dict)


class SchemaManagerSchema(BaseSchema):
    """Manager for handling schema operations and migrations."""
    registry: SchemaRegistry = Field(default_factory=SchemaRegistry)
    factory: SchemaFactory = Field(default_factory=SchemaFactory)
    migrations: Dict[str, Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]]] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def register_migration(
        self,
        schema_name: str,
        from_version: str,
        to_version: str,
        migration_func: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> None:
        """Register a migration function for a schema version upgrade."""
        if schema_name not in self.migrations:
            self.migrations[schema_name] = {}

        migration_key = f"{from_version}->{to_version}"
        self.migrations[schema_name][migration_key] = migration_func

    def migrate_schema(
        self, schema_name: str, data: dict, from_version: str, to_version: str
    ) -> DictSchema:
        """Migrate schema data from one version to another."""
        if schema_name not in self.migrations:
            raise ValueError(f"No migrations registered for schema {schema_name}")

        migration_key = f"{from_version}->{to_version}"
        if migration_key not in self.migrations[schema_name]:
            raise ValueError(f"No migration path from {from_version} to {to_version}")

        migration_func = self.migrations[schema_name][migration_key]
        migrated_data = migration_func(data)
        return DictSchema(data=migrated_data)

    def create_schema_version(
        self, name: str, fields: Dict[str, Any], version: str = "1.0.0"
    ) -> Type[BaseSchema]:
        """Create a new version of a schema."""
        schema_class = self.factory.create_schema(name, fields, base_class=TimestampedSchema)

        # Set version metadata
        setattr(schema_class, "_schema_version", version)
        return schema_class

    def validate_and_migrate(
        self, schema_name: str, data: dict, target_version: Optional[str] = None
    ) -> DictSchema:
        """Validate data and migrate to target version if needed."""
        current_schema = self.factory.get_schema(schema_name)
        if not current_schema:
            raise ValueError(f"Schema {schema_name} not found")

        # Get current version from data or assume latest
        current_version = data.get("_version", current_schema._schema_version)
        target_version = target_version or current_schema._schema_version

        # Migrate if versions differ
        if current_version != target_version:
            data = self.migrate_schema(schema_name, data, current_version, target_version)

        # Validate against current schema
        if not self.registry.validate_schema(schema_name, data):
            raise ValueError("Schema validation failed after migration")
        
        return DictSchema(data=data)

    def get_schema_versions(self, schema_name: str) -> Dict[str, Type[BaseSchema]]:
        """Get all versions of a schema."""
        schemas = self.factory.list_schemas()
        return {
            getattr(schema, "_schema_version", "1.0.0"): schema
            for schema in schemas.values()
            if schema.__name__.startswith(schema_name)
        }
