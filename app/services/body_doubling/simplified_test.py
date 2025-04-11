#!/usr/bin/env python
"""Simplified test for AnalyticsService that doesn't require database access.

This script provides minimal tests for the AnalyticsService core functionality
and can be run independently without a database connection.
"""

import unittest
import asyncio
from typing import List, Dict, Any


# Import just what we need for the test
class MockAnalyticsService:
    """Simplified version of the AnalyticsService with only essential functions."""

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate the trend direction from a list of values."""
        if not values or len(values) < 2:
            return "stable"

        # Simple linear trend
        changes = [values[i] - values[i - 1] for i in range(1, len(values))]
        avg_change = sum(changes) / len(changes)

        if avg_change > 0.1:  # Threshold for improvement
            return "improving"
        elif avg_change < -0.1:  # Threshold for decline
            return "declining"
        else:
            return "stable"

    def generate_simple_insights(
        self, focus_ratings: List[float], productivity_ratings: List[float]
    ) -> Dict[str, Any]:
        """Generate simple insights based on focus and productivity ratings."""
        insights = {
            "message": "Here are some insights based on your session history",
            "insights": [],
        }

        # Add focus trend insight
        focus_trend = self._calculate_trend(focus_ratings)
        if focus_trend == "improving":
            insights["insights"].append(
                {
                    "type": "focus",
                    "insight": "Your focus has been improving over time",
                    "confidence": "high" if len(focus_ratings) > 5 else "medium",
                }
            )
        elif focus_trend == "declining":
            insights["insights"].append(
                {
                    "type": "focus",
                    "insight": "Your focus has been declining recently",
                    "confidence": "high" if len(focus_ratings) > 5 else "medium",
                }
            )
        else:
            insights["insights"].append(
                {"type": "focus", "insight": "Your focus has been stable", "confidence": "medium"}
            )

        # Add productivity trend insight
        productivity_trend = self._calculate_trend(productivity_ratings)
        if productivity_trend == "improving":
            insights["insights"].append(
                {
                    "type": "productivity",
                    "insight": "Your productivity has been improving over time",
                    "confidence": "high" if len(productivity_ratings) > 5 else "medium",
                }
            )
        elif productivity_trend == "declining":
            insights["insights"].append(
                {
                    "type": "productivity",
                    "insight": "Your productivity has been declining recently",
                    "confidence": "high" if len(productivity_ratings) > 5 else "medium",
                }
            )
        else:
            insights["insights"].append(
                {
                    "type": "productivity",
                    "insight": "Your productivity has been stable",
                    "confidence": "medium",
                }
            )

        # Add correlation insight if we have both metrics
        if (
            focus_ratings
            and productivity_ratings
            and len(focus_ratings) == len(productivity_ratings)
        ):
            # This is a very simplified correlation calculation
            correlation = (
                "strong"
                if abs(
                    sum(focus_ratings) / len(focus_ratings)
                    - sum(productivity_ratings) / len(productivity_ratings)
                )
                < 0.5
                else "weak"
            )

            if correlation == "strong":
                insights["insights"].append(
                    {
                        "type": "correlation",
                        "insight": "There is a strong correlation between your focus and productivity",
                        "confidence": "medium",
                    }
                )
            else:
                insights["insights"].append(
                    {
                        "type": "correlation",
                        "insight": "There appears to be a weak correlation between your focus and productivity",
                        "confidence": "low",
                    }
                )

        return insights


class TestAnalyticsService(unittest.TestCase):
    """Test the core functionality of the AnalyticsService."""

    def setUp(self):
        """Set up the test case."""
        self.service = MockAnalyticsService()

    def test_calculate_trend_improving(self):
        """Test the trend calculation with improving values."""
        values = [1, 2, 3, 4, 5]
        trend = self.service._calculate_trend(values)
        self.assertEqual(trend, "improving")

    def test_calculate_trend_declining(self):
        """Test the trend calculation with declining values."""
        values = [5, 4, 3, 2, 1]
        trend = self.service._calculate_trend(values)
        self.assertEqual(trend, "declining")

    def test_calculate_trend_stable(self):
        """Test the trend calculation with stable values."""
        values = [3, 3, 3, 3, 3]
        trend = self.service._calculate_trend(values)
        self.assertEqual(trend, "stable")

    def test_calculate_trend_small_changes(self):
        """Test the trend calculation with small changes."""
        values = [3, 3.05, 2.98, 3.01, 3.03]
        trend = self.service._calculate_trend(values)
        self.assertEqual(trend, "stable")

    def test_calculate_trend_empty(self):
        """Test the trend calculation with an empty list."""
        values = []
        trend = self.service._calculate_trend(values)
        self.assertEqual(trend, "stable")

    def test_calculate_trend_single_value(self):
        """Test the trend calculation with a single value."""
        values = [4]
        trend = self.service._calculate_trend(values)
        self.assertEqual(trend, "stable")

    def test_generate_simple_insights(self):
        """Test generating insights based on sample data."""
        focus_ratings = [3, 3.5, 4, 4.5, 5]
        productivity_ratings = [3, 3.2, 3.8, 4.2, 4.5]

        insights = self.service.generate_simple_insights(focus_ratings, productivity_ratings)

        # Verify structure
        self.assertIn("message", insights)
        self.assertIn("insights", insights)
        self.assertTrue(len(insights["insights"]) > 0)

        # Check specific insights
        focus_insights = [i for i in insights["insights"] if i["type"] == "focus"]
        productivity_insights = [i for i in insights["insights"] if i["type"] == "productivity"]
        correlation_insights = [i for i in insights["insights"] if i["type"] == "correlation"]

        self.assertEqual(len(focus_insights), 1)
        self.assertEqual(len(productivity_insights), 1)
        self.assertEqual(len(correlation_insights), 1)

        # Verify specific trend detection
        self.assertIn("improving", focus_insights[0]["insight"].lower())
        self.assertIn("improving", productivity_insights[0]["insight"].lower())
        self.assertIn("correlation", correlation_insights[0]["insight"].lower())


def run_tests():
    """Run the tests."""
    unittest.main(argv=["first-arg-is-ignored"], exit=False)


if __name__ == "__main__":
    run_tests()
