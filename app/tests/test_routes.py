import pytest
from fastapi import APIRouter
from app.routes.task_routes import task_router
from app.routes.user_routes import user_router
from app.routes import *  # Import all routers

# List of router instances to check
router_instances = [
    task_router,
    user_router,
    # Add other router instances here
]

@pytest.mark.parametrize("router_instance", router_instances)
def test_router_instance(router_instance):
    """Test if router instance is an instance of APIRouter."""
    assert isinstance(router_instance, APIRouter), f"{router_instance} is not an instance of APIRouter"
