#!/usr/bin/env python3
"""
Test script for CommitmentDetectionService resilience patterns.
"""

import sys
import os
import logging
from datetime import datetime
from uuid import uuid4

# Add the parent directory to the path to allow importing app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("commitment_test")

from sqlalchemy.orm import Session
from app.services.commitment_detection_service import CommitmentDetectionService
from app.services.base_service import BaseService, OPEN, CLOSED, HALF_OPEN
from app.schemas.commitment_schema import CommitmentDetectionRequest, CommitmentInDB
from app.models.commitment_model import CommitmentModel, CommitmentSource, CommitmentStatus

class MockDB:
    """Mock database session for testing."""
    def __init__(self):
        self.committed = False
        self.rollbacked = False
    
    def add(self, obj):
        logger.info(f"Added object: {obj}")
        return
        
    def commit(self):
        self.committed = True
        logger.info("Committed to database")
        return
        
    def rollback(self):
        self.rollbacked = True
        logger.info("Rollback performed")
        return
        
    def refresh(self, obj):
        logger.info(f"Refreshed object: {obj}")
        return
        
    def query(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self
        
    def first(self):
        return None

class MockLLMService:
    """Mock LLM service for testing."""
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        
    def analyze_text_for_commitments(self, text, context=None):
        if self.should_fail:
            raise Exception("LLM service failure")
            
        return {
            "commitments": [
                {
                    "text": "call mom tomorrow",
                    "confidence": 0.85,
                    "priority": "HIGH",
                    "due_date": datetime.now().isoformat()
                }
            ]
        }
        
    def check_availability(self):
        return not self.should_fail

def test_resilience_patterns():
    """Test the resilience patterns in CommitmentDetectionService."""
    logger.info("=== Testing CommitmentDetectionService Resilience Patterns ===")
    
    # Setup
    db = MockDB()
    llm_service = MockLLMService()
    
    # Initialize service
    service = CommitmentDetectionService(db)
    logger.info("Service initialized successfully")
    
    # Check for resilience pattern attributes
    logger.info("Checking for resilience pattern implementations:")
    
    # Check for circuit breaker decorator in detect_commitments method
    detect_method = service.detect_commitments
    circuit_breaker_found = False
    retry_found = False
    
    # Try to unwrap the method to check for decorators
    while hasattr(detect_method, '__wrapped__'):
        detect_method_name = detect_method.__qualname__ if hasattr(detect_method, '__qualname__') else str(detect_method)
        logger.info(f"Found wrapped method: {detect_method_name}")
        
        if 'circuit_breaker' in detect_method_name.lower():
            circuit_breaker_found = True
            logger.info("Circuit breaker decorator found")
            
        if 'retry' in detect_method_name.lower():
            retry_found = True
            logger.info("Retry decorator found")
            
        detect_method = detect_method.__wrapped__
    
    # Check for retry pattern
    logger.info(f"Retry pattern: {'✓' if retry_found else '✗'}")
    
    # Check for circuit breaker pattern
    logger.info(f"Circuit breaker pattern: {'✓' if circuit_breaker_found else '✗'}")
    
    # Check for bulkhead pattern
    bulkhead = hasattr(service, '_llm_processing_bulkhead')
    logger.info(f"Bulkhead pattern: {'✓' if bulkhead else '✗'}")
    
    # Check for decorated methods
    methods_with_patterns = []
    for attr_name in dir(service):
        if not attr_name.startswith('_') and callable(getattr(service, attr_name)):
            method = getattr(service, attr_name)
            if hasattr(method, '__wrapped__'):
                methods_with_patterns.append(attr_name)
    
    if methods_with_patterns:
        logger.info(f"Methods with resilience patterns: {', '.join(methods_with_patterns)}")
    
    # Test service initialization only
    logger.info("\nDirectly checking service attributes:")
    
    # Look for circuit breaker implementation
    if hasattr(service, '_CircuitBreaker__circuit_states'):
        logger.info(f"Circuit breaker states found: {service._CircuitBreaker__circuit_states}")
    else:
        logger.info("Circuit breaker states not found in expected attribute")
        
    # Look for any attribute that might contain circuit breaker states
    for attr_name in dir(service):
        if 'circuit' in attr_name.lower() and not callable(getattr(service, attr_name)):
            try:
                attr_value = getattr(service, attr_name)
                logger.info(f"Found circuit-related attribute: {attr_name} = {attr_value}")
            except:
                pass
    
    # Check the source code directly
    logger.info("\nChecking for decorator usage in source code:")
    import inspect
    source = inspect.getsource(CommitmentDetectionService)
    
    if '@BaseService.with_retry' in source:
        logger.info("✓ Retry decorator found in source code")
    else:
        logger.info("✗ Retry decorator not found in source code")
        
    if '@BaseService.with_circuit_breaker' in source:
        logger.info("✓ Circuit breaker decorator found in source code")
    else:
        logger.info("✗ Circuit breaker decorator not found in source code")
    
    if 'with_bulkhead' in source:
        logger.info("✓ Bulkhead pattern found in source code")
    else:
        logger.info("✗ Bulkhead pattern not found in source code")
    
    logger.info("\n=== Test Complete ===")
    
if __name__ == "__main__":
    test_resilience_patterns() 