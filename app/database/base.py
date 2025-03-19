"""Import all models here to ensure they are registered before relationships are established.

This module imports all SQLAlchemy models in the correct order to ensure that all table
definitions are complete before relationships between tables are established.
This prevents "table not found" errors when SQLAlchemy tries to create foreign key
references during model initialization.
"""

# Import base model class first
from app.models.base_model import BaseModel
from app.database.base_class import Base  # Base is now BaseModel

# Import models in dependency order - user model should come first since many models depend on it
from app.models.user_model import UserModel
from app.models.contact_model import ContactModel  # Add contact model before models that depend on it
from app.models.calendar_model import CalendarModel
from app.models.calendar_event_model import CalendarEventModel
from app.models.calendar_sync_model import CalendarSyncModel
from app.models.task_category_model import TaskCategoryModel
from app.models.task_model import TaskModel
from app.models.session_model import SessionModel  # Add session model before scheduling model
from app.models.scheduling_model import Interruption, Break, WorkHours, ScheduleBlock, SchedulePreferences, EnergyPattern  # Add scheduling models
from app.models.reminder_model import ReminderModel  # Add reminder model after models it depends on
from app.models.interaction_model import Interaction, InteractionStats  # Add interaction model which depends on session model
# Import other models that depend on user model
# Add more imports as needed