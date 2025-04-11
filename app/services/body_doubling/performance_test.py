#!/usr/bin/env python
"""Performance test for the AnalyticsService.

This script measures the performance of the AnalyticsService under load.
It creates multiple sessions and users, then measures the time taken for
various operations.

To run:
    python -m app.services.body_doubling.performance_test
"""

import asyncio
import uuid
import sys
import os
import time
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add project root to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Import required components
try:
    from app.database import get_session, init_db
    from app.services.body_doubling.analytics_service import AnalyticsService
    from app.models.body_doubling_model import BodyDoublingSessionModel
    from app.models.enums_model import SessionStatus, SessionType
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure the database and model dependencies are properly set up")
    sys.exit(1)

# Test configuration
NUM_USERS = 5
SESSIONS_PER_USER = 10
FEEDBACK_PER_SESSION = 3
CLEANUP_AFTER_TEST = True

async def setup_test_data(db) -> Tuple[List[uuid.UUID], List[uuid.UUID]]:
    """Set up test data for performance testing.
    
    Returns:
        Tuple containing lists of user IDs and session IDs
    """
    logger.info(f"Setting up test data: {NUM_USERS} users with {SESSIONS_PER_USER} sessions each")
    user_ids = []
    session_ids = []
    
    # Create users
    for _ in range(NUM_USERS):
        user_ids.append(uuid.uuid4())
    
    # Activity types and session types
    activity_types = ["Programming", "Reading", "Writing", "Studying", "Creative Work"]
    session_types = [SessionType.WORKING, SessionType.STUDYING, SessionType.CREATIVE]
    
    # Create sessions for each user
    for user_id in user_ids:
        for i in range(SESSIONS_PER_USER):
            now = datetime.now()
            days_ago = random.randint(1, 30)  # Random session between 1 and 30 days ago
            hours_duration = random.randint(1, 4)  # Random duration between 1 and 4 hours
            
            # Create a session
            session = BodyDoublingSessionModel(
                id=uuid.uuid4(),
                user_id=user_id,
                host_id=user_id,
                title=f"Performance Test Session {i+1}",
                description="Session for performance testing",
                start_time=now - timedelta(days=days_ago, hours=random.randint(0, 23)),
                end_time=now - timedelta(days=days_ago, hours=random.randint(0, 23)-hours_duration),
                status=SessionStatus.COMPLETED,
                session_type=random.choice(session_types),
                activity_type=random.choice(activity_types),
                focus_rating=random.randint(1, 5),
                productivity_rating=random.randint(1, 5),
                meta_data={
                    "participants": [str(user_id), str(random.choice(user_ids))],
                    "feedback": []
                }
            )
            
            # Add the session to the database
            db.add(session)
            session_ids.append(session.id)
            
            # Add feedback to the session
            for j in range(FEEDBACK_PER_SESSION):
                feedback = {
                    "user_id": str(user_id if j == 0 else random.choice(user_ids)),
                    "focus_rating": random.randint(1, 5),
                    "productivity_rating": random.randint(1, 5),
                    "distraction_level": random.randint(1, 5),
                    "notes": f"Feedback {j+1} for session {i+1}",
                    "timestamp": (datetime.now() - timedelta(days=days_ago-1)).isoformat()
                }
                
                if "feedback" not in session.meta_data:
                    session.meta_data["feedback"] = []
                
                session.meta_data["feedback"].append(feedback)
    
    # Commit all changes
    await db.commit()
    logger.info(f"Created {len(session_ids)} sessions for {len(user_ids)} users")
    
    return user_ids, session_ids

async def cleanup_test_data(db, session_ids):
    """Clean up test data after performance testing."""
    if not CLEANUP_AFTER_TEST:
        logger.info("Cleanup skipped as configured")
        return
    
    logger.info(f"Cleaning up {len(session_ids)} test sessions")
    for session_id in session_ids:
        try:
            session = await db.get(BodyDoublingSessionModel, session_id)
            if session:
                await db.delete(session)
        except Exception as e:
            logger.warning(f"Error deleting session {session_id}: {e}")
    
    await db.commit()
    logger.info("Cleanup completed")

async def measure_performance(analytics_service, user_ids, session_ids):
    """Measure the performance of AnalyticsService methods."""
    results = {}
    
    # Measure get_user_analytics performance
    start_time = time.time()
    for user_id in user_ids:
        await analytics_service.get_user_analytics(user_id)
    end_time = time.time()
    avg_time = (end_time - start_time) / len(user_ids)
    results["get_user_analytics"] = {
        "total_time": end_time - start_time,
        "avg_time": avg_time,
        "operations": len(user_ids)
    }
    logger.info(f"get_user_analytics: avg {avg_time:.4f} seconds per call")
    
    # Measure get_session_analytics performance
    start_time = time.time()
    sample_sessions = random.sample(session_ids, min(len(session_ids), 20))
    for session_id in sample_sessions:
        await analytics_service.get_session_analytics(session_id)
    end_time = time.time()
    avg_time = (end_time - start_time) / len(sample_sessions)
    results["get_session_analytics"] = {
        "total_time": end_time - start_time,
        "avg_time": avg_time,
        "operations": len(sample_sessions)
    }
    logger.info(f"get_session_analytics: avg {avg_time:.4f} seconds per call")
    
    # Measure get_session_feedback performance
    start_time = time.time()
    for session_id in sample_sessions:
        await analytics_service.get_session_feedback(session_id)
    end_time = time.time()
    avg_time = (end_time - start_time) / len(sample_sessions)
    results["get_session_feedback"] = {
        "total_time": end_time - start_time,
        "avg_time": avg_time,
        "operations": len(sample_sessions)
    }
    logger.info(f"get_session_feedback: avg {avg_time:.4f} seconds per call")
    
    # Measure get_focus_pattern_insights performance
    start_time = time.time()
    for user_id in user_ids:
        await analytics_service.get_focus_pattern_insights(user_id)
    end_time = time.time()
    avg_time = (end_time - start_time) / len(user_ids)
    results["get_focus_pattern_insights"] = {
        "total_time": end_time - start_time,
        "avg_time": avg_time,
        "operations": len(user_ids)
    }
    logger.info(f"get_focus_pattern_insights: avg {avg_time:.4f} seconds per call")
    
    # Measure add_session_feedback performance
    start_time = time.time()
    sample_sessions = random.sample(session_ids, min(len(session_ids), 10))
    feedback_count = 0
    for session_id in sample_sessions:
        user_id = random.choice(user_ids)
        feedback_data = {
            "focus_rating": random.randint(1, 5),
            "productivity_rating": random.randint(1, 5),
            "distraction_level": random.randint(1, 5),
            "notes": "Performance test feedback"
        }
        await analytics_service.add_session_feedback(session_id, user_id, feedback_data)
        feedback_count += 1
    end_time = time.time()
    avg_time = (end_time - start_time) / feedback_count if feedback_count > 0 else 0
    results["add_session_feedback"] = {
        "total_time": end_time - start_time,
        "avg_time": avg_time,
        "operations": feedback_count
    }
    logger.info(f"add_session_feedback: avg {avg_time:.4f} seconds per call")
    
    return results

async def run_performance_tests():
    """Run all performance tests."""
    logger.info("=== Starting AnalyticsService Performance Tests ===")
    
    # Initialize database if needed
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"Database initialization error (may be already initialized): {e}")
    
    # Create a db session
    session_ids = []
    try:
        # Set up test data
        async with get_session() as db:
            user_ids, session_ids = await setup_test_data(db)
        
        # Run performance tests
        async with get_session() as db:
            analytics_service = AnalyticsService(db)
            results = await measure_performance(analytics_service, user_ids, session_ids)
        
        # Display results summary
        logger.info("\nPerformance Test Results Summary:")
        logger.info(f"{'Method':<30} {'Avg Time (s)':<15} {'Total Time (s)':<15} {'Operations':<10}")
        for method, metrics in results.items():
            logger.info(f"{method:<30} {metrics['avg_time']:<15.4f} {metrics['total_time']:<15.4f} {metrics['operations']:<10}")
    
    except Exception as e:
        logger.error(f"Error during performance tests: {e}")
    finally:
        # Clean up the test data
        if session_ids:
            try:
                async with get_session() as db:
                    await cleanup_test_data(db, session_ids)
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
    
    logger.info("=== AnalyticsService Performance Tests Completed ===")

if __name__ == "__main__":
    # Run the async tests
    asyncio.run(run_performance_tests()) 