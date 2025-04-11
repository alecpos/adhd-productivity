"""
Pytest plugin for configuring asyncio properly.

This module sets up the proper event loop policy for pytest-asyncio to use.
It ensures there is always a valid event loop available for tests.
"""

import asyncio
import platform
import sys
import pytest


# Define the hook to set up asyncio for pytest
def pytest_configure(config):
    """Configure pytest to use the proper event loop policy."""
    # Use the appropriate event loop policy based on platform
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        # For MacOS and Linux, use the default policy but make sure event loops can be created
        policy = asyncio.get_event_loop_policy()

        # Patch the policy if needed to avoid "There is no current event loop in thread" errors
        original_get_event_loop = policy.get_event_loop

        def patched_get_event_loop():
            """Patched get_event_loop that creates a new loop if none exists."""
            try:
                loop = original_get_event_loop()
                return loop
            except RuntimeError:
                # If no event loop exists, create one and set it
                loop = policy.new_event_loop()
                asyncio.set_event_loop(loop)
                return loop

        # Apply the patch to the policy
        policy.get_event_loop = patched_get_event_loop


# Force the right event loop policy when this module is imported
pytest_configure(None)
