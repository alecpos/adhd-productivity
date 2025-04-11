"""
API endpoints for project management tool integration.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional, Any

from app.api.deps import get_current_user
from app.models.user_model import UserModel
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional, Union


class ProjectToolType(str, Enum):
    JIRA = "jira"
    TRELLO = "trello"
    ASANA = "asana"
    GITHUB = "github"
    GITLAB = "gitlab"
    NOTION = "notion"
    CLICKUP = "clickup"
    MONDAY = "monday"
    OTHER = "other"


class SyncDirection(str, Enum):
    IMPORT = "import"
    EXPORT = "export"
    BIDIRECTIONAL = "bidirectional"


class SyncFrequency(str, Enum):
    MANUAL = "manual"
    HOURLY = "hourly"
    DAILY = "daily"
    REALTIME = "realtime"


class ProjectToolConfig(BaseModel):
    user_id: str
    tool_type: ProjectToolType
    enabled: bool = True
    sync_direction: SyncDirection = SyncDirection.IMPORT
    sync_frequency: SyncFrequency = SyncFrequency.MANUAL


class SyncResult(BaseModel):
    tool_type: ProjectToolType
    tasks_synced: int
    success: bool
    timestamp: datetime
    error_message: Optional[str] = None


class ExternalTask(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    project_id: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    assignee: Optional[str] = None
    tool_type: ProjectToolType
    url: Optional[str] = None


class ProjectManagementService:
    async def get_user_integrations(self, user_id: str) -> List[ProjectToolConfig]:
        return [ProjectToolConfig(user_id=user_id, tool_type=ProjectToolType.JIRA)]

    async def register_integration(self, user_id: str, config: Dict[str, Any]) -> ProjectToolConfig:
        return ProjectToolConfig(user_id=user_id, tool_type=ProjectToolType.JIRA)

    async def remove_integration(self, user_id: str, tool_type: ProjectToolType) -> bool:
        return True

    async def sync_tasks(
        self, user_id: str, tool_types: Optional[List[ProjectToolType]] = None
    ) -> Dict[ProjectToolType, int]:
        return {ProjectToolType.JIRA: 5}

    async def get_sync_status(self, user_id: str) -> Dict[str, Any]:
        return {"last_sync": datetime.now().isoformat(), "status": "completed"}

    async def get_available_projects(
        self, user_id: str, tool_type: ProjectToolType
    ) -> List[Dict[str, Any]]:
        return [{"id": "PROJ-1", "name": "Sample Project"}]

    async def create_task(
        self, user_id: str, tool_type: ProjectToolType, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"id": "TASK-123", "title": task_data.get("title", "New Task")}

    async def update_task(
        self, user_id: str, tool_type: ProjectToolType, task_id: str, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"id": task_id, "title": task_data.get("title", "Updated Task")}


router = APIRouter(prefix="/project-management", tags=["Project Management", "Integration"])
project_management_service = ProjectManagementService()


@router.get("/integrations", response_model=List[ProjectToolType])
async def get_user_integrations(
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get all project management tool integrations for the current user.
    """
    return await project_management_service.get_user_integrations(current_user.id)


@router.post("/integrations", response_model=bool)
async def register_integration(
    config: ProjectToolConfig,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Register a new project management tool integration for the current user.
    """
    # Ensure user_id matches current user
    config.user_id = current_user.id
    return await project_management_service.register_integration(config)


@router.delete("/integrations/{tool_type}", response_model=bool)
async def remove_integration(
    tool_type: ProjectToolType,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Remove a project management tool integration for the current user.
    """
    return await project_management_service.remove_integration(current_user.id, tool_type)


@router.get("/sync", response_model=List[SyncResult])
async def sync_tasks(
    tool_type: Optional[ProjectToolType] = None,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Synchronize tasks between ADHD Calendar and external project management tools.
    If tool_type is provided, sync only that tool, otherwise sync all.
    """
    return await project_management_service.sync_tasks(current_user.id, tool_type)


@router.get("/sync/status", response_model=Dict[ProjectToolType, Dict[str, Any]])
async def get_sync_status(
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get synchronization status for all user integrations.
    """
    return await project_management_service.get_sync_status(current_user.id)


@router.get("/projects", response_model=List[Dict[str, Any]])
async def get_available_projects(
    tool_type: ProjectToolType,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get available projects from an external tool.
    """
    return await project_management_service.get_available_projects(current_user.id, tool_type)


@router.post("/tasks", response_model=ExternalTask)
async def create_task_in_external_tool(
    tool_type: ProjectToolType,
    task_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user),
):
    """
    Create a task directly in an external tool.
    """
    result = await project_management_service.create_task_in_external_tool(
        current_user.id, tool_type, task_data
    )

    if result is None:
        raise HTTPException(status_code=400, detail="Failed to create task")

    return result


@router.put("/tasks/{tool_type}/{external_id}", response_model=ExternalTask)
async def update_task_in_external_tool(
    tool_type: ProjectToolType,
    external_id: str,
    task_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user),
):
    """
    Update a task directly in an external tool.
    """
    result = await project_management_service.update_task_in_external_tool(
        current_user.id, tool_type, external_id, task_data
    )

    if result is None:
        raise HTTPException(status_code=400, detail="Failed to update task")

    return result
