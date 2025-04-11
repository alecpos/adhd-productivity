"""
Neurodiverse-Optimized UI Following WCAG 2.2 Guidelines (ADHD-27)

This module provides UI optimization components and settings specifically
designed for neurodiverse users, with a focus on ADHD-friendly interfaces.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AccessibilityLevel(str, Enum):
    """Different levels of accessibility features."""

    ESSENTIAL = "essential"  # Core accessibility features
    ENHANCED = "enhanced"  # More extensive accommodations
    MAXIMUM = "maximum"  # Maximum possible accommodations


class ColorTheme(str, Enum):
    """Color themes optimized for different needs."""

    STANDARD = "standard"
    HIGH_CONTRAST = "high_contrast"
    DARK = "dark"
    LIGHT = "light"
    REDUCED_BLUE = "reduced_blue"  # Reduces blue light
    CALM = "calm"  # Low-stimulation colors
    FOCUS = "focus"  # Colors that support focus
    CUSTOM = "custom"  # User-defined colors


class FontStyle(str, Enum):
    """Font styles optimized for readability."""

    STANDARD = "standard"
    DYSLEXIC_FRIENDLY = "dyslexic_friendly"
    LARGE_PRINT = "large_print"
    OPEN_DYSLEXIC = "open_dyslexic"
    COMIC_SANS = "comic_sans"  # Often preferred by some neurodiverse users
    CUSTOM = "custom"


class AnimationLevel(str, Enum):
    """Animation settings for UI elements."""

    FULL = "full"
    REDUCED = "reduced"
    MINIMAL = "minimal"
    NONE = "none"


class NotificationStyle(str, Enum):
    """Notification styles for ADHD users."""

    STANDARD = "standard"
    GENTLE = "gentle"  # Less intrusive
    PERSISTENT = "persistent"  # Stay visible longer
    PRIORITY_ONLY = "priority_only"
    CUSTOM = "custom"


class FocusAssistLevel(str, Enum):
    """Focus assist feature levels."""

    OFF = "off"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


class LayoutDensity(str, Enum):
    """Density options for UI layout."""

    COMPACT = "compact"
    STANDARD = "standard"
    SPACIOUS = "spacious"


class AccessibilityPreferences(BaseModel):
    """User's accessibility preferences for UI customization."""

    user_id: str
    color_theme: ColorTheme = ColorTheme.STANDARD
    font_style: FontStyle = FontStyle.STANDARD
    font_size: int = 16  # Base font size in pixels
    line_spacing: float = 1.5  # Line height multiplier
    animation_level: AnimationLevel = AnimationLevel.REDUCED
    notification_style: NotificationStyle = NotificationStyle.STANDARD
    focus_assist_level: FocusAssistLevel = FocusAssistLevel.MEDIUM
    layout_density: LayoutDensity = LayoutDensity.STANDARD
    reduced_motion: bool = False
    high_contrast: bool = False
    text_to_speech: bool = False
    keyboard_shortcuts_enabled: bool = True
    tooltip_delay: int = 500  # Milliseconds before tooltips appear
    use_visual_cues: bool = True  # Visual indicators for state changes
    use_audio_cues: bool = True  # Audio feedback for important actions
    simplify_ui: bool = False  # Simplified UI with fewer elements
    distraction_reduction: bool = True  # Reduce distracting elements
    color_overlay: Optional[str] = None  # CSS color for screen overlay
    custom_css: Optional[str] = None  # Custom CSS overrides
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class WCAGComplianceLevel(str, Enum):
    """WCAG 2.2 compliance levels."""

    A = "a"
    AA = "aa"
    AAA = "aaa"


class WCAGGuideline(BaseModel):
    """Representation of a WCAG 2.2 guideline."""

    id: str  # E.g., "1.4.3"
    name: str
    description: str
    level: WCAGComplianceLevel
    impact_for_adhd: str
    implementation_status: bool = False


class AccessibilityService:
    """
    Service for managing UI accessibility features, optimized for neurodiverse users
    with a focus on ADHD support and WCAG 2.2 compliance.
    """

    def __init__(self):
        self.default_preferences = AccessibilityPreferences(user_id="default")
        self.user_preferences: Dict[str, AccessibilityPreferences] = {}
        self.wcag_guidelines = self._load_wcag_guidelines()

    def _load_wcag_guidelines(self) -> List[WCAGGuideline]:
        """Load WCAG 2.2 guidelines relevant for ADHD users."""
        guidelines = [
            WCAGGuideline(
                id="1.4.3",
                name="Contrast (Minimum)",
                description="Text and images have sufficient contrast",
                level=WCAGComplianceLevel.AA,
                impact_for_adhd="Helps users focus on content without strain",
                implementation_status=True,
            ),
            WCAGGuideline(
                id="1.4.10",
                name="Reflow",
                description="Content can be presented without scrolling in two dimensions",
                level=WCAGComplianceLevel.AA,
                impact_for_adhd="Reduces cognitive load from managing complex layouts",
                implementation_status=True,
            ),
            WCAGGuideline(
                id="1.4.12",
                name="Text Spacing",
                description="No loss of content when text spacing is adjusted",
                level=WCAGComplianceLevel.AA,
                impact_for_adhd="Allows for text customization to improve readability",
                implementation_status=True,
            ),
            WCAGGuideline(
                id="2.2.1",
                name="Timing Adjustable",
                description="Time limits have user controls",
                level=WCAGComplianceLevel.A,
                impact_for_adhd="Critical for ADHD users who may need extra time",
                implementation_status=True,
            ),
            WCAGGuideline(
                id="2.4.5",
                name="Multiple Ways",
                description="Multiple ways to locate a page",
                level=WCAGComplianceLevel.AA,
                impact_for_adhd="Helps users who may forget navigation paths",
                implementation_status=True,
            ),
            WCAGGuideline(
                id="2.4.7",
                name="Focus Visible",
                description="Keyboard focus indicator is visible",
                level=WCAGComplianceLevel.AA,
                impact_for_adhd="Crucial for users who lose track of focus",
                implementation_status=True,
            ),
            WCAGGuideline(
                id="2.5.5",
                name="Target Size (Enhanced)",
                description="Clickable targets are at least 44x44 pixels",
                level=WCAGComplianceLevel.AAA,
                impact_for_adhd="Reduces errors for users with motor control variations",
                implementation_status=True,
            ),
            WCAGGuideline(
                id="2.5.8",
                name="Target Spacing",
                description="Adequate spacing between interactive elements",
                level=WCAGComplianceLevel.AA,
                impact_for_adhd="Prevents accidental clicks, important for impulsivity",
                implementation_status=True,
            ),
            WCAGGuideline(
                id="3.2.4",
                name="Consistent Identification",
                description="Components with same functionality are identified consistently",
                level=WCAGComplianceLevel.AA,
                impact_for_adhd="Reduces cognitive load through predictability",
                implementation_status=True,
            ),
            WCAGGuideline(
                id="3.3.7",
                name="Accessible Authentication",
                description="Authentication without cognitive function tests",
                level=WCAGComplianceLevel.A,
                impact_for_adhd="Reduces barriers for users with memory challenges",
                implementation_status=True,
            ),
        ]
        return guidelines

    async def get_user_preferences(self, user_id: str) -> AccessibilityPreferences:
        """Get accessibility preferences for a user, or create default ones."""
        if user_id in self.user_preferences:
            return self.user_preferences[user_id]

        # Create default preferences for the user
        prefs = AccessibilityPreferences(user_id=user_id)
        self.user_preferences[user_id] = prefs
        return prefs

    async def update_user_preferences(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> AccessibilityPreferences:
        """Update specific accessibility preferences for a user."""
        current_prefs = await self.get_user_preferences(user_id)

        # Get the original timestamp for later comparison
        original_timestamp = current_prefs.last_updated

        # Update only the fields that are provided
        for key, value in preferences.items():
            if hasattr(current_prefs, key):
                setattr(current_prefs, key, value)

        # Update timestamp, ensure it's greater than the original
        new_timestamp = datetime.utcnow()

        # In case the timestamps would be equal (happens in fast tests)
        # force the timestamp to be at least 1 microsecond later
        if new_timestamp <= original_timestamp:
            from datetime import timedelta

            new_timestamp = original_timestamp + timedelta(microseconds=1)

        current_prefs.last_updated = new_timestamp

        # Save the updated preferences
        self.user_preferences[user_id] = current_prefs
        return current_prefs

    async def get_theme_css(self, user_id: str) -> Dict[str, str]:
        """Generate CSS variables based on user preferences."""
        prefs = await self.get_user_preferences(user_id)

        # Base CSS variables
        css_vars = {}

        # Apply color theme
        if prefs.color_theme == ColorTheme.HIGH_CONTRAST:
            css_vars.update(
                {
                    "--background-color": "#000000",
                    "--text-color": "#ffffff",
                    "--primary-color": "#ffff00",
                    "--secondary-color": "#00ffff",
                    "--accent-color": "#ff00ff",
                    "--success-color": "#00ff00",
                    "--error-color": "#ff0000",
                    "--warning-color": "#ffa500",
                    "--info-color": "#00ffff",
                    "--border-color": "#ffffff",
                }
            )
        elif prefs.color_theme == ColorTheme.DARK:
            css_vars.update(
                {
                    "--background-color": "#121212",
                    "--text-color": "#e0e0e0",
                    "--primary-color": "#bb86fc",
                    "--secondary-color": "#03dac6",
                    "--accent-color": "#cf6679",
                    "--success-color": "#4caf50",
                    "--error-color": "#f44336",
                    "--warning-color": "#ff9800",
                    "--info-color": "#2196f3",
                    "--border-color": "#333333",
                }
            )
        elif prefs.color_theme == ColorTheme.CALM:
            css_vars.update(
                {
                    "--background-color": "#f5f5f7",
                    "--text-color": "#333333",
                    "--primary-color": "#6b8e9a",
                    "--secondary-color": "#a2b9bc",
                    "--accent-color": "#b2ad7f",
                    "--success-color": "#8fbc8f",
                    "--error-color": "#c8a2c8",
                    "--warning-color": "#e8d2a6",
                    "--info-color": "#add8e6",
                    "--border-color": "#d3d3d3",
                }
            )
        elif prefs.color_theme == ColorTheme.FOCUS:
            css_vars.update(
                {
                    "--background-color": "#ffffff",
                    "--text-color": "#333333",
                    "--primary-color": "#3949ab",
                    "--secondary-color": "#5c6bc0",
                    "--accent-color": "#d81b60",
                    "--success-color": "#2e7d32",
                    "--error-color": "#c62828",
                    "--warning-color": "#f57f17",
                    "--info-color": "#0277bd",
                    "--border-color": "#e0e0e0",
                }
            )
        else:  # Standard or other themes
            css_vars.update(
                {
                    "--background-color": "#ffffff",
                    "--text-color": "#333333",
                    "--primary-color": "#1976d2",
                    "--secondary-color": "#03a9f4",
                    "--accent-color": "#e91e63",
                    "--success-color": "#4caf50",
                    "--error-color": "#f44336",
                    "--warning-color": "#ff9800",
                    "--info-color": "#2196f3",
                    "--border-color": "#e0e0e0",
                }
            )

        # Apply font settings
        if prefs.font_style == FontStyle.DYSLEXIC_FRIENDLY:
            css_vars["--font-family"] = '"Lexend Deca", sans-serif'
        elif prefs.font_style == FontStyle.OPEN_DYSLEXIC:
            css_vars["--font-family"] = '"OpenDyslexic", sans-serif'
        elif prefs.font_style == FontStyle.COMIC_SANS:
            css_vars["--font-family"] = '"Comic Sans MS", cursive, sans-serif'
        else:
            css_vars["--font-family"] = '"Inter", system-ui, sans-serif'

        # Font size and spacing
        css_vars["--base-font-size"] = f"{prefs.font_size}px"
        css_vars["--line-height"] = str(prefs.line_spacing)

        # Spacing based on layout density
        if prefs.layout_density == LayoutDensity.COMPACT:
            css_vars["--spacing-unit"] = "0.75rem"
        elif prefs.layout_density == LayoutDensity.SPACIOUS:
            css_vars["--spacing-unit"] = "1.5rem"
        else:  # Standard
            css_vars["--spacing-unit"] = "1rem"

        # Animation settings
        if prefs.animation_level == AnimationLevel.NONE or prefs.reduced_motion:
            css_vars["--transition-duration"] = "0s"
            css_vars["--animation-enabled"] = "none"
        elif prefs.animation_level == AnimationLevel.MINIMAL:
            css_vars["--transition-duration"] = "0.1s"
            css_vars["--animation-enabled"] = "minimal"
        elif prefs.animation_level == AnimationLevel.REDUCED:
            css_vars["--transition-duration"] = "0.2s"
            css_vars["--animation-enabled"] = "reduced"
        else:  # Full animations
            css_vars["--transition-duration"] = "0.3s"
            css_vars["--animation-enabled"] = "all"

        # Accessibility enhancements
        if prefs.high_contrast:
            css_vars["--contrast-mode"] = "high"
        else:
            css_vars["--contrast-mode"] = "normal"

        # Simplified UI
        if prefs.simplify_ui:
            css_vars["--ui-complexity"] = "simplified"
        else:
            css_vars["--ui-complexity"] = "standard"

        # Custom overlay
        if prefs.color_overlay:
            css_vars["--color-overlay"] = prefs.color_overlay

        return css_vars

    async def get_wcag_compliance_report(self) -> Dict[str, Any]:
        """Generate a WCAG 2.2 compliance report for the application."""
        total_guidelines = len(self.wcag_guidelines)
        implemented_guidelines = sum(1 for g in self.wcag_guidelines if g.implementation_status)

        compliance_by_level = {
            WCAGComplianceLevel.A: {"total": 0, "implemented": 0},
            WCAGComplianceLevel.AA: {"total": 0, "implemented": 0},
            WCAGComplianceLevel.AAA: {"total": 0, "implemented": 0},
        }

        for guideline in self.wcag_guidelines:
            compliance_by_level[guideline.level]["total"] += 1
            if guideline.implementation_status:
                compliance_by_level[guideline.level]["implemented"] += 1

        # Calculate compliance percentages
        compliance_percentages = {}
        for level, counts in compliance_by_level.items():
            if counts["total"] > 0:
                compliance_percentages[level] = (counts["implemented"] / counts["total"]) * 100
            else:
                compliance_percentages[level] = 0

        # Determine overall compliance level
        overall_level = WCAGComplianceLevel.AAA  # Start with highest
        for level in [WCAGComplianceLevel.A, WCAGComplianceLevel.AA, WCAGComplianceLevel.AAA]:
            if compliance_percentages[level] < 100:
                # Drop to the previous level (or stay at A if already there)
                if level == WCAGComplianceLevel.A:
                    overall_level = None  # Not fully compliant with any level
                    break
                elif level == WCAGComplianceLevel.AA:
                    overall_level = WCAGComplianceLevel.A
                    break
                else:  # AAA
                    overall_level = WCAGComplianceLevel.AA
                    break

        return {
            "total_guidelines": total_guidelines,
            "implemented_guidelines": implemented_guidelines,
            "compliance_percentage": (
                (implemented_guidelines / total_guidelines) * 100 if total_guidelines > 0 else 0
            ),
            "compliance_by_level": {k.value: v for k, v in compliance_by_level.items()},
            "compliance_percentages": {k.value: v for k, v in compliance_percentages.items()},
            "overall_compliance_level": overall_level.value if overall_level else "none",
            "guidelines": [g.dict() for g in self.wcag_guidelines],
        }

    def generate_focus_assist_styles(self, level: FocusAssistLevel) -> Dict[str, str]:
        """Generate CSS styles for focus assist features."""
        styles = {}

        if level == FocusAssistLevel.OFF:
            return styles

        # Basic focus styles for all levels
        styles["focus-outline"] = "2px solid var(--primary-color)"

        if level == FocusAssistLevel.LOW:
            styles["dim-background"] = "rgba(0, 0, 0, 0.1)"
            styles["highlight-intensity"] = "0.1"
        elif level == FocusAssistLevel.MEDIUM:
            styles["dim-background"] = "rgba(0, 0, 0, 0.3)"
            styles["highlight-intensity"] = "0.3"
            styles["zoom-factor"] = "1.05"
        elif level == FocusAssistLevel.HIGH:
            styles["dim-background"] = "rgba(0, 0, 0, 0.5)"
            styles["highlight-intensity"] = "0.5"
            styles["zoom-factor"] = "1.1"
            styles["reduce-periphery"] = "true"
        elif level == FocusAssistLevel.MAXIMUM:
            styles["dim-background"] = "rgba(0, 0, 0, 0.7)"
            styles["highlight-intensity"] = "0.7"
            styles["zoom-factor"] = "1.15"
            styles["reduce-periphery"] = "true"
            styles["hide-non-essential"] = "true"

        return styles

    async def generate_adhd_optimized_ui_settings(
        self, user_id: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate ADHD-optimized UI settings based on user preferences and current context.
        Context may include time of day, user energy level, or other factors.
        """
        prefs = await self.get_user_preferences(user_id)
        context = context or {}

        # Get base CSS theme
        css_vars = await self.get_theme_css(user_id)

        # Adjust based on time of day if available
        hour = context.get("current_hour", datetime.now().hour)
        if hour >= 20 or hour < 6:  # Night mode
            # Reduce blue light in evening
            if css_vars["--background-color"] == "#ffffff":
                css_vars["--background-color"] = "#f5e6c8"  # Warm background
            css_vars["--blue-light-filter"] = "0.7"  # Reduce blue light
        else:
            css_vars["--blue-light-filter"] = "0"

        # Adjust based on user energy level
        energy_level = context.get("energy_level", 0.5)
        if energy_level < 0.3:  # Low energy
            # Increase contrast and reduce complexity
            css_vars["--contrast-enhancement"] = "1.2"
            if not prefs.simplify_ui:
                css_vars["--ui-density"] = "spacious"  # More space when tired

        # Adjust focus assist based on task importance
        task_importance = context.get("task_importance", 0.5)
        if task_importance > 0.7:
            focus_level = FocusAssistLevel.HIGH
        elif task_importance > 0.4:
            focus_level = FocusAssistLevel.MEDIUM
        else:
            focus_level = prefs.focus_assist_level

        focus_styles = self.generate_focus_assist_styles(focus_level)

        # Combine all settings
        settings = {
            "css_variables": css_vars,
            "focus_styles": focus_styles,
            "notifications": {
                "style": prefs.notification_style.value,
                "duration": (
                    5000 if prefs.notification_style == NotificationStyle.PERSISTENT else 3000
                ),
                "position": "top-right",
                "max_visible": 3 if not prefs.simplify_ui else 1,
                "audio_enabled": prefs.use_audio_cues,
            },
            "interactions": {
                "tooltip_delay": prefs.tooltip_delay,
                "visual_feedback": prefs.use_visual_cues,
                "audio_feedback": prefs.use_audio_cues,
                "keyboard_shortcuts": prefs.keyboard_shortcuts_enabled,
                "touch_target_size": "large",  # WCAG 2.5.5 compliance
                "touch_target_spacing": "adequate",  # WCAG 2.5.8 compliance
            },
        }

        # Add custom CSS if provided
        if prefs.custom_css:
            settings["custom_css"] = prefs.custom_css

        return settings
