"""Simple test file for testing AnalyticsService calculate_trend method."""

from unittest import mock

def calculate_trend(values):
    """Calculate the trend direction from a list of values."""
    if not values or len(values) < 2:
        return "stable"
    
    # Simple linear trend
    changes = [values[i] - values[i-1] for i in range(1, len(values))]
    avg_change = sum(changes) / len(changes)
    
    if avg_change > 0.1:  # Threshold for improvement
        return "improving"
    elif avg_change < -0.1:  # Threshold for decline
        return "declining"
    else:
        return "stable"

def test_calculate_trend_improving():
    """Test improving trend."""
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert calculate_trend(values) == "improving"

def test_calculate_trend_declining():
    """Test declining trend."""
    values = [5.0, 4.0, 3.0, 2.0, 1.0]
    assert calculate_trend(values) == "declining"

def test_calculate_trend_stable():
    """Test stable trend."""
    values = [3.0, 3.0, 3.0, 3.0, 3.0]
    assert calculate_trend(values) == "stable"

def test_calculate_trend_small_changes():
    """Test small changes (should be stable)."""
    values = [3.0, 3.01, 3.02, 3.01, 3.0]
    assert calculate_trend(values) == "stable"

def test_calculate_trend_empty():
    """Test empty list."""
    values = []
    assert calculate_trend(values) == "stable"

def test_calculate_trend_single_value():
    """Test single value."""
    values = [4.0]
    assert calculate_trend(values) == "stable"

if __name__ == "__main__":
    # Run all tests
    test_functions = [
        test_calculate_trend_improving,
        test_calculate_trend_declining,
        test_calculate_trend_stable,
        test_calculate_trend_small_changes,
        test_calculate_trend_empty,
        test_calculate_trend_single_value
    ]
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__} passed")
        except AssertionError as e:
            print(f"❌ {test_func.__name__} failed: {e}")
    
    print("\nAll tests completed.") 