"""
Test suite for the neurodiverse-optimized UI accessibility module.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import asyncio

from app.ui.accessibility import (
    AccessibilityService,
    AccessibilityPreferences,
    ColorTheme,
    FontStyle,
    AnimationLevel,
    NotificationStyle,
    FocusAssistLevel,
    LayoutDensity,
    WCAGComplianceLevel,
    WCAGGuideline,
)


class TestAccessibilityPreferences:
    """Test the AccessibilityPreferences model."""
    
    def test_default_preferences(self):
        """Test that default preferences are set correctly."""
        prefs = AccessibilityPreferences(user_id="test_user")
        
        assert prefs.user_id == "test_user"
        assert prefs.color_theme == ColorTheme.STANDARD
        assert prefs.font_style == FontStyle.STANDARD
        assert prefs.font_size == 16
        assert prefs.line_spacing == 1.5
        assert prefs.animation_level == AnimationLevel.REDUCED
        assert prefs.notification_style == NotificationStyle.STANDARD
        assert prefs.focus_assist_level == FocusAssistLevel.MEDIUM
        assert prefs.layout_density == LayoutDensity.STANDARD
        assert prefs.reduced_motion is False
        assert prefs.high_contrast is False
        assert prefs.text_to_speech is False
        assert prefs.keyboard_shortcuts_enabled is True
        assert prefs.tooltip_delay == 500
        assert prefs.use_visual_cues is True
        assert prefs.use_audio_cues is True
        assert prefs.simplify_ui is False
        assert prefs.distraction_reduction is True
        assert prefs.color_overlay is None
        assert prefs.custom_css is None
        
    def test_custom_preferences(self):
        """Test that custom preferences can be set."""
        prefs = AccessibilityPreferences(
            user_id="test_user",
            color_theme=ColorTheme.DARK,
            font_style=FontStyle.DYSLEXIC_FRIENDLY,
            font_size=20,
            line_spacing=2.0,
            animation_level=AnimationLevel.NONE,
            reduced_motion=True,
            high_contrast=True,
            custom_css="body { font-family: 'Comic Sans MS'; }"
        )
        
        assert prefs.user_id == "test_user"
        assert prefs.color_theme == ColorTheme.DARK
        assert prefs.font_style == FontStyle.DYSLEXIC_FRIENDLY
        assert prefs.font_size == 20
        assert prefs.line_spacing == 2.0
        assert prefs.animation_level == AnimationLevel.NONE
        assert prefs.reduced_motion is True
        assert prefs.high_contrast is True
        assert prefs.custom_css == "body { font-family: 'Comic Sans MS'; }"


class TestAccessibilityService:
    """Test the AccessibilityService class."""
    
    @pytest.fixture
    def service(self):
        """Create an AccessibilityService instance for testing."""
        return AccessibilityService()
    
    def test_init(self, service):
        """Test that the service initializes correctly."""
        assert service.default_preferences.user_id == "default"
        assert len(service.user_preferences) == 0
        assert len(service.wcag_guidelines) > 0
    
    @pytest.mark.asyncio
    async def test_get_user_preferences_new_user(self, service):
        """Test getting preferences for a new user."""
        prefs = await service.get_user_preferences("new_user")
        
        assert prefs.user_id == "new_user"
        assert prefs in service.user_preferences.values()
        assert service.user_preferences["new_user"] == prefs
    
    @pytest.mark.asyncio
    async def test_get_user_preferences_existing_user(self, service):
        """Test getting preferences for an existing user."""
        # Create preferences for user
        existing_prefs = AccessibilityPreferences(
            user_id="existing_user",
            color_theme=ColorTheme.DARK
        )
        service.user_preferences["existing_user"] = existing_prefs
        
        # Get preferences
        prefs = await service.get_user_preferences("existing_user")
        
        assert prefs == existing_prefs
        assert prefs.color_theme == ColorTheme.DARK
    
    @pytest.mark.asyncio
    async def test_update_user_preferences(self, service):
        """Test updating user preferences."""
        # Get default preferences for user
        original_prefs = await service.get_user_preferences("update_user")
        assert original_prefs.color_theme == ColorTheme.STANDARD
        
        # Store the original timestamp
        original_timestamp = original_prefs.last_updated
        
        # Add a small delay to ensure timestamps differ
        await asyncio.sleep(0.001)  # 1 millisecond delay
        
        # Update preferences
        updated_prefs = await service.update_user_preferences("update_user", {
            "color_theme": ColorTheme.DARK,
            "font_size": 24,
            "reduced_motion": True
        })
        
        assert updated_prefs.color_theme == ColorTheme.DARK
        assert updated_prefs.font_size == 24
        assert updated_prefs.reduced_motion is True
        assert updated_prefs.font_style == FontStyle.STANDARD  # Unchanged
        
        # Ensure last_updated was updated
        assert updated_prefs.last_updated > original_timestamp
    
    @pytest.mark.asyncio
    async def test_get_theme_css(self, service):
        """Test CSS variable generation based on user preferences."""
        # Create preferences
        service.user_preferences["theme_user"] = AccessibilityPreferences(
            user_id="theme_user",
            color_theme=ColorTheme.DARK,
            font_style=FontStyle.COMIC_SANS,
            font_size=20,
            layout_density=LayoutDensity.SPACIOUS
        )
        
        # Get CSS
        css_vars = await service.get_theme_css("theme_user")
        
        # Check dark theme colors
        assert css_vars["--background-color"] == "#121212"
        assert css_vars["--text-color"] == "#e0e0e0"
        assert css_vars["--primary-color"] == "#bb86fc"
        
        # Check font settings
        assert css_vars["--font-family"] == '"Comic Sans MS", cursive, sans-serif'
        assert css_vars["--base-font-size"] == "20px"
        
        # Check spacing for spacious layout
        assert css_vars["--spacing-unit"] == "1.5rem"
    
    @pytest.mark.asyncio
    async def test_get_wcag_compliance_report(self, service):
        """Test WCAG compliance report generation."""
        report = await service.get_wcag_compliance_report()
        
        assert "total_guidelines" in report
        assert "implemented_guidelines" in report
        assert "compliance_percentage" in report
        assert "compliance_by_level" in report
        assert "guidelines" in report
        assert "overall_compliance_level" in report
        
        # Check level-specific stats are present
        assert "a" in report["compliance_by_level"]
        assert "aa" in report["compliance_by_level"]
        assert "aaa" in report["compliance_by_level"]
        
        # Check guidelines are included
        assert len(report["guidelines"]) > 0
        
        # Check a specific guideline structure
        guideline = report["guidelines"][0]
        assert "id" in guideline
        assert "name" in guideline
        assert "description" in guideline
        assert "level" in guideline
        assert "impact_for_adhd" in guideline
        assert "implementation_status" in guideline
    
    def test_generate_focus_assist_styles(self, service):
        """Test focus assist style generation for different levels."""
        # Test OFF level
        off_styles = service.generate_focus_assist_styles(FocusAssistLevel.OFF)
        assert len(off_styles) == 0
        
        # Test LOW level
        low_styles = service.generate_focus_assist_styles(FocusAssistLevel.LOW)
        assert "focus-outline" in low_styles
        assert "dim-background" in low_styles
        assert low_styles["dim-background"] == "rgba(0, 0, 0, 0.1)"
        
        # Test MEDIUM level
        medium_styles = service.generate_focus_assist_styles(FocusAssistLevel.MEDIUM)
        assert "zoom-factor" in medium_styles
        assert medium_styles["dim-background"] == "rgba(0, 0, 0, 0.3)"
        
        # Test HIGH level
        high_styles = service.generate_focus_assist_styles(FocusAssistLevel.HIGH)
        assert "reduce-periphery" in high_styles
        assert medium_styles["zoom-factor"] < high_styles["zoom-factor"]
        
        # Test MAXIMUM level
        max_styles = service.generate_focus_assist_styles(FocusAssistLevel.MAXIMUM)
        assert "hide-non-essential" in max_styles
        assert max_styles["dim-background"] == "rgba(0, 0, 0, 0.7)"
    
    @pytest.mark.asyncio
    async def test_generate_adhd_optimized_ui_settings_base(self, service):
        """Test UI settings generation with default context."""
        # Create preferences
        service.user_preferences["ui_user"] = AccessibilityPreferences(
            user_id="ui_user",
            color_theme=ColorTheme.STANDARD,
            notification_style=NotificationStyle.PERSISTENT,
            focus_assist_level=FocusAssistLevel.MEDIUM
        )
        
        # Get UI settings with no context
        settings = await service.generate_adhd_optimized_ui_settings("ui_user")
        
        assert "css_variables" in settings
        assert "focus_styles" in settings
        assert "notifications" in settings
        assert "interactions" in settings
        
        # Check notification duration is longer for persistent style
        assert settings["notifications"]["duration"] == 5000
        assert settings["notifications"]["style"] == "persistent"
        
        # Check focus styles
        assert "zoom-factor" in settings["focus_styles"]
        
        # Check interactions
        assert settings["interactions"]["tooltip_delay"] == 500
    
    @pytest.mark.asyncio
    async def test_generate_adhd_optimized_ui_settings_with_context(self, service):
        """Test UI settings generation with specific context variables."""
        # Create preferences
        service.user_preferences["context_user"] = AccessibilityPreferences(
            user_id="context_user"
        )
        
        # Get UI settings with night time context
        night_settings = await service.generate_adhd_optimized_ui_settings(
            "context_user", 
            {"current_hour": 22}  # 10pm
        )
        
        # Should have blue light filter at night
        assert night_settings["css_variables"]["--blue-light-filter"] == "0.7"
        
        # Get UI settings with low energy
        low_energy_settings = await service.generate_adhd_optimized_ui_settings(
            "context_user", 
            {"energy_level": 0.2}
        )
        
        # Should have contrast enhancement for low energy
        assert "--contrast-enhancement" in low_energy_settings["css_variables"]
        
        # Get UI settings with high importance task
        high_importance_settings = await service.generate_adhd_optimized_ui_settings(
            "context_user", 
            {"task_importance": 0.8}
        )
        
        # Should have higher focus assistance for important tasks
        assert "reduce-periphery" in high_importance_settings["focus_styles"] 