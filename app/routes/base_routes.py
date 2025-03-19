from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import APIResponse
from app.database import get_db
from app.models.base_model import BaseModel
from app.services.base_service import BaseService
from app.schemas.base_schema import BaseSchema
from app.schemas.metrics_schema import RouteMetricsSchema
from app.utils.metrics import RouteMetrics

SchemaType = TypeVar("SchemaType", bound=BaseSchema)  # Schema must inherit from BaseSchema
ServiceType = TypeVar("ServiceType", bound=BaseService)  # Service must inherit from BaseService
ModelType = TypeVar("ModelType", bound=BaseModel)  # Model must inherit from BaseModel


class BaseRouter(Generic[SchemaType, ServiceType, ModelType]):
    """Base router with improved type safety and metrics."""

    def __init__(
        self,
        prefix: str,
        tags: List[str],
        schema_class: Type[SchemaType],
        service_class: Type[ServiceType],
        model_class: Type[ModelType],
        metrics: Optional[RouteMetricsSchema] = None,
    ):
        """Initialize the router with required components.
        
        Args:
            prefix: URL prefix for all routes
            tags: OpenAPI tags for documentation
            schema_class: Pydantic schema class for request/response
            service_class: Service class for business logic
            model_class: SQLAlchemy model class
            metrics: Optional metrics configuration
        """
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.schema_class = schema_class
        self.service_class = service_class
        self.model_class = model_class
        self.metrics = metrics or RouteMetrics()
        self._register_default_routes()

    def _register_default_routes(self):
        """Register default CRUD routes."""

        @self.router.get("/", response_model=APIResponse[List[SchemaType]])
        async def get_all(
            skip: int = 0,
            limit: int = 100,
            filters: Optional[Dict[str, Any]] = None,
            db: AsyncSession = Depends(get_db),
        ):
            """Get all items with pagination and filtering."""
            service = self.service_class(db, model=self.model_class)
            items = await service.get_all(skip=skip, limit=limit, filters=filters)
            return APIResponse(data=items, message="Items retrieved successfully")

        @self.router.get("/{id}", response_model=APIResponse[SchemaType])
        async def get_by_id(id: Any, db: AsyncSession = Depends(get_db)):
            """Get a single item by ID."""
            service = self.service_class(db, model=self.model_class)
            item = await service.get_by_id(id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return APIResponse(data=item, message="Item retrieved successfully")

        @self.router.post("/", response_model=APIResponse[SchemaType])
        async def create(data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
            """Create a new item."""
            service = self.service_class(db, model=self.model_class)
            item = await service.create(data)
            return APIResponse(data=item, message="Item created successfully")

        @self.router.put("/{id}", response_model=APIResponse[SchemaType])
        async def update(id: Any, data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
            """Update an existing item."""
            service = self.service_class(db, model=self.model_class)
            item = await service.update(id, data)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return APIResponse(data=item, message="Item updated successfully")

        @self.router.delete("/{id}", response_model=APIResponse[SchemaType])
        async def delete(id: Any, db: AsyncSession = Depends(get_db)):
            """Delete an item."""
            service = self.service_class(db, model=self.model_class)
            success = await service.delete(id)
            if not success:
                raise HTTPException(status_code=404, detail="Item not found")
            return APIResponse(data=None, message="Item deleted successfully")
