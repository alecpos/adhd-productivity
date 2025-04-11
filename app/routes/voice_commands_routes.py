from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
import logging
from typing import Dict, Any
from app.database import get_db
from app.schemas.voice_command_schema import (
    VoiceCommandRequestSchema,
    VoiceCommandResponseSchema,
    VoiceCommandServiceSchema,
    TaskCreationCommandSchema,
    ReminderCreationCommandSchema,
)

logger = logging.getLogger(__name__)
voice_commands_router = APIRouter(prefix="/voice", tags=["Voice Commands"])


async def get_voice_command_service(
    db: AsyncSession = Depends(get_db),
) -> VoiceCommandServiceSchema:
    """Get an instance of the VoiceCommandServiceSchema."""
    return VoiceCommandServiceSchema(db)


@voice_commands_router.post(
    "/process",
    response_model=VoiceCommandResponseSchema,
    summary="Process Voice Command",
)
async def process_voice_command(
    command: VoiceCommandRequestSchema,
    service: VoiceCommandServiceSchema = Depends(get_voice_command_service),
) -> Dict[str, Any]:
    """Process a voice command and return the appropriate response."""
    logger.info(f"Processing voice command: {command.command_text}")
    try:
        parsed_command = await service.parse_command(command.command_text)
        if parsed_command.command_type == "create_task":
            task_data = TaskCreationCommandSchema(
                title=parsed_command.title,
                due_date=parsed_command.due_date,
                priority=parsed_command.priority,
            )
            result = await service.create_task(task_data)
        elif parsed_command.command_type == "create_reminder":
            reminder_data = ReminderCreationCommandSchema(
                title=parsed_command.title, reminder_time=parsed_command.reminder_time
            )
            result = await service.create_reminder(reminder_data)
        else:
            raise ValueError(f"Unknown command type: {parsed_command.command_type}")
        logger.info(f"Successfully processed voice command with result: {result}")
        return {
            "success": True,
            "message": "Command processed successfully",
            "data": result,
        }
    except ValueError as e:
        logger.error(f"Invalid command format: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing voice command: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing command: {str(e)}")


@voice_commands_router.post(
    "/create-task",
    response_model=VoiceCommandResponseSchema,
    summary="Create TaskModelSchema from Voice",
)
async def create_task_from_voice(
    command: TaskCreationCommandSchema,
    service: VoiceCommandServiceSchema = Depends(get_voice_command_service),
) -> Dict[str, Any]:
    """Create a task from voice command data."""
    logger.info(f"Creating task from voice command: {command.title}")
    try:
        result = await service.create_task(command)
        logger.info(f"Successfully created task: {result}")
        return {
            "success": True,
            "message": "TaskModelSchema created successfully",
            "data": result,
        }
    except Exception as e:
        logger.error(f"Error creating task from voice command: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")
