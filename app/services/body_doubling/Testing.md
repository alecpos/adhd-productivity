# Testing the Body Doubling AnalyticsService

This document provides guidance on testing the `AnalyticsService` component of the Body Doubling Service.

## Setting Up the Test Environment

1. Ensure you have all project dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Install pytest if not already installed:
   ```bash
   pip install pytest
   ```

3. Optional: Install transformers for AI-powered insights testing:
   ```bash
   # For most systems
   pip install transformers torch
   
   # For Mac (to avoid TensorFlow/Metal issues)
   pip uninstall -y tensorflow tensorflow-macos
   pip install torch transformers
   ```

## Running Tests

### Basic Tests

Run all tests or specific components using pytest:

```bash
# Run all Body Doubling Service tests 
./scripts/run_body_doubling_simple_tests.sh

# Or run specific test modules
python -m app.tests.services.body_doubling.test_simple
python -m app.services.body_doubling.simplified_test
python -m app.tests.services.body_doubling.test_analytics_direct
```

### Standalone Test with Mocked Models

To avoid SQLAlchemy model dependency issues (like the TaskCategoryModel error), use the standalone test:

```bash
# Run the standalone test script with mocked models
./scripts/run_standalone_test.sh
```

This approach uses mock models injected into `sys.modules` before SQLAlchemy initialization.

### AI-Powered Insight Generation Testing

The mock tests now support testing the insight generation with actual ML models:

```bash
# Run tests with Hugging Face transformers for AI-powered insights
./scripts/run_standalone_test.sh --ai

# For Mac users with TensorFlow issues, use PyTorch-only mode
./scripts/run_standalone_test.sh --ai --pytorch
```

If the transformers library is available, the tests will use a pre-trained language model to generate insights based on mock session data. If not, it will fall back to static mock insights.

#### Mac-Specific Test Solutions

For Mac users who encounter TensorFlow or Metal plugin issues, we now offer multiple solutions:

1. **PyTorch-only Mode**: The simplest approach that bypasses TensorFlow completely:
   ```bash
   ./scripts/run_standalone_test.sh --ai --pytorch
   ```
   This uses a custom PyTorch-based implementation that doesn't require TensorFlow at all.

2. **Remove TensorFlow**: If you want to use the full transformers library without TensorFlow:
   ```bash
   pip uninstall -y tensorflow tensorflow-macos
   pip install torch transformers
   ./scripts/run_standalone_test.sh --ai
   ```

3. **Use Mock Insights**: If you don't need AI-powered insights for testing:
   ```bash
   ./scripts/run_standalone_test.sh
   ```

### Available Test Modules

The Body Doubling AnalyticsService has several test modules targeting different aspects:

1. **test_simple.py**: Tests the core `_calculate_trend` method with various input patterns.

2. **simplified_test.py**: Standalone tests for core functionality without database dependencies.

3. **test_analytics_direct.py**: Direct tests for the complete service using mocks to simulate database interactions.

4. **standalone_test.py**: Tests that use mock model injection to avoid database model dependency issues.

5. **manual_test.py**: A script to manually test the service with mock database sessions (requires full DB setup).

### Testing Specific Features

The `AnalyticsService` provides several methods for analyzing body doubling sessions:

- `get_user_analytics`: Retrieves analytics for a user based on their session history
- `get_session_analytics`: Retrieves analytics for a specific session
- `get_session_feedback`: Retrieves feedback for a specific session
- `add_session_feedback`: Adds feedback for a session
- `get_focus_pattern_insights`: Generates insights about a user's focus patterns (now with optional ML support)

## Testing with Real Data

To test the service with actual database data:

```python
from app.services.body_doubling.analytics_service import AnalyticsService
from app.database.session import get_db_session

async def test_with_real_db():
    async with get_db_session() as db:
        analytics_service = AnalyticsService(db)
        
        # Get user analytics
        user_id = "user_uuid_here"
        analytics = await analytics_service.get_user_analytics(user_id)
        print(f"Total sessions: {analytics.total_sessions}")
        
        # Get focus pattern insights
        insights = await analytics_service.get_focus_pattern_insights(user_id)
        print(f"Insights: {insights}")
```

## Troubleshooting

### Common SQLAlchemy Model Dependency Errors

When you see errors like:

```
sqlalchemy.exc.InvalidRequestError: When initializing mapper Mapper[UserModel(users)], 
expression 'TaskCategoryModel' failed to locate a name ('TaskCategoryModel').
```

Use the standalone test approach with mock models:

1. Create mock versions of the required models in `mock_models.py`
2. Inject them into `sys.modules` before importing the actual models
3. Run with the standalone test script

### Hugging Face Transformer Issues

#### General Import Issues

If you encounter errors with transformer models:

```
ImportError: Failed to import transformers
```

The test will automatically fall back to using static mock insights. If you want to test with the AI-powered insights:

1. Install the required libraries: `pip install transformers torch`
2. Ensure you have enough memory for the model (even small models need ~500MB)
3. For faster testing, the first run will download the model which might take time

#### TensorFlow/Metal Plugin Issues on Mac

If you see errors like:

```
dlopen(/opt/homebrew/lib/python3.11/site-packages/tensorflow-plugins/libmetal_plugin.dylib, 0x0006): 
Symbol not found: __ZN3tsl8internal10LogMessageC1EPKcii
```

Or:

```
⚠️ TensorFlow or Metal plugin issue detected
This is likely due to TensorFlow/Metal compatibility issues on Mac
```

This is a common issue with TensorFlow and the Metal plugin on Mac. To resolve it:

1. **Use our PyTorch-only Mode** (Recommended):
   ```bash
   ./scripts/run_standalone_test.sh --ai --pytorch
   ```
   This solution completely bypasses TensorFlow, using a custom PyTorch-based implementation that doesn't require the transformers library to load TensorFlow at all.

2. Uninstall TensorFlow and related packages:
   ```bash
   pip uninstall -y tensorflow tensorflow-macos
   ```

3. Install PyTorch and transformers only:
   ```bash
   pip install torch transformers
   ```

4. Run the test again:
   ```bash
   ./scripts/run_standalone_test.sh --ai
   ```

The code now automatically tries to use PyTorch only (without TensorFlow) to avoid these issues, but explicitly using the `--pytorch` flag provides the most reliable solution for Mac users.

#### Keras 3 Compatibility Issue

If you see this error:

```
⚠️ Keras 3 detected, which is incompatible with current transformers.
   To use AI insights, install the backwards-compatible tf-keras:
   pip install tf-keras
```

This is due to a known compatibility issue between Keras 3 and current versions of Transformers. To resolve it:

1. Install the backward-compatible tf-keras package:
   ```bash
   pip install tf-keras
   ```

2. Run the test again:
   ```bash
   ./scripts/run_standalone_test.sh --ai
   ```

For Mac users experiencing both Keras 3 and TensorFlow/Metal issues, we recommend using the PyTorch-only mode:
```bash
./scripts/run_standalone_test.sh --ai --pytorch
```

### Python Path Issues

If you encounter import errors, ensure your project structure is correct and the `PYTHONPATH` includes the project root:

```bash
export PYTHONPATH=$PYTHONPATH:/path/to/project/root
```

## Key Testing Components

### AI-Powered Insight Generation

The mock tests now include an `InsightGenerator` class that can use Hugging Face transformers:

```python
class InsightGenerator:
    def __init__(self):
        # Initialize transformer model for text generation if available
        if TRANSFORMERS_AVAILABLE:
            try:
                # Explicitly use PyTorch to avoid TensorFlow issues
                from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
                model_name = "distilgpt2"
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(model_name)
                
                self.text_generator = pipeline(
                    "text-generation", 
                    model=model,
                    tokenizer=tokenizer,
                    max_length=50,
                    framework="pt"  # Force PyTorch
                )
            except Exception:
                self.text_generator = None
```

For Mac users, we also provide a PyTorch-only fallback:

```python
# PyTorch-only implementation for Mac users
class SimplePyTorchGenerator:
    def __init__(self):
        self.responses = [
            "you tend to be most productive when you have a clear goal.",
            "your focus improves significantly in distraction-free environments.",
            # More predefined responses...
        ]
    
    def __call__(self, prompt):
        # Use torch random to select a response
        idx = torch.randint(0, len(self.responses), (1,)).item()
        response = self.responses[idx]
        return [{"generated_text": prompt + response}]
```

### Mock Models for Dependency Resolution

The standalone test uses mock model injection to avoid dependency issues:

```python
# Create a mock module for the task_category_model
mock_module_name = "app.models.task_category_model"
mock_spec = importlib.util.find_spec("app.services.body_doubling.mock_models")
mock_module = importlib.util.module_from_spec(mock_spec)
sys.modules[mock_module_name] = mock_module

# Add the TaskCategoryModel to the mock module
setattr(sys.modules[mock_module_name], "TaskCategoryModel", MockTaskCategoryModel)
```

### Mock Session

The simplified tests use `MockAnalyticsService` which implements the core algorithms without database dependencies:

```python
class MockAnalyticsService:
    def _calculate_trend(self, values):
        # Implementation for trend calculation
        # ...
    
    def generate_simple_insights(self, focus_ratings, productivity_ratings):
        # Generate insights based on ratings
        # ...
```

### Mock Database Session

Direct tests use a mock database session to simulate interactions:

```python
db_mock = AsyncMock()
execute_mock = MagicMock()
execute_mock.scalar_one_or_none.return_value = mock_session
db_mock.execute.return_value = execute_mock
```

## Further Improvements

- **Edge Cases**: Add tests for edge cases like empty databases, invalid inputs, etc.
- **Performance Testing**: Add tests to measure performance under load in `performance_test.py`.
- **Integration Testing**: Develop tests that verify how the `AnalyticsService` works with other components.
- **Error Handling**: Add tests for error cases and verify appropriate exceptions are raised.
- **Additional ML Models**: Experiment with different models for insight generation to improve quality.
- **PyTorch vs TensorFlow**: The code now prefers PyTorch to avoid TensorFlow issues, but you could add an option to explicitly choose which ML backend to use.

To run performance tests:
```bash
python -m app.services.body_doubling.performance_test
``` 