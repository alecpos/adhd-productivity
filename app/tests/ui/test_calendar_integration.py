"""
Test suite for the calendar integration module.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from app.ui.calendar_integration import (
    CalendarPlatform,
    EventType,
    CalendarPermission,
    CalendarIntegrationConfig,
    ExternalEvent,
    CalendarSyncResult,
    CalendarIntegration,
    GoogleCalendarIntegration,
    CalendarIntegrationService,
)


class TestCalendarIntegrationConfig:
    """Test the CalendarIntegrationConfig model."""
    
    def test_default_config(self):
        """Test that default configuration values are set correctly."""
        config = CalendarIntegrationConfig(
            user_id="test_user",
            platform=CalendarPlatform.GOOGLE,
            calendar_id="primary",
            display_name="My Calendar"
        )
        
        assert config.user_id == "test_user"
        assert config.platform == CalendarPlatform.GOOGLE
        assert config.calendar_id == "primary"
        assert config.display_name == "My Calendar"
        assert config.color is None
        assert config.auth_token is None
        assert config.auth_refresh_token is None
        assert config.auth_expiry is None
        assert config.sync_enabled is True
        assert config.sync_frequency_minutes == 30
        assert config.last_sync is None
        assert config.sync_events_days_back == 30
        assert config.sync_events_days_forward == 90
        assert len(config.event_types_to_sync) > 0  # Should contain all EventType values
        assert config.custom_sync_settings == {}
    
    def test_custom_config(self):
        """Test that custom configuration can be set."""
        config = CalendarIntegrationConfig(
            user_id="test_user",
            platform=CalendarPlatform.OUTLOOK,
            calendar_id="work@example.com",
            display_name="Work Calendar",
            color="#FF0000",
            auth_token="outlook_token",
            sync_frequency_minutes=60,
            sync_events_days_back=7,
            event_types_to_sync={EventType.MEETING, EventType.APPOINTMENT},
            custom_sync_settings={"include_declined": False}
        )
        
        assert config.platform == CalendarPlatform.OUTLOOK
        assert config.calendar_id == "work@example.com"
        assert config.display_name == "Work Calendar"
        assert config.color == "#FF0000"
        assert config.auth_token == "outlook_token"
        assert config.sync_frequency_minutes == 60
        assert config.sync_events_days_back == 7
        assert EventType.MEETING in config.event_types_to_sync
        assert EventType.APPOINTMENT in config.event_types_to_sync
        assert EventType.TASK not in config.event_types_to_sync
        assert config.custom_sync_settings == {"include_declined": False}


class TestExternalEvent:
    """Test the ExternalEvent model."""
    
    def test_minimal_event(self):
        """Test creation of a minimal external event."""
        now = datetime.now()
        event = ExternalEvent(
            event_id="event123",
            calendar_id="primary",
            title="Test Event",
            start_time=now,
            end_time=now + timedelta(hours=1),
            platform=CalendarPlatform.GOOGLE
        )
        
        assert event.event_id == "event123"
        assert event.calendar_id == "primary"
        assert event.title == "Test Event"
        assert event.start_time == now
        assert event.end_time == now + timedelta(hours=1)
        assert event.is_all_day is False
        assert event.location is None
        assert event.url is None
        assert event.event_type == EventType.APPOINTMENT  # Default
        assert event.recurrence_rule is None
        assert event.attendees == []
        assert event.reminders == []
        assert event.transparency is False
        assert event.platform == CalendarPlatform.GOOGLE
        assert event.additional_data == {}
    
    def test_complete_event(self):
        """Test creation of a fully populated external event."""
        now = datetime.now()
        event = ExternalEvent(
            event_id="event456",
            calendar_id="primary",
            title="Comprehensive Event",
            description="This is a detailed event for testing",
            start_time=now,
            end_time=now + timedelta(hours=2),
            is_all_day=False,
            location="Conference Room",
            url="https://meet.google.com/abc-def-ghi",
            event_type=EventType.MEETING,
            recurrence_rule="RRULE:FREQ=WEEKLY;BYDAY=MO",
            attendees=[
                {"email": "user1@example.com", "name": "User One"},
                {"email": "user2@example.com", "name": "User Two"},
            ],
            reminders=[
                {"method": "popup", "minutes_before": 10},
                {"method": "email", "minutes_before": 60},
            ],
            color="#4285F4",
            transparency=True,  # Free
            organizer={"email": "organizer@example.com", "name": "Organizer"},
            created=now - timedelta(days=1),
            updated=now - timedelta(hours=1),
            platform=CalendarPlatform.GOOGLE,
            additional_data={"conference_solution": "Google Meet"}
        )
        
        assert event.event_id == "event456"
        assert event.title == "Comprehensive Event"
        assert event.description == "This is a detailed event for testing"
        assert event.location == "Conference Room"
        assert event.url == "https://meet.google.com/abc-def-ghi"
        assert event.event_type == EventType.MEETING
        assert event.recurrence_rule == "RRULE:FREQ=WEEKLY;BYDAY=MO"
        assert len(event.attendees) == 2
        assert len(event.reminders) == 2
        assert event.color == "#4285F4"
        assert event.transparency is True
        assert event.organizer["email"] == "organizer@example.com"
        assert event.created == now - timedelta(days=1)
        assert event.updated == now - timedelta(hours=1)
        assert event.additional_data["conference_solution"] == "Google Meet"


class TestGoogleCalendarIntegration:
    """Test the GoogleCalendarIntegration class."""
    
    @pytest.fixture
    def google_config(self):
        """Create a Google Calendar configuration for testing."""
        return CalendarIntegrationConfig(
            user_id="test_user",
            platform=CalendarPlatform.GOOGLE,
            calendar_id="primary",
            display_name="My Calendar",
            auth_token="test_token"
        )
    
    @pytest.fixture
    def google_integration(self, google_config):
        """Create a GoogleCalendarIntegration instance for testing."""
        return GoogleCalendarIntegration(google_config)
    
    def test_init(self, google_integration, google_config):
        """Test that the integration initializes correctly."""
        assert google_integration.config == google_config
        assert google_integration.name == "Google"
    
    @pytest.mark.asyncio
    @patch("app.ui.calendar_integration.logger")
    async def test_authenticate_success(self, mock_logger, google_integration):
        """Test successful authentication."""
        result = await google_integration.authenticate()
        
        assert result is True
        mock_logger.info.assert_called_once()
    
    @pytest.mark.asyncio
    @patch.object(GoogleCalendarIntegration, '_refresh_token')
    async def test_authenticate_refresh_token(self, mock_refresh_token, google_integration):
        """Test authentication with token refresh."""
        # Set expired token
        google_integration.config.auth_expiry = datetime.utcnow() - timedelta(hours=1)
        
        result = await google_integration.authenticate()
        
        assert result is True
        mock_refresh_token.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_sync_time_range(self, google_integration):
        """Test getting time range for sync."""
        start_date, end_date = await google_integration.get_sync_time_range()
        
        # Start date should be in the past
        assert start_date < datetime.utcnow()
        # End date should be in the future
        assert end_date > datetime.utcnow()
        # The difference should match configuration
        assert (end_date - start_date).days == (
            google_integration.config.sync_events_days_back + 
            google_integration.config.sync_events_days_forward
        )
    
    @pytest.mark.asyncio
    async def test_fetch_events(self, google_integration):
        """Test fetching events from Google Calendar."""
        now = datetime.utcnow()
        events = await google_integration.fetch_events(
            now - timedelta(days=7), now + timedelta(days=7)
        )
        
        assert len(events) > 0
        assert isinstance(events[0], ExternalEvent)
        assert events[0].platform == CalendarPlatform.GOOGLE
        assert events[0].title == "Team Meeting"
    
    @pytest.mark.asyncio
    async def test_create_event(self, google_integration):
        """Test creating an event in Google Calendar."""
        now = datetime.utcnow()
        event_data = {
            "title": "New Event",
            "description": "Event description",
            "start_time": now,
            "end_time": now + timedelta(hours=1),
            "location": "Conference Room",
            "attendees": [
                {"email": "attendee@example.com", "name": "Attendee"}
            ],
            "reminders": [
                {"method": "popup", "minutes_before": 15}
            ]
        }
        
        created_event = await google_integration.create_event(event_data)
        
        assert isinstance(created_event, ExternalEvent)
        assert created_event.title == "New Event"
        assert created_event.description == "Event description"
        assert created_event.location == "Conference Room"
        assert len(created_event.attendees) == 1
        assert len(created_event.reminders) == 1
        assert created_event.platform == CalendarPlatform.GOOGLE
    
    @pytest.mark.asyncio
    async def test_update_event(self, google_integration):
        """Test updating an event in Google Calendar."""
        event_data = {
            "title": "Updated Event",
            "start_time": datetime.utcnow(),
            "end_time": datetime.utcnow() + timedelta(hours=2)
        }
        
        updated_event = await google_integration.update_event("event123", event_data)
        
        assert isinstance(updated_event, ExternalEvent)
        assert updated_event.title == "Updated Event"
        assert updated_event.event_id == "event123"
    
    @pytest.mark.asyncio
    async def test_delete_event(self, google_integration):
        """Test deleting an event from Google Calendar."""
        result = await google_integration.delete_event("event123")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_calendars(self, google_integration):
        """Test getting calendars from Google Calendar."""
        calendars = await google_integration.get_calendars()
        
        assert len(calendars) > 0
        assert "id" in calendars[0]
        assert "summary" in calendars[0]
        assert "backgroundColor" in calendars[0]


class TestCalendarIntegrationService:
    """Test the CalendarIntegrationService class."""
    
    @pytest.fixture
    def service(self):
        """Create a CalendarIntegrationService instance for testing."""
        return CalendarIntegrationService()
    
    def test_init(self, service):
        """Test that the service initializes correctly."""
        assert service.integrations == {}
        assert CalendarPlatform.GOOGLE in service.integration_classes
    
    @pytest.mark.asyncio
    @patch.object(GoogleCalendarIntegration, 'test_connection', new_callable=AsyncMock, return_value=True)
    async def test_register_integration_success(self, mock_test_connection, service):
        """Test successful integration registration."""
        config = CalendarIntegrationConfig(
            user_id="test_user",
            platform=CalendarPlatform.GOOGLE,
            calendar_id="primary",
            display_name="My Calendar"
        )
        
        result = await service.register_integration(config)
        
        assert result is True
        assert "test_user" in service.integrations
        assert "google:primary" in service.integrations["test_user"]
        assert isinstance(
            service.integrations["test_user"]["google:primary"], 
            GoogleCalendarIntegration
        )
    
    @pytest.mark.asyncio
    @patch.object(GoogleCalendarIntegration, 'test_connection', new_callable=AsyncMock, return_value=False)
    async def test_register_integration_connection_failure(self, mock_test_connection, service):
        """Test integration registration with connection failure."""
        config = CalendarIntegrationConfig(
            user_id="test_user",
            platform=CalendarPlatform.GOOGLE,
            calendar_id="primary",
            display_name="My Calendar"
        )
        
        result = await service.register_integration(config)
        
        assert result is False
        assert "test_user" not in service.integrations
    
    @pytest.mark.asyncio
    async def test_register_integration_unsupported_platform(self, service):
        """Test integration registration with unsupported platform."""
        # Temporarily remove GOOGLE from supported integrations
        original_classes = service.integration_classes
        service.integration_classes = {}
        
        config = CalendarIntegrationConfig(
            user_id="test_user",
            platform=CalendarPlatform.GOOGLE,
            calendar_id="primary",
            display_name="My Calendar"
        )
        
        result = await service.register_integration(config)
        
        assert result is False
        
        # Restore original classes
        service.integration_classes = original_classes
    
    @pytest.mark.asyncio
    @patch.object(GoogleCalendarIntegration, 'test_connection', new_callable=AsyncMock, return_value=True)
    async def test_get_user_integrations(self, mock_test_connection, service):
        """Test getting integrations for a user."""
        # Register an integration
        config = CalendarIntegrationConfig(
            user_id="test_user",
            platform=CalendarPlatform.GOOGLE,
            calendar_id="primary",
            display_name="My Calendar"
        )
        await service.register_integration(config)
        
        # Get user integrations
        integrations = await service.get_user_integrations("test_user")
        
        assert len(integrations) == 1
        assert integrations[0]["platform"] == "google"
        assert integrations[0]["calendar_id"] == "primary"
        assert integrations[0]["display_name"] == "My Calendar"
        
        # Test with non-existent user
        empty_integrations = await service.get_user_integrations("nonexistent_user")
        assert empty_integrations == []
    
    @pytest.mark.asyncio
    @patch.object(GoogleCalendarIntegration, 'test_connection', new_callable=AsyncMock, return_value=True)
    async def test_remove_integration(self, mock_test_connection, service):
        """Test removing an integration for a user."""
        # Register an integration
        config = CalendarIntegrationConfig(
            user_id="test_user",
            platform=CalendarPlatform.GOOGLE,
            calendar_id="primary",
            display_name="My Calendar"
        )
        await service.register_integration(config)
        
        # Remove integration
        result = await service.remove_integration(
            "test_user", "primary", CalendarPlatform.GOOGLE
        )
        
        assert result is True
        assert "test_user" not in service.integrations
        
        # Test with non-existent integration
        false_result = await service.remove_integration(
            "test_user", "primary", CalendarPlatform.GOOGLE
        )
        assert false_result is False
    
    @pytest.mark.asyncio
    @patch.object(GoogleCalendarIntegration, 'test_connection', new_callable=AsyncMock, return_value=True)
    @patch.object(GoogleCalendarIntegration, 'fetch_events', new_callable=AsyncMock, return_value=[
        ExternalEvent(
            event_id="event123",
            calendar_id="primary",
            title="Test Event",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            platform=CalendarPlatform.GOOGLE
        )
    ])
    async def test_sync_calendars(self, mock_fetch_events, mock_test_connection, service):
        """Test synchronizing calendars for a user."""
        # Register an integration
        config = CalendarIntegrationConfig(
            user_id="test_user",
            platform=CalendarPlatform.GOOGLE,
            calendar_id="primary",
            display_name="My Calendar"
        )
        await service.register_integration(config)
        
        # Sync calendars
        results = await service.sync_calendars("test_user")
        
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].platform == CalendarPlatform.GOOGLE
        assert results[0].calendar_id == "primary"
        assert results[0].events_imported == 1
        
        # Test with specific platform and calendar_id
        specific_results = await service.sync_calendars(
            "test_user", CalendarPlatform.GOOGLE, "primary"
        )
        assert len(specific_results) == 1
        
        # Test with non-existent user
        empty_results = await service.sync_calendars("nonexistent_user")
        assert empty_results == []
    
    @pytest.mark.asyncio
    @patch.object(GoogleCalendarIntegration, 'get_calendars', new_callable=AsyncMock, return_value=[
        {"id": "primary", "summary": "My Calendar", "backgroundColor": "#4285F4"}
    ])
    @patch.object(GoogleCalendarIntegration, 'test_connection', new_callable=AsyncMock, return_value=True)
    async def test_get_available_calendars(self, mock_test_connection, mock_get_calendars, service):
        """Test getting available calendars for a platform."""
        # Register an integration
        config = CalendarIntegrationConfig(
            user_id="test_user",
            platform=CalendarPlatform.GOOGLE,
            calendar_id="primary",
            display_name="My Calendar"
        )
        await service.register_integration(config)
        
        # Get calendars
        calendars = await service.get_available_calendars("test_user", CalendarPlatform.GOOGLE)
        
        assert len(calendars) == 1
        assert calendars[0]["id"] == "primary"
        assert calendars[0]["summary"] == "My Calendar"
        
        # Test with non-existent platform
        empty_calendars = await service.get_available_calendars("test_user", CalendarPlatform.OUTLOOK)
        assert empty_calendars == []
    
    @pytest.mark.asyncio
    @patch.object(GoogleCalendarIntegration, 'create_event', new_callable=AsyncMock)
    @patch.object(GoogleCalendarIntegration, 'test_connection', new_callable=AsyncMock, return_value=True)
    async def test_create_event_in_external_calendar(self, mock_test_connection, mock_create_event, service):
        """Test creating an event in an external calendar."""
        # Set up mock return value
        event = ExternalEvent(
            event_id="event123",
            calendar_id="primary",
            title="New Event",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            platform=CalendarPlatform.GOOGLE
        )
        mock_create_event.return_value = event
        
        # Register an integration
        config = CalendarIntegrationConfig(
            user_id="test_user",
            platform=CalendarPlatform.GOOGLE,
            calendar_id="primary",
            display_name="My Calendar"
        )
        await service.register_integration(config)
        
        # Create event
        event_data = {"title": "New Event"}
        created_event = await service.create_event_in_external_calendar(
            "test_user", CalendarPlatform.GOOGLE, "primary", event_data
        )
        
        assert created_event is not None
        assert created_event.title == "New Event"
        assert created_event.event_id == "event123"
        mock_create_event.assert_called_once_with(event_data)
    
    @pytest.mark.asyncio
    @patch.object(GoogleCalendarIntegration, 'delete_event', new_callable=AsyncMock, return_value=True)
    @patch.object(GoogleCalendarIntegration, 'test_connection', new_callable=AsyncMock, return_value=True)
    async def test_delete_event_in_external_calendar(self, mock_test_connection, mock_delete_event, service):
        """Test deleting an event from an external calendar."""
        # Register an integration
        config = CalendarIntegrationConfig(
            user_id="test_user",
            platform=CalendarPlatform.GOOGLE,
            calendar_id="primary",
            display_name="My Calendar"
        )
        await service.register_integration(config)
        
        # Delete event
        result = await service.delete_event_in_external_calendar(
            "test_user", CalendarPlatform.GOOGLE, "primary", "event123"
        )
        
        assert result is True
        mock_delete_event.assert_called_once_with("event123") 