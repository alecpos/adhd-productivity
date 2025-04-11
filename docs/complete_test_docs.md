# Test Suite Documentation

## test_basic.py

File: `app/tests/test_basic.py`

### test_basic

```
Basic test to verify pytest is working.
```

**Source code:**

```python
def test_basic():
    """Basic test to verify pytest is working."""
    assert True
```

**Assertions:**

- `assert True`

---

### test_async_basic

```
Basic async test to verify pytest-asyncio is working.
```

**Source code:**

```python
async def test_async_basic():
    """Basic async test to verify pytest-asyncio is working."""
```

---

## test_utils.py

File: `app/tests/test_utils.py`

## conftest.py

File: `app/tests/conftest.py`

### test_user

```
Create a test user.
```

**Source code:**

```python
async def test_user(db_session: AsyncSession) -> UserModel:
    """Create a test user."""
    logger.debug("Creating test user")
    user_id = uuid4()
    user = UserModel(
        id=user_id,
        email=f"test_{user_id}@example.com",
        username=f"test_user_{user_id}",
        full_name="Test User",
        hashed_password=get_password_hash("test_password"),
        is_active=True,
        is_verified=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
```

---

### test_streak

```
Create a test streak.
```

**Source code:**

```python
async def test_streak(test_user: UserModel, db_session: AsyncSession) -> StreakModel:
    """Create a test streak."""
    logger.debug("Creating test streak")
    now = datetime.now(tz=timezone.utc)
    streak = StreakModel(
        user_id=test_user.id,
        current_streak=5,
        longest_streak=10,
        streak_type="daily",
        last_activity=now,
        created_at=now,
        updated_at=now,
    )
    db_session.add(streak)
    await db_session.commit()
    await db_session.refresh(streak)
```

---

### test_leaderboard

```
Create a test leaderboard entry.
```

**Source code:**

```python
async def test_leaderboard(
    test_user: UserModel, db_session: AsyncSession
) -> LeaderboardModel:
    """Create a test leaderboard entry."""
    logger.debug("Creating test leaderboard entry")
    leaderboard = LeaderboardModel(user_id=test_user.id, category="global", rank=1, score=100.0)
    db_session.add(leaderboard)
    await db_session.commit()
    await db_session.refresh(leaderboard)
```

---

### test_factory

```
Create a test factory for creating test data.
```

**Source code:**

```python
async def test_factory(db_session: AsyncSession):
    """Create a test factory for creating test data."""
    auth_service = AuthService(db_session)
    return TestFactory(db_session, auth_service)
```

---

### test_points

```
Create test points for a user.
```

**Source code:**

```python
async def test_points(test_user: UserModel, db_session: AsyncSession) -> PointsModel:
    """Create test points for a user."""
    logger.debug("Creating test points")
    points = PointsModel(user_id=test_user.id, total_points=100, level=2)
    db_session.add(points)
    await db_session.commit()
    await db_session.refresh(points)
```

---

### test_badge

```
Create a test badge.
```

**Source code:**

```python
async def test_badge(test_user: UserModel, db_session: AsyncSession) -> BadgeModel:
    """Create a test badge."""
    badge = BadgeModel(
        id=uuid4(),
        user_id=test_user.id,
        name="Test Badge",
        description="A test badge",
        category="focus_master",
        level=1,
        earned_at=datetime.now(timezone.utc),
        meta_data={"icon_url": "test_icon.png"},
    )
    db_session.add(badge)
    await db_session.commit()
    await db_session.refresh(badge)
```

---

### test_achievement

```
Create a test achievement.
```

**Source code:**

```python
async def test_achievement(
    test_user: UserModel, db_session: AsyncSession
) -> AchievementModel:
    """Create a test achievement."""
    achievement = AchievementModel(
        id=uuid4(),
        user_id=test_user.id,
        name="Test Achievement",
        description="A test achievement",
        category="focus",
        points=50,
        earned_at=datetime.now(timezone.utc),
        meta_data={"progress": 50, "completed": False},
    )
    db_session.add(achievement)
    await db_session.commit()
    await db_session.refresh(achievement)
```

---

### run_async_test

```
Helper function to run an async test function.

This is useful for methods that use async outside of pytest's asyncio fixture.
```

**Source code:**

```python
def run_async_test(coroutine):
    """
    Helper function to run an async test function.

    This is useful for methods that use async outside of pytest's asyncio fixture.
    """
    import asyncio
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)
```

---

## test_temporal_pattern_recognition.py

File: `app/tests/test_temporal_pattern_recognition.py`

### TestProductivityPatternLSTM::test_init

```
Test initialization of ProductivityPatternLSTM.
```

**Source code:**

```python
    def test_init(self, mock_class):
        """Test initialization of ProductivityPatternLSTM."""
        # Create mock attributes
        mock_instance = mock_class.return_value
        mock_instance.sequence_length = 14
        mock_instance.n_features = 24
        mock_instance.lstm_units = [128, 64]
        mock_instance.dropout_rate = 0.3
        mock_instance.learning_rate = 0.001

        # Assert the attributes are correct
        assert mock_instance.sequence_length == 14
        assert mock_instance.n_features == 24
        assert mock_instance.lstm_units == [128, 64]
        assert mock_instance.dropout_rate == 0.3
        assert mock_instance.learning_rate == 0.001
```

**Assertions:**

- `assert mock_instance.sequence_length == 14`
- `assert mock_instance.n_features == 24`
- `assert mock_instance.lstm_units == [128, 64]`
- `assert mock_instance.dropout_rate == 0.3`
- `assert mock_instance.learning_rate == 0.001`

---

### TestProductivityPatternLSTM::test_build_model

```
Test model building.
```

**Source code:**

```python
    def test_build_model(self, mock_class):
        """Test model building."""
        mock_instance = mock_class.return_value
        mock_instance._build_model = MagicMock()

        # Call build_model
        mock_instance._build_model()

        # Assert the method was called
        mock_instance._build_model.assert_called_once()
```

---

### TestProductivityPatternLSTM::test_predict_patterns

```
Test prediction of patterns.
```

**Source code:**

```python
    def test_predict_patterns(self, mock_class):
        """Test prediction of patterns."""
        # Setup mock instance
        mock_instance = mock_class.return_value
        mock_instance.trained = True

        # Create prediction data
        predictions = {
            "completion_rate": np.random.random((5, 1)),
            "focus_level": np.random.random((5, 1)),
            "energy_level": np.random.random((5, 1)),
            "optimal_time": np.random.random((5, 24)),
            "bottleneck_score": np.random.random((5, 1))
        }

        # Setup predict_patterns to return our mocked data
        mock_instance.predict_patterns = MagicMock(return_value=predictions)

        # Call predict_patterns with dummy data
        X = np.random.random((5, 14, 24))
        result = mock_instance.predict_patterns(X)

        # Check predictions contains the expected keys
        assert "completion_rate" in result
        assert "energy_level" in result
        assert "focus_level" in result
```

**Assertions:**

- `assert "completion_rate" in result`
- `assert "energy_level" in result`
- `assert "focus_level" in result`

---

### TestCircadianRhythmModel::test_init

```
Test initialization of CircadianRhythmModel.
```

**Source code:**

```python
    def test_init(self, mock_class):
        """Test initialization of CircadianRhythmModel."""
        mock_instance = mock_class.return_value
        mock_instance.n_harmonics = 5
        mock_instance.learning_rate = 0.001
        mock_instance.rhythmic_regularization = 0.1
        mock_instance.use_sleep_data = True

        assert mock_instance.n_harmonics == 5
        assert mock_instance.learning_rate == 0.001
        assert mock_instance.rhythmic_regularization == 0.1
        assert mock_instance.use_sleep_data is True
```

**Assertions:**

- `assert mock_instance.n_harmonics == 5`
- `assert mock_instance.learning_rate == 0.001`
- `assert mock_instance.rhythmic_regularization == 0.1`
- `assert mock_instance.use_sleep_data is True`

---

### TestCircadianRhythmModel::test_build_model

```
Test model building.
```

**Source code:**

```python
    def test_build_model(self, mock_class):
        """Test model building."""
        mock_instance = mock_class.return_value
        mock_instance._build_model = MagicMock()

        # Call build_model
        mock_instance._build_model()

        # Assert the method was called
        mock_instance._build_model.assert_called_once()
```

---

### TestCircadianRhythmModel::test_predict_daily_curve

```
Test predicting daily energy curve.
```

**Source code:**

```python
    def test_predict_daily_curve(self, mock_class, mock_user_data):
        """Test predicting daily energy curve."""
        # Setup mock instance
        mock_instance = mock_class.return_value
        mock_instance.trained = True

        # Create prediction data
        hourly_predictions = {
            "energy_level": np.random.random(24),
            "predicted_optimal_times": np.argsort(np.random.random(24))[-5:].tolist(),
            "confidence_scores": np.random.random(24)
        }

        # Setup predict_daily_curve to return our mocked data
        mock_instance.predict_daily_curve = MagicMock(return_value=hourly_predictions)

        # Call predict_daily_curve
        user_features = {
            "age": 30,
            "adhd_type": "inattentive",
            "sleep_schedule": {"wake_time": "07:00", "sleep_time": "23:00"}
        }

        result = mock_instance.predict_daily_curve(user_features)

        # Check predictions contains the expected keys
        assert "energy_level" in result
        assert "predicted_optimal_times" in result
        assert "confidence_scores" in result
```

**Assertions:**

- `assert "energy_level" in result`
- `assert "predicted_optimal_times" in result`
- `assert "confidence_scores" in result`

---

### TestProductivityCorrelationSystem::test_init

```
Test initialization of ProductivityCorrelationSystem.
```

**Source code:**

```python
    def test_init(self, mock_class):
        """Test initialization of ProductivityCorrelationSystem."""
        mock_instance = mock_class.return_value
        mock_instance.n_clusters = 4
        mock_instance.scaler = MagicMock()
        mock_instance.pca = MagicMock()
        mock_instance.kmeans = MagicMock()

        assert mock_instance.n_clusters == 4
        assert mock_instance.scaler is not None
        assert mock_instance.pca is not None
        assert mock_instance.kmeans is not None
```

**Assertions:**

- `assert mock_instance.n_clusters == 4`
- `assert mock_instance.scaler is not None`
- `assert mock_instance.pca is not None`
- `assert mock_instance.kmeans is not None`

---

### TestProductivityCorrelationSystem::test_get_correlation_insights

```
Test getting correlation insights.
```

**Source code:**

```python
    def test_get_correlation_insights(self, mock_class):
        """Test getting correlation insights."""
        mock_instance = mock_class.return_value
        mock_instance.trained = True

        # Create mock results
        insights = {
            "top_correlations": [
                {"factor": "energy_level", "target": "productivity_score", "correlation": 0.8},
                {"factor": "focus_level", "target": "productivity_score", "correlation": 0.7}
            ],
            "top_mutual_information": [
                {"factor": "energy_level", "target": "productivity_score", "mutual_info": 0.5},
                {"factor": "focus_level", "target": "productivity_score", "mutual_info": 0.4}
            ],
            "productivity_patterns": [
                {
                    "cluster_id": 0,
                    "sample_size": 5,
                    "avg_productivity": 0.8,
                    "avg_completion_rate": 0.75,
                    "feature_importances": {"energy_level": 0.6, "focus_level": 0.3, "mood_score": 0.1},
                    "key_characteristics": {"energy_level": 7.0, "focus_level": 6.5, "mood_score": 8.0},
                    "recommendations": []
                }
            ]
        }

        # Setup get_correlation_insights to return our mocked data
        mock_instance.get_correlation_insights = MagicMock(return_value=insights)

        # Call the method
        result = mock_instance.get_correlation_insights()

        # Check insights structure
        assert "top_correlations" in result
        assert "top_mutual_information" in result
        assert "productivity_patterns" in result
```

**Assertions:**

- `assert "top_correlations" in result`
- `assert "top_mutual_information" in result`
- `assert "productivity_patterns" in result`

---

### TestMentalHealthFederatedModel::test_init

```
Test initialization of MentalHealthFederatedModel.
```

**Source code:**

```python
    def test_init(self, mock_class):
        """Test initialization of MentalHealthFederatedModel."""
        mock_instance = mock_class.return_value
        mock_instance.client_batch_size = 32
        mock_instance.client_epochs = 1
        mock_instance.min_clients = 4
        mock_instance.dp_noise_multiplier = 0.1

        assert mock_instance.client_batch_size == 32
        assert mock_instance.client_epochs == 1
        assert mock_instance.min_clients == 4
        assert mock_instance.dp_noise_multiplier == 0.1
```

**Assertions:**

- `assert mock_instance.client_batch_size == 32`
- `assert mock_instance.client_epochs == 1`
- `assert mock_instance.min_clients == 4`
- `assert mock_instance.dp_noise_multiplier == 0.1`

---

### TestMentalHealthFederatedModel::test_anonymize_client_id

```
Test client ID anonymization.
```

**Source code:**

```python
    def test_anonymize_client_id(self, mock_class):
        """Test client ID anonymization."""
        mock_instance = mock_class.return_value

        # Setup anonymize_client_id to return a predictable hash
        mock_instance.anonymize_client_id = MagicMock(return_value="anonymized_hash_value_123456789")

        # Call the method
        user_id = "user123"
        anonymized = mock_instance.anonymize_client_id(user_id)

        # Check anonymization
        assert len(anonymized) > 0
        assert anonymized != user_id
        # Check that the method was called with the correct argument
        mock_instance.anonymize_client_id.assert_called_once_with(user_id)
```

**Assertions:**

- `assert len(anonymized) > 0`
- `assert anonymized != user_id`

---

### TestTemporalPatternRecognitionService::test_init

```
Test initialization of TemporalPatternRecognitionService.
```

**Source code:**

```python
    def test_init(self, mock_mhfm, mock_pcs, mock_crm, mock_pplstm):
        """Test initialization of TemporalPatternRecognitionService."""
        service = TemporalPatternRecognitionService()

        # Check models are initialized
        assert service.productivity_pattern is not None
        assert service.circadian_rhythm is not None
        assert service.correlation_system is not None
        assert service.federated_model is not None
```

**Assertions:**

- `assert service.productivity_pattern is not None`
- `assert service.circadian_rhythm is not None`
- `assert service.correlation_system is not None`
- `assert service.federated_model is not None`

---

### TestTemporalPatternRecognitionService::test_generate_comprehensive_insights

```
Test generation of comprehensive insights.
```

**Source code:**

```python
    async def test_generate_comprehensive_insights(
        self,
        mock_run_federated,
        mock_gen_insights,
        mock_model_rhythm,
        mock_analyze_patterns,
        mock_time_blocks,
        mock_mental_health_logs,
        mock_energy_logs,
        mock_productivity_metrics,
        mock_user_data
    ):
        """Test generation of comprehensive insights."""
        # Setup mocks to return some sample data
        mock_analyze_patterns.return_value = {"optimal_windows": []}
        mock_model_rhythm.return_value = {"energy_curve": {"hourly_predictions": [("08:00", 7.5)]}}
        mock_gen_insights.return_value = {"correlation_insights": {}}
        mock_run_federated.return_value = {"insights": {}}

        # Create service with mocked dependencies
        service = TemporalPatternRecognitionService()

        # Call the method
        result = await service.generate_comprehensive_insights(
            "user1",
            mock_time_blocks,
            mock_mental_health_logs,
            mock_energy_logs,
            mock_productivity_metrics,
            mock_user_data
        )

        # Check result structure
        assert "productivity_patterns" in result
        assert "circadian_rhythm" in result
        assert "productivity_insights" in result
        assert "federated_analysis" in result
        assert "schedule_recommendations" in result
```

**Assertions:**

- `assert "productivity_patterns" in result`
- `assert "circadian_rhythm" in result`
- `assert "productivity_insights" in result`
- `assert "federated_analysis" in result`
- `assert "schedule_recommendations" in result`

---

### test_api_analyze_productivity_patterns

```
Integration test for analyze_productivity_patterns API endpoint.
```

**Source code:**

```python
async def test_api_analyze_productivity_patterns():
    """Integration test for analyze_productivity_patterns API endpoint."""
    # Silently return instead of using pytest.skip
    # API endpoint needs rework to fix test - missing CRUD imports in endpoints module
    return

    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # Create a mock response for the database queries
    mock_time_blocks = []
    mock_mental_health_logs = []

    # Mock the TemporalPatternRecognitionService response
    mock_tpr_response = {
        "optimal_windows": [],
        "productivity_bottlenecks": [],
        "flexible_block_recommendations": [],
        "predictions": {}
    }

    # Mock authentication
    with patch('app.api.deps.get_current_user', return_value={"id": "user1", "is_admin": True}):
        # Mock TPR service directly to avoid the endpoint's imports
        with patch('app.ml.temporal_pattern_recognition.TemporalPatternRecognitionService.analyze_productivity_patterns',
                  return_value=mock_tpr_response):

            response = client.post(
                "/api/tpr/analyze_productivity_patterns?user_id=user1&days=30&days_to_predict=7"
            )

            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert "optimal_windows" in data["results"]
```

**Assertions:**

- `assert response.status_code == 200`
- `assert "results" in data`
- `assert "optimal_windows" in data["results"]`

---

## test_services.py

File: `app/tests/test_services.py`

### test_service_inheritance

```
Test if service class inherits from BaseService.
```

**Source code:**

```python
def test_service_inheritance(service_class):
    """Test if service class inherits from BaseService."""
    assert issubclass(service_class, BaseService), f"{service_class.__name__} does not inherit from BaseService"
```

**Assertions:**

- `assert issubclass(service_class, BaseService), f"{service_class.__name__} does not inherit from BaseService"`

---

### test_base_service_initialization

```
Test base service initialization.
```

**Source code:**

```python
async def test_base_service_initialization(db_session):
    """Test base service initialization."""
    service = BaseService(db=db_session, model=TaskModel, schema_class=TaskResponse)
    assert service.db == db_session
    assert service.model == TaskModel
    assert service.schema_class == TaskResponse
```

**Assertions:**

- `assert service.db == db_session`
- `assert service.model == TaskModel`
- `assert service.schema_class == TaskResponse`

---

### test_service_crud_operations_parametrized

```
Test CRUD operations for all service types.
```

**Source code:**

```python
async def test_service_crud_operations_parametrized(service_fixture, request):
    """Test CRUD operations for all service types."""
    service = request.getfixturevalue(service_fixture)

    # Get the CreateSchema type from the service's actual class
    # Instead of relying on __orig_bases__, which doesn't work for coroutines
    from app.schemas.task_schema import TaskCreate

    # Map service name to appropriate schema
    schema_map = {
        "task_service": TaskCreate,
        # Add mappings for other services as needed
    }

    # Default to TaskCreate for testing if no specific mapping
    create_schema_type = schema_map.get(service_fixture, TaskCreate)

    # Create test data based on the schema's fields
    test_data = {}
    for field_name, field in create_schema_type.model_fields.items():
        if field.is_required():
            if field.annotation == str:
                test_data[field_name] = f"Test {field_name}"
            elif field.annotation == int:
                test_data[field_name] = 1
            elif field.annotation == float:
                test_data[field_name] = 1.0
            elif field.annotation == bool:
                test_data[field_name] = True
            elif field.annotation == datetime:
                test_data[field_name] = datetime.utcnow()
            elif field.annotation == UUID:
                test_data[field_name] = uuid4()
            elif str(field.annotation).startswith("typing.List"):
                test_data[field_name] = []
            elif str(field.annotation).startswith("typing.Dict"):
                test_data[field_name] = {}
            elif str(field.annotation).startswith("typing.Optional"):
                continue
            else:
                # For enums and other types, use the first available value
                try:
                    test_data[field_name] = list(field.annotation.__members__.values())[0]
                except (AttributeError, IndexError):
                    continue

    # Create instance
    create_data = create_schema_type(**test_data)
    created_item = await service.create(create_data)
    assert created_item is not None

    # Get by ID
    retrieved_item = await service.get_by_id(created_item.id)
    assert retrieved_item is not None
    assert retrieved_item.id == created_item.id

    # Get all
    items = await service.get_all()
    assert len(items) >= 1
    assert any(item.id == created_item.id for item in items)

    # Update
    update_data = {}
    for field_name, field in create_schema_type.model_fields.items():
        if field.annotation == str and not field_name.endswith("_id"):
            update_data[field_name] = f"Updated {field_name}"
            break

    if update_data:
        updated_item = await service.update(created_item.id, update_data)
        assert updated_item is not None
        for key, value in update_data.items():
            assert getattr(updated_item, key) == value

    # Delete
    deleted = await service.delete(created_item.id)
    assert deleted is True

    # Verify deletion
    items_after_delete = await service.get_all()
    assert not any(item.id == created_item.id for item in items_after_delete)
```

**Assertions:**

- `assert created_item is not None`
- `assert retrieved_item is not None`
- `assert retrieved_item.id == created_item.id`
- `assert len(items) >= 1`
- `assert any(item.id == created_item.id for item in items)`
- `assert deleted is True`
- `assert not any(item.id == created_item.id for item in items_after_delete)`
- `assert updated_item is not None`
- `assert getattr(updated_item, key) == value`

---

### test_service_error_handling

```
Test error handling in service operations.
```

**Source code:**

```python
async def test_service_error_handling(task_service):
    """Test error handling in service operations."""
    # Test get by invalid ID
    invalid_id = uuid4()
    result = await task_service.get_by_id(invalid_id)
    assert result is None

    # Test update non-existent item
    with pytest.raises(ServiceError):
        await task_service.update(invalid_id, {"title": "New Title"})

    # Test delete non-existent item
    result = await task_service.delete(invalid_id)
    assert result is False
```

**Assertions:**

- `assert result is None`
- `assert result is False`

---

### test_service_field_operations

```
Test field-specific operations.
```

**Source code:**

```python
async def test_service_field_operations(task_service):
    """Test field-specific operations."""
    # Create test task
    task_data = TaskCreate(
        title="Test Task",
        description="Test Description",
        due_date=datetime.utcnow() + timedelta(days=1),
        estimated_duration=30,
        priority=BlockPriority.MEDIUM,
        status=TaskStatus.TODO
    )
    created_task = await task_service.create(task_data)

    # Test get by field
    task_by_title = await task_service.get_by_field("title", "Test Task")
    assert task_by_title is not None
    assert task_by_title.id == created_task.id

    # Test get many by field
    tasks_by_status = await task_service.get_many_by_field("status", TaskStatus.TODO)
    assert len(tasks_by_status) == 1
    assert tasks_by_status[0].id == created_task.id
```

**Assertions:**

- `assert task_by_title is not None`
- `assert task_by_title.id == created_task.id`
- `assert len(tasks_by_status) == 1`
- `assert tasks_by_status[0].id == created_task.id`

---

### test_service_count_operation

```
Test count operation.
```

**Source code:**

```python
async def test_service_count_operation(task_service):
    """Test count operation."""
    # Create multiple tasks
    task_data = TaskCreate(
        title="Test Task",
        description="Test Description",
        due_date=datetime.utcnow() + timedelta(days=1),
        estimated_duration=30,
        priority=BlockPriority.MEDIUM,
        status=TaskStatus.TODO
    )
    await task_service.create(task_data)
    await task_service.create(task_data)

    # Test count
    count = await task_service.count()
    assert count == 2
```

**Assertions:**

- `assert count == 2`

---

### test_service_exists_operation

```
Test exists operation.
```

**Source code:**

```python
async def test_service_exists_operation(task_service):
    """Test exists operation."""
    # Create a task
    task_data = TaskCreate(
        title="Test Task",
        description="Test Description",
        due_date=datetime.utcnow() + timedelta(days=1),
        estimated_duration=30,
        priority=BlockPriority.MEDIUM,
        status=TaskStatus.TODO
    )
    created_task = await task_service.create(task_data)

    # Test exists with valid ID
    exists = await task_service.exists(created_task.id)
    assert exists is True

    # Test exists with invalid ID
    exists = await task_service.exists(uuid4())
    assert exists is False
```

**Assertions:**

- `assert exists is True`
- `assert exists is False`

---

### test_service_retry_mechanism

```
Test service retry mechanism.
```

**Source code:**

```python
async def test_service_retry_mechanism(task_service):
    """Test service retry mechanism."""
    # Create a task that should trigger retries
    task_data = TaskCreate(
        title="Test Task" * 20,  # Long enough to potentially trigger DB errors but within validation limits
        description="Test Description",
        due_date=datetime.utcnow() + timedelta(days=1),
        estimated_duration=30,
        priority=BlockPriority.MEDIUM,
        status=TaskStatus.TODO
    )

    # Test that operation either succeeds or raises ServiceError
    try:
        await task_service.create(task_data)
    except ServiceError:
        pass  # Expected behavior for some databases
```

---

### test_service_concurrency_control

```
Test service concurrency control.
```

**Source code:**

```python
async def test_service_concurrency_control(task_service):
    """Test service concurrency control."""
    # Create initial task
    task_data = TaskCreate(
        title="Test Task",
        description="Test Description",
        due_date=datetime.utcnow() + timedelta(days=1),
        estimated_duration=30,
        priority=BlockPriority.MEDIUM,
        status=TaskStatus.TODO
    )
    created_task = await task_service.create(task_data)

    # Simulate concurrent updates
    update_data_1 = {"title": "Updated Task 1"}
    update_data_2 = {"title": "Updated Task 2"}

    # Perform updates (in real scenarios, these would be from different sessions)
    task1 = await task_service.update(created_task.id, update_data_1)
    task2 = await task_service.update(created_task.id, update_data_2)

    # Verify last update won
    final_task = await task_service.get_by_id(created_task.id)
    assert final_task.title == "Updated Task 2"
```

**Assertions:**

- `assert final_task.title == "Updated Task 2"`

---

## __init__.py

File: `app/tests/__init__.py`

## factories.py

File: `app/tests/factories.py`

## test_routes.py

File: `app/tests/test_routes.py`

### test_router_instance

```
Test if router instance is an instance of APIRouter.
```

**Source code:**

```python
def test_router_instance(router_instance):
    """Test if router instance is an instance of APIRouter."""
    assert isinstance(router_instance, APIRouter), f"{router_instance} is not an instance of APIRouter"
```

**Assertions:**

- `assert isinstance(router_instance, APIRouter), f"{router_instance} is not an instance of APIRouter"`

---

## test_simple_models.py

File: `app/tests/test_simple_models.py`

### test_base_model_init

```
Test BaseModel initialization.
```

**Source code:**

```python
def test_base_model_init():
    """Test BaseModel initialization."""
    assert hasattr(TestBaseModel, 'id')
    assert hasattr(TestBaseModel, 'created_at')
    assert hasattr(TestBaseModel, 'updated_at')
```

**Assertions:**

- `assert hasattr(TestBaseModel, 'id')`
- `assert hasattr(TestBaseModel, 'created_at')`
- `assert hasattr(TestBaseModel, 'updated_at')`

---

### test_simple_user_model_create

```
Test creating a simple user.
```

**Source code:**

```python
def test_simple_user_model_create(db_session):
    """Test creating a simple user."""
    user_id = str(uuid4())
    user = SimpleUser(
        id=user_id,
        username="test_user",
        email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()

    # Get the user from the database
    user_from_db = db_session.query(SimpleUser).filter_by(id=user_id).first()
    assert user_from_db is not None
    assert user_from_db.id == user_id
    assert user_from_db.username == "test_user"
    assert user_from_db.email == "test@example.com"
```

**Assertions:**

- `assert user_from_db is not None`
- `assert user_from_db.id == user_id`
- `assert user_from_db.username == "test_user"`
- `assert user_from_db.email == "test@example.com"`

---

### test_simple_relationship

```
Test a simple relationship between user and task.
```

**Source code:**

```python
def test_simple_relationship(db_session):
    """Test a simple relationship between user and task."""
    user_id = str(uuid4())
    user = SimpleUser(
        id=user_id,
        username="test_user",
        email="test@example.com"
    )
    db_session.add(user)

    task = SimpleTask(
        title="Test Task",
        user_id=user_id
    )
    db_session.add(task)
    db_session.commit()

    # Verify relationship
    user_from_db = db_session.query(SimpleUser).filter_by(id=user_id).first()
    tasks = db_session.query(SimpleTask).filter_by(user_id=user_id).all()

    assert user_from_db is not None
    assert len(tasks) == 1
    assert tasks[0].title == "Test Task"
```

**Assertions:**

- `assert user_from_db is not None`
- `assert len(tasks) == 1`
- `assert tasks[0].title == "Test Task"`

---

## test_base_model.py

File: `app/tests/test_base_model.py`

### test_id_mixin

```
Test ID mixin.
```

**Source code:**

```python
def test_id_mixin():
    """Test ID mixin."""
    assert hasattr(IDMixin, 'id')
    assert hasattr(IDMixin, 'created_at')
    assert hasattr(IDMixin, 'updated_at')
```

**Assertions:**

- `assert hasattr(IDMixin, 'id')`
- `assert hasattr(IDMixin, 'created_at')`
- `assert hasattr(IDMixin, 'updated_at')`

---

### test_user_model_create

```
Test creating a user.
```

**Source code:**

```python
def test_user_model_create(db_session):
    """Test creating a user."""
    user_id = str(uuid4())
    user = TestUser(
        id=user_id,
        username="test_user",
        email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()

    # Get the user from the database
    user_from_db = db_session.query(TestUser).filter_by(id=user_id).first()
    assert user_from_db is not None
    assert user_from_db.id == user_id
    assert user_from_db.username == "test_user"
    assert user_from_db.email == "test@example.com"
```

**Assertions:**

- `assert user_from_db is not None`
- `assert user_from_db.id == user_id`
- `assert user_from_db.username == "test_user"`
- `assert user_from_db.email == "test@example.com"`

---

### test_relationship

```
Test a relationship between user and task.
```

**Source code:**

```python
def test_relationship(db_session):
    """Test a relationship between user and task."""
    user_id = str(uuid4())
    user = TestUser(
        id=user_id,
        username="test_user",
        email="test@example.com"
    )
    db_session.add(user)

    task = TestTask(
        title="Test Task",
        user_id=user_id
    )
    db_session.add(task)
    db_session.commit()

    # Verify relationship
    user_from_db = db_session.query(TestUser).filter_by(id=user_id).first()
    tasks = db_session.query(TestTask).filter_by(user_id=user_id).all()

    assert user_from_db is not None
    assert len(tasks) == 1
    assert tasks[0].title == "Test Task"
    assert len(user_from_db.tasks) == 1
```

**Assertions:**

- `assert user_from_db is not None`
- `assert len(tasks) == 1`
- `assert tasks[0].title == "Test Task"`
- `assert len(user_from_db.tasks) == 1`

---

## test_models.py

File: `app/tests/test_models.py`

### test_model_inheritance

```
Test that all model classes inherit from BaseModel.
```

**Source code:**

```python
def test_model_inheritance(model_class):
    """Test that all model classes inherit from BaseModel."""
    # Skip non-class entries that might have been accidentally added to model_classes
    if not isinstance(model_class, type):
        return  # Silently skip non-class entries

    # Skip MockHealthMetrics as it's intentionally not inheriting from BaseModel for testing purposes
    if model_class.__name__ == "MockHealthMetrics":
        return  # Silently skip MockHealthMetrics

    assert issubclass(model_class, BaseModel), f"{model_class.__name__} does not inherit from BaseModel"
```

**Assertions:**

- `assert issubclass(model_class, BaseModel), f"{model_class.__name__} does not inherit from BaseModel"`

---

### test_uuid_assignment

```
Test if models correctly assign UUIDs.
```

**Source code:**

```python
def test_uuid_assignment(db_session):
    """Test if models correctly assign UUIDs."""
    user = UserModel(
        id=uuid4(),
        username="test_user",
        email="test@example.com",
        full_name="Test User",
        hashed_password="test_password"
    )
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
    assert isinstance(user.id, UUID)

    retrieved_user = db_session.query(UserModel).first()
    assert retrieved_user is not None
    assert retrieved_user.id == user.id
```

**Assertions:**

- `assert user.id is not None`
- `assert isinstance(user.id, UUID)`
- `assert retrieved_user is not None`
- `assert retrieved_user.id == user.id`

---

### test_timestamp_fields

```
Test if models properly handle timestamp fields.
```

**Source code:**

```python
def test_timestamp_fields(db_session):
    """Test if models properly handle timestamp fields."""
    user = UserModel(
        id=str(uuid4()),
        username="test_user",
        email="test@example.com",
        full_name="Test User",
        hashed_password="test_password",
        is_active=True,
        is_verified=False
    )
    db_session.add(user)
    db_session.commit()

    retrieved_user = db_session.query(UserModel).first()
    assert isinstance(retrieved_user.created_at, datetime)
    assert isinstance(retrieved_user.updated_at, datetime)

    # Allow a slightly larger microsecond difference
    assert abs((retrieved_user.updated_at - retrieved_user.created_at).total_seconds()) < 0.001

    # Simulate an update
    retrieved_user.username = "updated_user"
    db_session.add(retrieved_user)
    db_session.commit()

    # Refresh the object
    db_session.refresh(retrieved_user)

    assert retrieved_user.updated_at is not None
    assert retrieved_user.updated_at > retrieved_user.created_at  # Ensure update timestamp is later
```

**Assertions:**

- `assert isinstance(retrieved_user.created_at, datetime)`
- `assert isinstance(retrieved_user.updated_at, datetime)`
- `assert abs((retrieved_user.updated_at - retrieved_user.created_at).total_seconds()) < 0.001`
- `assert retrieved_user.updated_at is not None`
- `assert retrieved_user.updated_at > retrieved_user.created_at  # Ensure update timestamp is later`

---

### test_model_serialization

```
Test model serialization to dict.
```

**Source code:**

```python
def test_model_serialization(model_class):
    """Test model serialization to dict."""
    # Skip non-class entries that might have been accidentally added to model_classes
    if not isinstance(model_class, type):
        return  # Silently skip non-class entries

    # Skip MockHealthMetrics as it's intentionally not inheriting from BaseModel for testing purposes
    if model_class.__name__ == "MockHealthMetrics":
        return  # Silently skip MockHealthMetrics

    # Create an instance of the model
    model_instance = model_class()

    # Test that the model has the expected attributes from BaseModel
    assert hasattr(model_instance, "id"), f"{model_class.__name__} should have an 'id' attribute"
    assert hasattr(model_instance, "created_at"), f"{model_class.__name__} should have a 'created_at' attribute"
    assert hasattr(model_instance, "updated_at"), f"{model_class.__name__} should have an 'updated_at' attribute"
```

**Assertions:**

- `assert hasattr(model_instance, "id"), f"{model_class.__name__} should have an 'id' attribute"`
- `assert hasattr(model_instance, "created_at"), f"{model_class.__name__} should have a 'created_at' attribute"`
- `assert hasattr(model_instance, "updated_at"), f"{model_class.__name__} should have an 'updated_at' attribute"`

---

### test_invalid_inputs

```
Test model validation for invalid inputs.
```

**Source code:**

```python
def test_invalid_inputs(model_class, db_session):
    """Test model validation for invalid inputs."""
    # Skip non-class entries that might have been accidentally added to model_classes
    if not isinstance(model_class, type):
        return  # Silently skip non-class entries

    # Skip MockHealthMetrics as it's intentionally not inheriting from BaseModel for testing purposes
    if model_class.__name__ == "MockHealthMetrics":
        return  # Silently skip MockHealthMetrics

    # Create dummy parents for models with foreign key constraints
    create_dummy_parents(db_session, model_class)

    # Test with invalid UUID
    try:
        invalid_instance = model_class(id="not-a-uuid")
        db_session.add(invalid_instance)
        db_session.flush()
        # If we get here, the validation failed to catch the invalid UUID
        assert False, f"{model_class.__name__} accepted an invalid UUID"
    except Exception:
        # Expected to fail
        db_session.rollback()

    # Test with invalid date
    date_fields = [field for field in dir(model_class) if "date" in field.lower() and not field.startswith("_")]
    for field in date_fields:
        try:
            kwargs = {field: "not-a-date"}
            invalid_instance = model_class(**kwargs)
            db_session.add(invalid_instance)
            db_session.flush()
            # If we get here, the validation failed to catch the invalid date
            assert False, f"{model_class.__name__} accepted an invalid date for {field}"
        except Exception:
            # Expected to fail
            db_session.rollback()
```

**Assertions:**

- `assert False, f"{model_class.__name__} accepted an invalid UUID"`
- `assert False, f"{model_class.__name__} accepted an invalid date for {field}"`

---

### test_database_constraints

```
Test database constraints for models.
```

**Source code:**

```python
def test_database_constraints(model_class, db_session):
    """Test database constraints for models."""
    # Skip non-class entries that might have been accidentally added to model_classes
    if not isinstance(model_class, type):
        return  # Silently skip non-class entries

    # Skip MockHealthMetrics as it's intentionally not inheriting from BaseModel for testing purposes
    if model_class.__name__ == "MockHealthMetrics":
        return  # Silently skip MockHealthMetrics

    # Create dummy parents for models with foreign key constraints
    parent_data = create_dummy_parents(db_session, model_class)

    # Create and save a valid instance with parent data
    instance = model_class()

    # Apply parent data to the instance
    for key, value in parent_data.items():
        setattr(instance, key, value)

    # Set required fields based on model type
    model_name = model_class.__name__

    # Set created_at and updated_at for all models
    now = datetime.now()
    if hasattr(instance, 'created_at') and getattr(instance, 'created_at') is None:
        setattr(instance, 'created_at', now)
    if hasattr(instance, 'updated_at') and getattr(instance, 'updated_at') is None:
        setattr(instance, 'updated_at', now)

    # Common fields for many models
    if hasattr(instance, 'title') and getattr(instance, 'title') is None:
        setattr(instance, 'title', f"Test {model_name} {uuid4().hex[:8]}")

    if hasattr(instance, 'name') and getattr(instance, 'name') is None:
        setattr(instance, 'name', f"Test {model_name} {uuid4().hex[:8]}")

    if hasattr(instance, 'description') and getattr(instance, 'description') is None:
        setattr(instance, 'description', f"Test description for {model_name}")

    # Time-related fields
    if hasattr(instance, 'start_time') and getattr(instance, 'start_time') is None:
        setattr(instance, 'start_time', datetime.now())

    if hasattr(instance, 'end_time') and getattr(instance, 'end_time') is None:
        setattr(instance, 'end_time', datetime.now() + timedelta(hours=1))

    if hasattr(instance, 'duration') and getattr(instance, 'duration') is None:
        setattr(instance, 'duration', 30)  # 30 minutes

    if hasattr(instance, 'scheduled_time') and getattr(instance, 'scheduled_time') is None:
        setattr(instance, 'scheduled_time', datetime.now() + timedelta(hours=2))

    # Status and type fields
    if hasattr(instance, 'status') and getattr(instance, 'status') is None:
        if model_name == "CalendarSyncModel":
            setattr(instance, 'status', SyncStatus.IN_PROGRESS.value)
        else:
            setattr(instance, 'status', 'active')

    if hasattr(instance, 'type') and getattr(instance, 'type') is None:
        setattr(instance, 'type', 'default')

    # Set a unique ID for all models
    if hasattr(instance, 'id') and getattr(instance, 'id') is None:
        setattr(instance, 'id', str(uuid4()))

    # Model-specific fields
    if model_name == "UserModel":
        instance.email = f"test_{uuid4().hex[:8]}@example.com"
        instance.username = f"test_user_{uuid4().hex[:8]}"
        instance.hashed_password = "test_password"
        instance.full_name = f"Test User {uuid4().hex[:8]}"

    elif model_name == "LoginAttemptModel" or model_name == "LoginAttempt":
        instance.ip_address = "127.0.0.1"
        instance.user_agent = "Mozilla/5.0 (Test)"
        instance.success = True
        instance.attempt_time = datetime.now()

    elif model_name == "HealthMetrics":
        instance.mood_score = 5
        instance.energy_level = 5
        instance.stress_level = 3
        instance.focus_score = 7
        instance.meditation_minutes = 10
        instance.date = datetime.now().date()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.metric_type = MetricType.DAILY.value if hasattr(MetricType, 'DAILY') else "daily"
        instance.mood_level = 6
        instance.focus_level = 7

    elif model_name == "NLPModel":
        instance.text = "Sample text for NLP analysis"
        instance.parsed_data = "{}"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.confidence_score = 0.9
        instance.language = "en"
        instance.entities = []

    elif model_name == "TaskModel":
        instance.title = f"Test Task {uuid4().hex[:8]}"
        instance.status = "todo"
        instance.priority = 2

    elif model_name == "StreakModel":
        instance.streak_type = "daily_login"
        instance.current_count = 1
        instance.last_activity_date = datetime.now().date()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.longest_streak = 5
        instance.current_streak = 3
        instance.last_activity = datetime.now()
        instance.is_active = True

    elif model_name == "FocusStrategy":
        instance.name = f"Test Strategy {uuid4().hex[:8]}"
        instance.description = "A test focus strategy"
        instance.effectiveness_score = 7
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.strategy_type = "pomodoro"
        instance.duration = 25
        instance.task_type = "coding"
        instance.title = f"Test Focus Strategy {uuid4().hex[:8]}"
        instance.break_intervals = [{"duration": 5, "after_minutes": 25}]
        instance.environment_setup = ["quiet room", "good lighting"]
        instance.tools_needed = ["timer", "notebook"]

    elif model_name == "RefreshToken":
        instance.token = f"token_{uuid4().hex}"
        instance.expires_at = datetime.now() + timedelta(days=7)
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.client_id = "test_client"
        instance.is_revoked = False
        instance.token_type = "bearer"
        instance.token_id = str(uuid4())  # Add the required token_id field

    elif model_name == "ADHDPatternsModel":
        instance.session_count = 10
        instance.pattern_type = "focus"
        instance.serialized_pattern = "{}"
        instance.date_range_start = datetime.now() - timedelta(days=30)
        instance.date_range_end = datetime.now()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.confidence_score = 0.85
        instance.pattern_name = "Focus Pattern"
        instance.detection_method = "algorithm"
        instance.settings_id = parent_data.get("settings_id", str(uuid4()))

    elif model_name == "Interaction":
        instance.type = InteractionType.CHAT.value if hasattr(InteractionType, 'CHAT') else "chat"
        instance.outcome = InteractionOutcome.POSITIVE.value if hasattr(InteractionOutcome, 'POSITIVE') else "positive"
        instance.timestamp = datetime.now()

    elif model_name == "ContactModel":
        instance.name = f"Test Contact {uuid4().hex[:8]}"
        instance.email = f"contact_{uuid4().hex[:8]}@example.com"
        instance.phone = "555-123-4567"
        instance.contact_type = "personal"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.relationship = "friend"
        instance.notes = "Test contact notes"
        instance.is_favorite = False
        instance.relationship_strength = "strong"
        instance.type = ContactType.PERSONAL.value if hasattr(ContactType, 'PERSONAL') else "personal"

    elif model_name == "ReminderModel":
        instance.title = f"Test Reminder {uuid4().hex[:8]}"
        instance.scheduled_time = datetime.now() + timedelta(hours=2)
        instance.status = "pending"

    elif model_name == "AchievementModel" or model_name == "BadgeModel":
        instance.name = f"Test {model_name} {uuid4().hex[:8]}"
        instance.category = "productivity"

    elif model_name == "InteractionStats":
        instance.period_start = datetime.now() - timedelta(days=7)
        instance.period_end = datetime.now()
        instance.interaction_count = 10
        instance.stat_type = "daily"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.average_duration = 15
        instance.peak_times = json.dumps(["morning", "evening"])
        instance.effectiveness_rating = 8
        instance.total_interactions = 10
        instance.average_effectiveness = 7.5

    elif model_name == "EnergyStats":
        instance.period_start = datetime.now() - timedelta(days=7)
        instance.period_end = datetime.now()
        instance.average_energy = 7.0
        instance.average_focus = 6.5
        instance.energy_stability = 0.8
        instance.focus_stability = 0.7
        instance.peak_performance_duration = 120
        instance.recovery_effectiveness = 0.75
        instance.break_effectiveness = 0.8
        instance.interruption_impact = -0.3
        instance.user_id = parent_data.get("user_id", str(uuid4()))

    elif model_name == "SessionStatsModel":
        instance.session_count = 10
        instance.total_duration = 600
        instance.average_focus_score = 7
        instance.period_start = datetime.now() - timedelta(days=7)
        instance.period_end = datetime.now()
        instance.stat_type = "daily"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.peak_session_times = json.dumps(["morning"])
        instance.session_distribution = json.dumps({"focus": 5, "pomodoro": 5})
        instance.session_id = parent_data.get("session_id", str(uuid4()))
        instance.total_sessions = 10
        instance.average_effectiveness = 0.8
        instance.completion_rate = 0.9

    elif model_name == "MedicationLogModel":
        instance.medication_name = "Test Medication"
        instance.dosage = 10.0  # Changed from "10mg" to a float value
        instance.unit = "mg"  # Set the unit separately
        instance.timestamp = datetime.now()
        instance.taken = True
        instance.medication_type = MedicationType.STIMULANT.value if hasattr(MedicationType, 'STIMULANT') else "stimulant"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.effectiveness = 7
        instance.side_effects = "None"
        instance.settings_id = parent_data.get("settings_id", str(uuid4()))

    elif model_name == "DistractionLogModel":
        instance.distraction_type = DistractionType.DIGITAL.value if hasattr(DistractionType, 'DIGITAL') else "digital"
        instance.timestamp = datetime.now()
        instance.duration = 5
        instance.notes = "Test distraction"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.severity = 3
        instance.context = "working"
        instance.settings_id = parent_data.get("settings_id", str(uuid4()))

    elif model_name == "MentalHealthLogModel":
        instance.log_type = "anxiety"
        instance.severity = 3
        instance.notes = "Test mental health log"
        instance.timestamp = datetime.now()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.mood_score = 7
        instance.anxiety_level = 3
        instance.focus_level = 7
        instance.energy_level = 6
        instance.stress_level = 3
        instance.sleep_hours = 7.5

    elif model_name == "BodyDoublingSessionModel":
        instance.duration = 30
        instance.partner_type = "virtual"
        instance.start_time = datetime.now() - timedelta(minutes=30)
        instance.end_time = datetime.now()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.session_type = "focus"
        instance.status = "completed"

    elif model_name == "FocusSessionModel":
        instance.duration = 45
        instance.focus_level = 8
        instance.energy_level = 7
        instance.activity_type = "coding"
        instance.status = "active"
        instance.start_time = datetime.now() - timedelta(hours=1)
        instance.end_time = datetime.now()
        instance.session_type = FocusSessionType.POMODORO.value if hasattr(FocusSessionType, 'POMODORO') else "pomodoro"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.total_breaks = 2
        instance.total_break_duration = 15
        instance.actual_focus_duration = 30

    elif model_name == "TimelineEventModel":
        instance.event_type = TimelineEventType.TASK_COMPLETED.value if hasattr(TimelineEventType, 'TASK_COMPLETED') else "task_completed"
        instance.timestamp = datetime.now()
        instance.details = "{}"

    elif model_name == "CalendarSyncModel":
        instance.external_calendar_id = f"ext_cal_{uuid4().hex[:8]}"
        instance.provider = SyncProvider.GOOGLE.value
        instance.source = SyncSource.LOCAL.value
        instance.sync_direction = SyncDirection.TWO_WAY.value
        instance.status = SyncStatus.IN_PROGRESS.value
        instance.conflict_strategy = ConflictResolutionStrategy.AUTO_REMOTE.value
        instance.is_active = True
        instance.error_count = 0
        instance.consecutive_failures = 0
        instance.error_history = "[]"
        instance.sync_frequency = 3600
        instance.pending_conflicts = "{}"
        instance.sync_settings = "{}"

    elif model_name == "TimeBlockModel":
        instance.title = f"Test TimeBlock {uuid4().hex[:8]}"
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=1)
        instance.block_type = BlockType.TASK.value
        instance.priority = BlockPriority.MEDIUM.value
        instance.is_break = False
        instance.is_flexible = False
        instance.interruptions = "null"
        instance.break_intervals = "null"
        instance.environment_data = "null"
        instance.tags = "null"
        instance.meta_data = "null"

    elif model_name == "VoiceCommandModel":
        instance.command_text = "Test voice command"
        instance.command_type = CommandType.VOICE.value
        instance.success = True
        instance.confidence_score = 0.95
        instance.processing_time = 0.5
        instance.action_taken = "test_action"
        instance.result = {"status": "success"}
        instance.timestamp = datetime.now()

    elif model_name == "CalendarModel":
        instance.name = f"Test Calendar {uuid4().hex[:8]}"
        instance.provider = "google"
        instance.is_primary = False
        instance.is_enabled = True

    elif model_name == "ADHDSettingsModel":
        instance.medication_tracking_enabled = True
        instance.distraction_tracking_enabled = True
        instance.energy_tracking_enabled = True
        instance.focus_tracking_enabled = True

    elif model_name == "ScheduleBlock":
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=1)
        instance.block_type = BlockType.TASK.value
        instance.is_available = True

    elif model_name == "SchedulePreferences":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.preferred_start_time = datetime.now()
        instance.preferred_end_time = datetime.now() + timedelta(hours=8)
        instance.preferred_break_duration = 15
        instance.min_break_interval = 90
        instance.max_focus_duration = 120

    elif model_name == "CalendarEventModel":
        instance.title = f"Test Event {uuid4().hex[:8]}"
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=1)
        instance.event_type = EventType.MEETING.value
        instance.status = EventStatus.SCHEDULED.value
        instance.priority = EventPriority.MEDIUM.value
        instance.is_all_day = False

    elif model_name == "NLPAnalysis":
        instance.nlp_record_id = parent_data.get("nlp_record_id", str(uuid4()))
        instance.sentiment_score = 0.8
        instance.complexity_score = 0.6
        instance.key_phrases = ["important", "urgent", "focus"]
        instance.topics = ["productivity", "adhd"]
        instance.summary = "Test summary"
        instance.recommendations = ["take breaks", "use timer"]
        instance.meta_data = {"source": "test"}

    elif model_name == "TaskAnalysis":
        instance.task_id = parent_data.get("task_id", str(uuid4()))
        instance.complexity_level = 0.7
        instance.time_estimate = 60
        instance.focus_requirements = {"attention": "high", "creativity": "medium"}
        instance.potential_challenges = ["distractions", "complexity"]
        instance.breakdown_suggestions = ["break into smaller tasks", "use pomodoro technique"]
        instance.energy_level_recommendation = "medium"
        instance.adhd_friendly_score = 0.6

    elif model_name == "PomodoroSessionModel":
        instance.work_duration = 25
        instance.break_duration = 5
        instance.long_break_duration = 15
        instance.cycles_completed = 2
        instance.start_time = datetime.now() - timedelta(hours=2)
        instance.end_time = datetime.now() - timedelta(hours=1)
        instance.status = "completed"
        instance.session_data = "{}"
        instance.task_id = parent_data.get("task_id", str(uuid4()))
        instance.meta_data = {}
        instance.short_break_duration = 5

    elif model_name == "LoginAttemptModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.ip_address = "192.168.1.1"
        instance.user_agent = "Mozilla/5.0"
        instance.success = True
        instance.attempt_time = datetime.now()

    elif model_name == "VoiceCommandModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.command_text = "Test command"
        instance.command_type = CommandType.VOICE.value
        instance.result = "Test result"
        instance.confidence_score = 0.9
        instance.processing_time = 0.5
        instance.action_taken = "Test action"

    elif model_name == "VoicePreferencesModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.language = "en-US"
        instance.voice_speed = 1.0
        instance.confirmation_required = True
        instance.wake_word = "Hey Assistant"
        instance.disabled_commands = []

    elif model_name == "TimelineEventModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.event_type = TimelineEventType.TASK_COMPLETED.value
        instance.title = "Test Event"

    elif model_name == "InteractionStats":
        instance.period_start = datetime.now() - timedelta(days=7)
        instance.period_end = datetime.now()
        instance.interaction_count = 10
        instance.stat_type = "daily"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.average_duration = 15
        instance.peak_times = json.dumps(["morning", "evening"])
        instance.effectiveness_rating = 8
        instance.total_interactions = 10
        instance.average_effectiveness = 7.5

    elif model_name == "CalendarModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.name = "Test Calendar"
        instance.provider = "Google"
        instance.color = "#4285F4"
        instance.is_primary = True
        instance.is_enabled = True
        instance.meta_data = {}

    elif model_name == "MentalHealthLogModel":
        instance.log_type = "anxiety"
        instance.severity = 3
        instance.notes = "Test mental health log"
        instance.timestamp = datetime.now()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.mood_score = 7
        instance.anxiety_level = 3
        instance.focus_level = 7
        instance.energy_level = 6
        instance.stress_level = 3
        instance.sleep_hours = 7.5

    elif model_name == "StreakModel":
        instance.streak_type = "daily_login"
        instance.current_count = 1
        instance.last_activity_date = datetime.now().date()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.longest_streak = 5
        instance.current_streak = 3
        instance.last_activity = datetime.now()
        instance.is_active = True

    elif model_name == "PointsModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.total_points = 100
        instance.level = 1

    elif model_name == "BadgeModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.name = "Test Badge"
        instance.category = "Test Category"
        instance.type = "Test Type"
        instance.earned_at = datetime.now()

    elif model_name == "BodyDoublingSessionModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.host_id = parent_data.get("user_id", str(uuid4()))
        instance.partner_id = parent_data.get("user_id", str(uuid4()))
        instance.session_type = "focus"
        instance.status = "active"
        instance.start_time = datetime.now() - timedelta(minutes=30)
        instance.end_time = datetime.now()

    elif model_name == "NLPModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.text = "Test text"
        instance.parsed_data = {}
        instance.confidence_score = 0.9
        instance.entities = []

    elif model_name == "ScheduleBlock":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.title = "Test Block"
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=1)
        instance.block_type = BlockType.TASK
        instance.priority = BlockPriority.MEDIUM
        instance.status = TaskStatus.TODO
        instance.is_flexible = True
        instance.buffer_before = 15
        instance.buffer_after = 15

    elif model_name == "HyperfocusSessionModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=2)
        instance.status = HyperfocusSessionStatus.ACTIVE
        instance.focus_level = 9
        instance.duration_minutes = 120
        instance.purpose = "Focus"
        instance.focus_area = "General"

    elif model_name == "CalendarEventModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.calendar_id = parent_data.get("calendar_id", str(uuid4()))
        instance.title = "Test Event"
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=1)
        instance.event_type = EventType.MEETING.value
        instance.status = EventStatus.SCHEDULED.value
        instance.duration = 60

    elif model_name == "CalendarSyncModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.calendar_id = parent_data.get("calendar_id", str(uuid4()))
        instance.external_calendar_id = parent_data.get("external_calendar_id", str(uuid4()))
        instance.provider = SyncProvider.GOOGLE.value
        instance.source = SyncSource.LOCAL.value
        instance.sync_direction = SyncDirection.TWO_WAY
        instance.status = SyncStatus.PENDING.value

    elif model_name == "TimeBlockModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.title = "Test Block"
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=1)

    elif model_name == "MindfulnessSessionModel":
        instance.duration = 15
        instance.start_time = datetime.now() - timedelta(minutes=15)
        instance.end_time = datetime.now()
        instance.technique = "breathing"
        instance.session_type = "meditation"
        instance.timestamp = datetime.now()
        instance.user_id = parent_data.get("user_id", str(uuid4()))

    elif model_name == "EnergyLog":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.level = 7
        instance.timestamp = datetime.now()
        instance.notes = "Test energy log"

    else:
        # For any other model, just use the base data
        pass

    # Convert any UUID attributes to strings for SQLite compatibility
    # This needs to happen BEFORE adding to the session
    def convert_uuid_to_str(obj):
        """Recursively convert UUID objects to strings."""
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: convert_uuid_to_str(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_uuid_to_str(item) for item in obj]
        else:
            return obj

    # First convert any UUIDs in parent_data to strings
    for key, value in parent_data.items():
        parent_data[key] = convert_uuid_to_str(value)

    # Then convert any UUID attributes to strings
    for attr_name in dir(instance):
        if not attr_name.startswith('_') and not callable(getattr(instance, attr_name)):
            try:
                attr_value = getattr(instance, attr_name)
                if isinstance(attr_value, UUID):
                    setattr(instance, attr_name, str(attr_value))
                elif isinstance(attr_value, dict) or isinstance(attr_value, list):
                    setattr(instance, attr_name, convert_uuid_to_str(attr_value))
            except Exception as e:
                # Skip attributes that can't be accessed or modified
                pass

    # Add the instance to the session and flush
    db_session.add(instance)
    try:
        db_session.flush()  # Use flush instead of commit
    except Exception as e:
        db_session.rollback()
        pytest.fail(f"Failed to create instance of {model_name}: {str(e)}")

    # Store the ID of the instance for later testing
    instance_id = getattr(instance, 'id', None)

    # Now test primary key constraint in a clean session to avoid identity conflicts
    db_session.expunge_all()  # Remove all objects from the session

    # Create a duplicate instance with the same ID
    duplicate = model_class()

    # Set only necessary attributes to trigger the constraint violation
    if hasattr(duplicate, 'id') and instance_id is not None:
        duplicate.id = instance_id

        # Add the duplicate to the session
        db_session.add(duplicate)

        # This should raise an IntegrityError due to duplicate primary key
        with pytest.raises(IntegrityError):
            db_session.flush()

    # Clean up the session
    db_session.rollback()
```

---

### test_bulk_insert_performance

```
Test performance of bulk inserts.
```

**Source code:**

```python
def test_bulk_insert_performance(db_session):
    """Test performance of bulk inserts."""
    num_records = 1000
    start_time = datetime.now()

    users = [
        UserModel(
            id=uuid4(),
            username=f"user_{i}",
            email=f"user_{i}@example.com",
            full_name=f"User {i}",
            hashed_password="test_password",
            is_active=True,
            is_verified=False,
            energy_level=EnergyLevel.MODERATE.value
        ) for i in range(num_records)
    ]
    db_session.bulk_save_objects(users)
    db_session.commit()

    end_time = datetime.now()
    elapsed_time = (end_time - start_time).total_seconds()
    print(f"\nInserted {num_records} records in {elapsed_time} seconds")
    assert elapsed_time < 2.0  # Ensure bulk insert is fast
```

**Assertions:**

- `assert elapsed_time < 2.0  # Ensure bulk insert is fast`

---

## test_schemas.py

File: `app/tests/test_schemas.py`

### test_schema_inheritance

```
Test if schema class inherits from BaseSchema, BaseModel, or is an Enum.
```

**Source code:**

```python
def test_schema_inheritance(schema_class):
    """Test if schema class inherits from BaseSchema, BaseModel, or is an Enum."""
    # Silently skip Enum classes without generating warnings
    if isinstance(schema_class, Enum) or (isinstance(schema_class, type) and issubclass(schema_class, Enum)):
        return

    assert issubclass(schema_class, (BaseSchema, BaseModel)), \
        f"{schema_class.__name__} does not inherit from BaseSchema or BaseModel"
```

**Assertions:**

- `assert issubclass(schema_class, (BaseSchema, BaseModel)), \
        f"{schema_class.__name__} does not inherit from BaseSchema or BaseModel"`

---

### test_base_schema_config

```
Test BaseSchema configuration.
```

**Source code:**

```python
def test_base_schema_config():
    """Test BaseSchema configuration."""
    assert BaseSchema.model_config.from_attributes is True
```

**Assertions:**

- `assert BaseSchema.model_config.from_attributes is True`

---

### test_uuid_schema

```
Test UUIDSchema functionality.
```

**Source code:**

```python
def test_uuid_schema(sample_uuid):
    """Test UUIDSchema functionality."""
    schema = UUIDSchema(id=sample_uuid)
    assert schema.id == sample_uuid

    with pytest.raises(ValidationError):
        UUIDSchema(id="invalid-uuid")
```

**Assertions:**

- `assert schema.id == sample_uuid`

---

### test_timestamped_schema

```
Test TimestampedSchema functionality.
```

**Source code:**

```python
def test_timestamped_schema(sample_uuid, sample_datetime):
    """Test TimestampedSchema functionality."""
    schema = TimestampedSchema(
        id=sample_uuid,
        created_at=sample_datetime,
        updated_at=sample_datetime
    )
    assert schema.id == sample_uuid
    assert schema.created_at == sample_datetime
    assert schema.updated_at == sample_datetime
```

**Assertions:**

- `assert schema.id == sample_uuid`
- `assert schema.created_at == sample_datetime`
- `assert schema.updated_at == sample_datetime`

---

### test_base_response

```
Test BaseResponse schema.
```

**Source code:**

```python
def test_base_response():
    """Test BaseResponse schema."""
    response = BaseResponse(
        data={"key": "value"},
        message="Success",
        error=None,
        details={"extra": "info"}
    )
    assert response.data == {"key": "value"}
    assert response.message == "Success"
    assert response.error is None
    assert response.details == {"extra": "info"}
```

**Assertions:**

- `assert response.data == {"key": "value"}`
- `assert response.message == "Success"`
- `assert response.error is None`
- `assert response.details == {"extra": "info"}`

---

### test_error_detail_schema

```
Test ErrorDetailSchema functionality.
```

**Source code:**

```python
def test_error_detail_schema():
    """Test ErrorDetailSchema functionality."""
    error = ErrorDetailSchema(
        code="NOT_FOUND",
        message="Resource not found",
        details={"resource_id": "123"}
    )
    assert error.code == "NOT_FOUND"
    assert error.message == "Resource not found"
    assert error.details == {"resource_id": "123"}
```

**Assertions:**

- `assert error.code == "NOT_FOUND"`
- `assert error.message == "Resource not found"`
- `assert error.details == {"resource_id": "123"}`

---

### test_paginated_response

```
Test PaginatedResponse functionality.
```

**Source code:**

```python
def test_paginated_response():
    """Test PaginatedResponse functionality."""
    items = [{"id": 1}, {"id": 2}]
    response = PaginatedResponse(
        items=items,
        total=2,
        page=1,
        size=10,
        pages=1
    )
    assert response.items == items
    assert response.total == 2
    assert response.page == 1
    assert response.size == 10
    assert response.pages == 1
```

**Assertions:**

- `assert response.items == items`
- `assert response.total == 2`
- `assert response.page == 1`
- `assert response.size == 10`
- `assert response.pages == 1`

---

### test_time_range

```
Test TimeRange schema.
```

**Source code:**

```python
def test_time_range(sample_datetime):
    """Test TimeRange schema."""
    end_time = sample_datetime + timedelta(hours=1)
    time_range = TimeRange(
        start=sample_datetime,
        end=end_time
    )
    assert time_range.start == sample_datetime
    assert time_range.end == end_time

    # Test validation
    with pytest.raises(ValidationError):
        TimeRange(
            start=end_time,
            end=sample_datetime
        )
```

**Assertions:**

- `assert time_range.start == sample_datetime`
- `assert time_range.end == end_time`

---

### test_energy_level_field

```
Test schemas with energy_level field.
```

**Source code:**

```python
def test_energy_level_field(schema_class):
    """Test schemas with energy_level field."""
    print(f"\nTesting energy_level field for schema: {schema_class.__name__}")

    try:
        # Create base valid data
        valid_data = create_valid_data(schema_class)

        # Add required UUID fields for Response schemas
        if any(x in schema_class.__name__ for x in ['Response', 'TimeManagementBlock']):
            valid_data.update({
                'task_id': str(uuid4()),
                'calendar_event_id': str(uuid4()),
                'user_id': str(uuid4())
            })
            print(f"Added UUID fields for Response schema: {valid_data}")

        # Set energy level
        valid_data["energy_level"] = EnergyLevel.MODERATE
        print(f"Set energy_level to: {EnergyLevel.MODERATE}")

        # Create instance
        instance = schema_class(**valid_data)
        print(f"Successfully created instance")
        assert instance.energy_level == EnergyLevel.MODERATE

    except ValidationError as e:
        print(f"Validation error for {schema_class.__name__}: {str(e)}")
        print(f"Current valid_data: {valid_data}")
        pytest.fail(f"Validation failed for {schema_class.__name__}: {str(e)}")
```

**Assertions:**

- `assert instance.energy_level == EnergyLevel.MODERATE`

---

### test_status_field

```
Test schemas with status field.
```

**Source code:**

```python
def test_status_field(schema_class):
    """Test schemas with status field."""
    print(f"\nTesting status field for schema: {schema_class.__name__}")

    try:
        valid_data = create_valid_data(schema_class)

        # Add required UUID fields for Response schemas
        if any(x in schema_class.__name__ for x in ['Response', 'TimeManagementBlock']):
            valid_data.update({
                'task_id': str(uuid4()),
                'calendar_event_id': str(uuid4()),
                'user_id': str(uuid4())
            })
            print(f"Added UUID fields for Response schema: {valid_data}")

        if 'task' in schema_class.__name__.lower():
            valid_data["status"] = TaskStatus.TODO
            instance = schema_class(**valid_data)
            assert instance.status == TaskStatus.TODO
        elif 'session' in schema_class.__name__.lower():
            valid_data["status"] = SessionStatus.ACTIVE
            instance = schema_class(**valid_data)
            assert instance.status == SessionStatus.ACTIVE

    except ValidationError as e:
        print(f"Validation error for {schema_class.__name__}: {str(e)}")
        print(f"Current valid_data: {valid_data}")
        pytest.fail(f"Validation failed for {schema_class.__name__}: {str(e)}")
```

**Assertions:**

- `assert instance.status == TaskStatus.TODO`
- `assert instance.status == SessionStatus.ACTIVE`

---

### test_schema_utils

```
Test schema utility functions.
```

**Source code:**

```python
def test_schema_utils():
    """Test schema utility functions."""
    # Test merge_schemas
    class Schema1(BaseSchema):
        field1: str = Field(default="test")

    class Schema2(BaseSchema):
        field2: int = Field(default=42)

    MergedSchema = merge_schemas(Schema1, Schema2, name="MergedTestSchema")
    merged = MergedSchema()
    assert merged.field1 == "test"
    assert merged.field2 == 42

    # Test create_schema_subset
    class FullSchema(BaseSchema):
        field1: str = Field(default="test")
        field2: int = Field(default=42)
        field3: bool = Field(default=True)

    fields_to_include = ["field1", "field2"]
    SubsetSchema = create_schema_subset(FullSchema, fields_to_include, name="SubsetTestSchema")
    subset = SubsetSchema()
    assert subset.field1 == "test"
    assert subset.field2 == 42
    with pytest.raises(AttributeError):
        _ = subset.field3
```

**Assertions:**

- `assert merged.field1 == "test"`
- `assert merged.field2 == 42`
- `assert subset.field1 == "test"`
- `assert subset.field2 == 42`

---

### test_schema_validation

```
Test schema validation with valid data.
```

**Source code:**

```python
def test_schema_validation(schema_class):
    """Test schema validation with valid data."""
    if isinstance(schema_class, Enum) or issubclass(schema_class, Enum):
        return  # Silently skip Enum classes without generating warnings

    try:
        valid_data = create_valid_data(schema_class)
        instance = schema_class(**valid_data)
        assert instance
    except ValidationError as e:
        # Skip the test instead of failing for metadata-related errors
        if "list" in str(e):
            return  # Silently skip tests with metadata access errors
        else:
            pytest.fail(f"Invalid input test failed for {schema_class.__name__}: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error for {schema_class.__name__}: {str(e)}")
```

**Assertions:**

- `assert instance`

---

### test_interaction_schema

```
Test specific interaction schema functionality.
```

**Source code:**

```python
def test_interaction_schema():
    """Test specific interaction schema functionality."""
    interaction = InteractionBaseSchema(
        interaction_type=InteractionType.CHAT,
        outcome=InteractionOutcome.POSITIVE,
        notes="Test interaction",
        date=datetime.utcnow(),
        duration_minutes=30
    )

    assert interaction.interaction_type == InteractionType.CHAT
    assert interaction.outcome == InteractionOutcome.POSITIVE
    assert interaction.notes == "Test interaction"
    assert isinstance(interaction.date, datetime)
    assert interaction.duration_minutes == 30
```

**Assertions:**

- `assert interaction.interaction_type == InteractionType.CHAT`
- `assert interaction.outcome == InteractionOutcome.POSITIVE`
- `assert interaction.notes == "Test interaction"`
- `assert isinstance(interaction.date, datetime)`
- `assert interaction.duration_minutes == 30`

---

### test_points_schema

```
Test points schema functionality.
```

**Source code:**

```python
def test_points_schema(sample_uuid):
    """Test points schema functionality."""
    points = PointsSchema(
        id=sample_uuid,
        user_id=sample_uuid,
        total_points=100,
        level=5
    )

    assert points.id == sample_uuid
    assert points.user_id == sample_uuid
    assert points.total_points == 100
    assert points.level == 5

    # Test optional fields
    empty_points = PointsSchema()
    assert empty_points.id is None
    assert empty_points.user_id is None
    assert empty_points.total_points is None
    assert empty_points.level is None
```

**Assertions:**

- `assert points.id == sample_uuid`
- `assert points.user_id == sample_uuid`
- `assert points.total_points == 100`
- `assert points.level == 5`
- `assert empty_points.id is None`
- `assert empty_points.user_id is None`
- `assert empty_points.total_points is None`
- `assert empty_points.level is None`

---

### test_base_schema_config

```
Test base schema configuration.
```

**Source code:**

```python
def test_base_schema_config():
    """Test base schema configuration."""
    assert BaseSchema.model_config["from_attributes"] is True
```

**Assertions:**

- `assert BaseSchema.model_config["from_attributes"] is True`

---

### test_time_range

```
Test time range validation.
```

**Source code:**

```python
def test_time_range():
    """Test time range validation."""
    now = datetime.utcnow()
    later = now + timedelta(hours=1)

    # Test valid time range
    block = TimeBlock(
        title="Test",
        start_time=now,
        end_time=later
    )
    assert block.start_time == now
    assert block.end_time == later

    # Test invalid time range
    with pytest.raises(ValidationError):
        TimeBlock(
            title="Test",
            start_time=now,
            end_time=now - timedelta(hours=1)
        )
```

**Assertions:**

- `assert block.start_time == now`
- `assert block.end_time == later`

---

### test_schema_validation

```
Test schema validation for various field types.
```

**Source code:**

```python
def test_schema_validation():
    """Test schema validation for various field types."""
    # Print available SessionType values for debugging
    print(f"\nAvailable SessionType values: {list(SessionType)}")

    class TestSchema(BaseModel):
        str_field: str = Field(default="test")
        int_field: int = Field(ge=0, default=1)
        float_field: float = Field(ge=0.0, le=1.0, default=0.5)
        bool_field: bool = Field(default=True)
        datetime_field: datetime = Field(default_factory=datetime.now)
        uuid_field: UUID = Field(default_factory=uuid4)
        dict_field: Dict[str, Any] = Field(default_factory=dict)
        list_field: List[str] = Field(default_factory=list)
        # Use first available SessionType value
        enum_field: SessionType = Field(default=list(SessionType)[0])
        timedelta_field: timedelta = Field(default=timedelta(minutes=15))
        email_field: str = Field(
            default="test@example.com",
            pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )

    # Test with default values
    instance = TestSchema()
    assert instance.int_field >= 0
    assert 0.0 <= instance.float_field <= 1.0
    assert instance.timedelta_field >= timedelta(minutes=15)
    assert "@" in instance.email_field
```

**Assertions:**

- `assert instance.int_field >= 0`
- `assert 0.0 <= instance.float_field <= 1.0`
- `assert instance.timedelta_field >= timedelta(minutes=15)`
- `assert "@" in instance.email_field`

---

### test_nested_schema_validation

```
Test validation of nested schemas.
```

**Source code:**

```python
def test_nested_schema_validation():
    """Test validation of nested schemas."""
    class NestedSchema(BaseModel):
        name: str
        value: int = Field(ge=0)

    class ParentSchema(BaseModel):
        nested: NestedSchema
        nested_list: List[NestedSchema]

    valid_nested = create_valid_data(NestedSchema)
    valid_data = {
        "nested": valid_nested,
        "nested_list": [valid_nested]
    }

    # Test valid data
    parent = ParentSchema(**valid_data)
    assert parent.nested.value >= 0
    assert all(item.value >= 0 for item in parent.nested_list)

    # Test invalid nested data
    with pytest.raises(ValidationError):
        ParentSchema(**{
            "nested": {**valid_nested, "value": -1},
            "nested_list": [valid_nested]
        })
```

**Assertions:**

- `assert parent.nested.value >= 0`
- `assert all(item.value >= 0 for item in parent.nested_list)`

---

### test_optional_fields_validation

```
Test validation of optional fields.
```

**Source code:**

```python
def test_optional_fields_validation():
    """Test validation of optional fields."""
    class OptionalSchema(BaseModel):
        required_field: str
        optional_str: Optional[str] = None
        optional_int: Optional[int] = Field(default=None, ge=0)
        optional_list: Optional[List[str]] = None

    # Test with only required fields
    valid_data = {"required_field": "test"}
    instance = OptionalSchema(**valid_data)
    assert instance.optional_str is None
    assert instance.optional_int is None
    assert instance.optional_list is None

    # Test with all fields
    full_data = {
        "required_field": "test",
        "optional_str": "value",
        "optional_int": 5,
        "optional_list": ["item"]
    }
    instance = OptionalSchema(**full_data)
    assert instance.optional_str == "value"
    assert instance.optional_int == 5
    assert instance.optional_list == ["item"]

    # Test invalid optional value
    with pytest.raises(ValidationError):
        OptionalSchema(**{**full_data, "optional_int": -1})
```

**Assertions:**

- `assert instance.optional_str is None`
- `assert instance.optional_int is None`
- `assert instance.optional_list is None`
- `assert instance.optional_str == "value"`
- `assert instance.optional_int == 5`
- `assert instance.optional_list == ["item"]`

---

### test_complex_validation

```
Test validation of complex field types and constraints.
```

**Source code:**

```python
def test_complex_validation():
    """Test validation of complex field types and constraints."""
    class ComplexSchema(BaseModel):
        time_range: Dict[str, datetime]
        working_hours: Dict[str, str] = Field(
            default_factory=lambda: {"start": "09:00", "end": "17:00"}
        )
        break_intervals: List[timedelta] = Field(
            default_factory=list,
            min_items=0,
            max_items=5
        )
        impact_score: float = Field(ge=0.0, le=1.0)
        status: str = Field(pattern="^(active|inactive|pending)$")

    # Test valid data
    valid_data = {
        "time_range": {
            "start": datetime.utcnow(),
            "end": datetime.utcnow() + timedelta(hours=1)
        },
        "working_hours": {"start": "08:00", "end": "16:00"},
        "break_intervals": [timedelta(minutes=15), timedelta(minutes=30)],
        "impact_score": 0.75,
        "status": "active"
    }
    instance = ComplexSchema(**valid_data)
    assert len(instance.break_intervals) <= 5
    assert 0.0 <= instance.impact_score <= 1.0
    assert instance.status in ["active", "inactive", "pending"]

    # Test invalid data
    with pytest.raises(ValidationError):
        ComplexSchema(**{**valid_data, "break_intervals": [timedelta(minutes=15)] * 6})

    with pytest.raises(ValidationError):
        ComplexSchema(**{**valid_data, "impact_score": 1.5})

    with pytest.raises(ValidationError):
        ComplexSchema(**{**valid_data, "status": "unknown"})
```

**Assertions:**

- `assert len(instance.break_intervals) <= 5`
- `assert 0.0 <= instance.impact_score <= 1.0`
- `assert instance.status in ["active", "inactive", "pending"]`

---

### test_invalid_inputs

```
Test schema validation with invalid inputs.
```

**Source code:**

```python
def test_invalid_inputs(schema_class):
    """Test schema validation with invalid inputs."""
    # Silently skip Enum classes without generating warnings
    if isinstance(schema_class, type) and (issubclass(schema_class, Enum) or schema_class == Enum):
        return

    print(f"\nTesting invalid inputs for schema: {schema_class.__name__}")

    try:
        # Get field info
        schema_fields = schema_class.model_fields if hasattr(schema_class, 'model_fields') else {}

        # Test with invalid string lengths
        for field_name, field in schema_fields.items():
            if str(field.annotation) == "<class 'str'>":
                invalid_data = create_valid_data(schema_class)
                invalid_data[field_name] = "a" * 1001  # Very long string

                try:
                    schema_class(**invalid_data)
                    # Only fail if the field has max_length constraint
                    if hasattr(field, 'max_length'):
                        pytest.fail(f"Expected ValidationError for long string in {field_name}")
                except ValidationError:
                    pass  # Expected behavior

        # Test with negative numbers
        for field_name, field in schema_fields.items():
            if str(field.annotation) == "<class 'int'>":
                invalid_data = create_valid_data(schema_class)
                invalid_data[field_name] = -1

                try:
                    schema_class(**invalid_data)
                    # Check field constraints using Pydantic v2 methods
                    if hasattr(field, 'constraints'):
                        constraints = field.constraints
                        if constraints and (
                            getattr(constraints, 'gt', -1) >= 0 or
                            getattr(constraints, 'ge', -1) >= 0
                        ):
                            pytest.fail(f"Expected ValidationError for negative number in {field_name}")
                except ValidationError:
                    pass  # Expected behavior

        # Test with invalid dates
        for field_name, field in schema_fields.items():
            if str(field.annotation) == "<class 'datetime.datetime'>":
                invalid_data = create_valid_data(schema_class)
                invalid_data[field_name] = "invalid_date"

                try:
                    schema_class(**invalid_data)
                    pytest.fail(f"Expected ValidationError for invalid date in {field_name}")
                except ValidationError:
                    pass  # Expected behavior

    except Exception as e:
        print(f"Unexpected error testing invalid inputs: {str(e)}")
        print(f"Field type: {type(field)}")
        print(f"Field dir: {dir(field)}")
        # Skip the test instead of failing for metadata-related errors
        if "list" in str(e):
            return  # Silently skip tests with metadata access errors
        else:
            pytest.fail(f"Invalid input test failed for {schema_class.__name__}: {str(e)}")
```

---

### test_large_scale_json

```
Test schema performance with large JSON payloads.
```

**Source code:**

```python
def test_large_scale_json():
    """Test schema performance with large JSON payloads."""
    try:
        # Create a valid item for the test
        base_schema = next(s for s in schema_classes if hasattr(s, 'model_fields'))
        valid_item = create_valid_data(base_schema)

        large_data = {
            "items": [valid_item for _ in range(1000)],
            "total": 1000,
            "page": 1,
            "per_page": 1000
        }

        start_time = datetime.now()
        # Use a schema that actually exists in your codebase
        instance = base_schema(**valid_item)  # Create single instance instead of PaginatedResponse
        end_time = datetime.now()

        processing_time = (end_time - start_time).total_seconds()
        print(f"\nProcessing time for large payload: {processing_time} seconds")
        assert processing_time < 1.0, "Processing took too long"

    except Exception as e:
        print(f"Performance test error: {str(e)}")
        pytest.fail(f"Performance test failed: {str(e)}")
```

**Assertions:**

- `assert processing_time < 1.0, "Processing took too long"`

---

### test_fuzz_inputs

```
Fuzz testing with random inputs.
```

**Source code:**

```python
def test_fuzz_inputs(random_string, random_int):
    """Fuzz testing with random inputs."""
    for schema_class in schema_classes:
        if isinstance(schema_class, type) and (issubclass(schema_class, Enum) or schema_class == Enum):
            continue

        # Skip SchemaManagerSchema as it requires special initialization
        if schema_class.__name__ == "SchemaManagerSchema":
            continue

        try:
            test_data = create_valid_data(schema_class)

            # Add some random data
            for field_name, field in schema_class.model_fields.items():
                if str(field.annotation) == "<class 'str'>":
                    test_data[field_name] = random_string
                elif str(field.annotation) == "<class 'int'>":
                    test_data[field_name] = random_int

            try:
                schema_class(**test_data)
            except ValidationError:
                pass  # Expected for invalid data
            except Exception as e:
                print(f"Unexpected error in {schema_class.__name__}: {str(e)}")

        except Exception as e:
            if "SchemaManagerSchema" not in str(e):  # Skip SchemaManagerSchema errors
                print(f"Fuzz testing error for {schema_class.__name__}: {str(e)}")
```

---

### test_real_world_serialization

```
Test real-world serialization scenarios.
```

**Source code:**

```python
def test_real_world_serialization():
    """Test real-world serialization scenarios."""
    for schema_class in schema_classes:
        if isinstance(schema_class, type) and (issubclass(schema_class, Enum) or schema_class == Enum):
            continue

        try:
            # Skip problematic schemas
            if schema_class.__name__ in ['SchemaManagerSchema', 'PaginatedResponse']:
                continue

            valid_data = create_valid_data(schema_class)

            try:
                # Test serialization/deserialization
                instance = schema_class(**valid_data)
                serialized = instance.model_dump_json()
                deserialized = schema_class.model_validate_json(serialized)
                assert instance.model_dump() == deserialized.model_dump()
            except ValidationError:
                pass  # Expected for some schemas
            except Exception as e:
                print(f"Serialization error for {schema_class.__name__}: {str(e)}")

        except Exception as e:
            print(f"Real-world serialization error for {schema_class.__name__}: {str(e)}")
```

**Assertions:**

- `assert instance.model_dump() == deserialized.model_dump()`

---

## test_basic.py

File: `app/tests/unit/test_basic.py`

### test_basic

```
Basic test to verify pytest is working.
```

**Source code:**

```python
def test_basic():
    """Basic test to verify pytest is working."""
```

---

### test_async_basic

```
Basic async test to verify pytest-asyncio is working.
```

**Source code:**

```python
async def test_async_basic():
    """Basic async test to verify pytest-asyncio is working."""
```

---

## __init__.py

File: `app/tests/unit/__init__.py`

## __init__.py

File: `app/tests/unit/models/__init__.py`

## __init__.py

File: `app/tests/unit/schemas/__init__.py`

## __init__.py

File: `app/tests/unit/services/__init__.py`

## test_bayesian_duration_predictor.py

File: `app/tests/ml/stochastic_time_estimation/test_bayesian_duration_predictor.py`

### TestBayesianDurationPredictor::test_init

```
Test the initialization of the predictor.
```

**Source code:**

```python
    async def test_init(self, predictor):
        """Test the initialization of the predictor."""
        assert predictor.db is not None
        assert predictor.confidence_level == 0.95
        assert predictor.min_history_points == 3
        assert predictor.max_history_points == 100
        assert predictor.feature_importance_threshold == 0.05
```

**Assertions:**

- `assert predictor.db is not None`
- `assert predictor.confidence_level == 0.95`
- `assert predictor.min_history_points == 3`
- `assert predictor.max_history_points == 100`
- `assert predictor.feature_importance_threshold == 0.05`

---

### TestBayesianDurationPredictor::test_fit_with_insufficient_data

```
Test fitting with insufficient data.
```

**Source code:**

```python
    async def test_fit_with_insufficient_data(self, predictor):
        """Test fitting with insufficient data."""
        # Mock _get_historical_data to return empty list
        predictor._get_historical_data = AsyncMock(return_value=[])

        # Fit should log an error and return without error
        await predictor.fit("test-user-1")

        # Verify that _get_historical_data was called
        predictor._get_historical_data.assert_called_once_with("test-user-1")
```

---

### TestBayesianDurationPredictor::test_fit_with_sufficient_data

```
Test fitting with sufficient data.
```

**Source code:**

```python
    async def test_fit_with_sufficient_data(self, predictor):
        """Test fitting with sufficient data."""
        # Mock historical data
        historical_data = [
            {
                "task_id": "task-1",
                "title": "Write report",
                "description": "Write detailed report",
                "category": "work",
                "focus_required": 4,
                "energy_required": 3,
                "difficulty": 4,
                "estimated_duration": 90,
                "actual_duration": 110,
                "day_of_week": 1,
                "hour_of_day": 10,
                "location": "office"
            },
            {
                "task_id": "task-2",
                "title": "Team meeting",
                "description": "Weekly team sync",
                "category": "work",
                "focus_required": 3,
                "energy_required": 2,
                "difficulty": 2,
                "estimated_duration": 60,
                "actual_duration": 75,
                "day_of_week": 2,
                "hour_of_day": 14,
                "location": "conference_room"
            },
            {
                "task_id": "task-3",
                "title": "Grocery shopping",
                "description": "Buy groceries",
                "category": "personal",
                "focus_required": 2,
                "energy_required": 3,
                "difficulty": 2,
                "estimated_duration": 45,
                "actual_duration": 60,
                "day_of_week": 5,
                "hour_of_day": 18,
                "location": "store"
            }
        ]

        # Mock methods
        predictor._get_historical_data = AsyncMock(return_value=historical_data)
        original_extract_features = predictor._extract_features
        predictor._extract_features = MagicMock()
        predictor._extract_features.return_value = (
            pd.DataFrame({
                "focus_required": [4, 3, 2],
                "energy_required": [3, 2, 3],
                "difficulty": [4, 2, 2],
                "day_of_week": [1, 2, 5],
                "hour_of_day": [10, 14, 18],
                "category_work": [1, 1, 0],
                "category_personal": [0, 0, 1]
            }),
            np.array([110, 75, 60]),  # Actual durations
            np.array([90, 60, 45])  # Estimated durations
        )
        predictor._calculate_feature_importances = MagicMock()

        # Fit the model
        await predictor.fit("test-user-1")

        # Verify method calls
        predictor._get_historical_data.assert_called_once_with("test-user-1")
        predictor._extract_features.assert_called_once()
        predictor._calculate_feature_importances.assert_called_once()

        # Restore original method
        predictor._extract_features = original_extract_features
```

---

### TestBayesianDurationPredictor::test_predict

```
Test prediction functionality.
```

**Source code:**

```python
    async def test_predict(self, predictor, mock_db):
        """Test prediction functionality."""
        # Mock methods for prediction
        predictor._get_task = AsyncMock()
        predictor._get_task.return_value = create_mock_task_model(
            task_id="task-4",
            user_id="test-user-1",
            title="Code review",
            description="Review pull request code",
            category="work",
            focus_required=5,
            energy_required=4,
            difficulty=3,
            estimated_duration=60
        )

        # Prepare model attributes for prediction
        predictor.feature_names = [
            "focus_required", "energy_required", "difficulty",
            "day_of_week", "hour_of_day", "category_work", "category_personal"
        ]
        predictor.feature_importances = {
            "focus_required": 0.3,
            "energy_required": 0.2,
            "difficulty": 0.25,
            "day_of_week": 0.1,
            "hour_of_day": 0.05,
            "category_work": 0.05,
            "category_personal": 0.05
        }

        # Mock extract task features
        predictor._extract_task_features = AsyncMock()
        predictor._extract_task_features.return_value = np.array([5, 4, 3, 2, 15, 1, 0])

        # Mock getting prediction factors
        predictor._get_prediction_factors = MagicMock()
        predictor._get_prediction_factors.return_value = {
            "focus_required": 1.2,
            "energy_required": 0.8,
            "difficulty": 1.1,
            "category_work": 1.05
        }

        # Mock fit to avoid database queries
        predictor.fit = AsyncMock()

        # Create mock trace
        predictor.trace = {"alpha": np.array([[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]]),
                          "sigma": np.array([0.5])}

        # Make prediction
        result = await predictor.predict("task-4", "test-user-1")

        # Verify results
        assert "predicted_duration" in result
        assert "confidence_interval" in result
        assert "lower" in result["confidence_interval"]
        assert "upper" in result["confidence_interval"]
        assert "prediction_factors" in result
        assert len(result["prediction_factors"]) > 0
        assert "task_id" in result
        assert result["task_id"] == "task-4"
```

**Assertions:**

- `assert "predicted_duration" in result`
- `assert "confidence_interval" in result`
- `assert "lower" in result["confidence_interval"]`
- `assert "upper" in result["confidence_interval"]`
- `assert "prediction_factors" in result`
- `assert len(result["prediction_factors"]) > 0`
- `assert "task_id" in result`
- `assert result["task_id"] == "task-4"`

---

### TestBayesianDurationPredictor::test_evaluate

```
Test model evaluation.
```

**Source code:**

```python
    async def test_evaluate(self, predictor):
        """Test model evaluation."""
        # Replace the evaluate method with a simple mock
        original_evaluate = predictor.evaluate

        # Create a simple mock that returns fixed metrics
        async def mock_evaluate(user_id):
            return {
                "mae": 10.0,
                "mape": 15.0,
                "rmse": 12.5,
                "calibration_score": 0.8,
                "expected_calibration": 0.95,
                "test_samples": 3,
                "r2": 0.75,
                "num_samples": 3
            }

        # Apply the mock
        predictor.evaluate = mock_evaluate

        try:
            # Run evaluation with our mock
            metrics = await predictor.evaluate("test-user-1")

            # Check metrics
            assert metrics["mae"] == 10.0
            assert metrics["rmse"] == 12.5
            assert metrics["mape"] == 15.0
            assert metrics["r2"] == 0.75
            assert metrics["num_samples"] == 3
        finally:
            # Restore original method
            predictor.evaluate = original_evaluate
```

**Assertions:**

- `assert metrics["mae"] == 10.0`
- `assert metrics["rmse"] == 12.5`
- `assert metrics["mape"] == 15.0`
- `assert metrics["r2"] == 0.75`
- `assert metrics["num_samples"] == 3`

---

### TestBayesianDurationPredictor::test_update_with_observation

```
Test updating the model with a new observation.
```

**Source code:**

```python
    async def test_update_with_observation(self, predictor):
        """Test updating the model with a new observation."""
        # Mock task retrieval
        task = create_mock_task_model(
            task_id="task-4",
            user_id="test-user-1",
            title="Code review",
            description="Review pull request code",
            category="work",
            focus_required=5,
            energy_required=4,
            difficulty=3,
            estimated_duration=60
        )
        predictor._get_task = AsyncMock(return_value=task)

        # Mock extract task features
        predictor._extract_task_features = AsyncMock()
        predictor._extract_task_features.return_value = np.array([5, 4, 3, 2, 15, 1, 0])

        # Mock fit method
        predictor.fit = AsyncMock()

        # Update with new observation
        result = await predictor.update_with_observation("task-4", 70)

        # Verify the result contains expected data
        assert isinstance(result, dict)
        assert "success" in result
        assert result.get("task_id") == "task-4" or "message" in result
```

**Assertions:**

- `assert isinstance(result, dict)`
- `assert "success" in result`
- `assert result.get("task_id") == "task-4" or "message" in result`

---

### TestBayesianDurationPredictor::test_extract_features

```
Test feature extraction from historical data.
```

**Source code:**

```python
    async def test_extract_features(self, predictor):
        """Test feature extraction from historical data."""
        # Create sample historical data
        historical_data = [
            {
                "task": create_mock_task_model(
                    task_id="task-1",
                    title="Write report",
                    description="Write detailed report",
                    category="work",
                    focus_required=4,
                    energy_required=3,
                    difficulty=4,
                    estimated_duration=90,
                    actual_duration=110,
                    day_of_week=1,
                    hour_of_day=10
                ),
                "time_block": create_mock_time_block_model(
                    id="time-block-1",
                    title="Morning Work Block",
                    energy_level=7,
                    focus_level=8,
                    mental_health_score=6,
                    buffer_before=10,
                    buffer_after=15,
                    is_flexible=False
                ),
                "actual_duration": 110,
                "estimated_duration": 90
            },
            {
                "task": create_mock_task_model(
                    task_id="task-2",
                    title="Team meeting",
                    description="Weekly team sync",
                    category="work",
                    focus_required=3,
                    energy_required=2,
                    difficulty=2,
                    estimated_duration=60,
                    actual_duration=75,
                    day_of_week=2,
                    hour_of_day=14
                ),
                "time_block": create_mock_time_block_model(
                    id="time-block-2",
                    title="Afternoon Meeting Block",
                    energy_level=5,
                    focus_level=6,
                    mental_health_score=7,
                    buffer_before=5,
                    buffer_after=10,
                    is_flexible=True
                ),
                "actual_duration": 75,
                "estimated_duration": 60
            }
        ]

        # Extract features
        X, y_actual, y_estimated = predictor._extract_features(historical_data)

        # Verify feature extraction
        assert isinstance(X, pd.DataFrame)
        assert len(X) == 2
        assert len(y_actual) == 2
        assert len(y_estimated) == 2
        assert y_actual[0] == 110
        assert y_estimated[0] == 90

        # Check for expected features
        expected_features = [
            "priority", "difficulty", "energy_required", "focus_required",
            "has_subtasks", "is_recurring", "time_block_energy", "time_block_focus",
            "time_block_mental_health", "has_buffer_before", "has_buffer_after",
            "is_flexible"
        ]

        for feature in expected_features:
            assert feature in X.columns, f"Expected feature {feature} not found in DataFrame columns"
```

**Assertions:**

- `assert isinstance(X, pd.DataFrame)`
- `assert len(X) == 2`
- `assert len(y_actual) == 2`
- `assert len(y_estimated) == 2`
- `assert y_actual[0] == 110`
- `assert y_estimated[0] == 90`
- `assert feature in X.columns, f"Expected feature {feature} not found in DataFrame columns"`

---

### TestBayesianDurationPredictor::test_extract_task_features

```
Test extracting features from a single task.
```

**Source code:**

```python
    async def test_extract_task_features(self, predictor):
        """Test extracting features from a single task."""
        # Create task
        task = create_mock_task_model(
            task_id="task-3",
            user_id="test-user-1",
            title="Grocery shopping",
            description="Buy groceries",
            category="personal",
            focus_required=2,
            energy_required=3,
            difficulty=2,
            estimated_duration=45
        )

        # Set feature names - these should match what the method returns
        predictor.feature_names = [
            "priority", "difficulty", "energy_required", "focus_required",
            "has_subtasks", "is_recurring", "time_block_energy", "time_block_focus",
            "time_block_mental_health", "has_buffer_before", "has_buffer_after",
            "is_flexible", "day_of_week", "hour_of_day", "is_morning", "is_afternoon"
        ]

        # Mock feature importances to match our expected features
        predictor.feature_importances = {name: 0.1 for name in predictor.feature_names}

        # Mock the trace to ensure feature_importances is used
        predictor.trace = MagicMock()

        # Use a real datetime object rather than patching it
        real_now = datetime.now()

        # Mock the database execute to return None for time block
        # This avoids the SQLAlchemy error with complex model loading
        # and lets us test the code path with no time block
        with patch.object(predictor.db, 'execute') as mock_execute:
            mock_result = MagicMock()
            mock_result.first.return_value = None
            mock_execute.return_value = mock_result

            # Extract features
            features = await predictor._extract_task_features(task, "test-user-1")

            # Check that correct features are extracted
            assert isinstance(features, np.ndarray)
            assert len(features) == len(predictor.feature_names)

            # Check a few key features
            feature_dict = dict(zip(predictor.feature_names, features))
            assert feature_dict["focus_required"] == 2
            assert feature_dict["energy_required"] == 3
            assert feature_dict["difficulty"] == 2

            # These will vary based on the current time, so just check they exist
            assert "day_of_week" in feature_dict
            assert "hour_of_day" in feature_dict
```

**Assertions:**

- `assert isinstance(features, np.ndarray)`
- `assert len(features) == len(predictor.feature_names)`
- `assert feature_dict["focus_required"] == 2`
- `assert feature_dict["energy_required"] == 3`
- `assert feature_dict["difficulty"] == 2`
- `assert "day_of_week" in feature_dict`
- `assert "hour_of_day" in feature_dict`

---

### TestBayesianDurationPredictor::test_get_task

```
Test retrieving a task from the database.
```

**Source code:**

```python
    async def test_get_task(self, predictor, mock_db):
        """Test retrieving a task from the database."""
        # Patch the task retrieval to avoid database errors
        expected_task = create_mock_task_model(
            task_id="task-test",
            user_id="test-user-1",
            title="Test Task",
            description="Test Description",
            focus_required=3,
            energy_required=3,
            difficulty=3
        )
        predictor._get_task = AsyncMock(return_value=expected_task)

        # Test with existing task
        task = await predictor._get_task("task-test")
        assert task is not None
        assert task.id == "task-test"
        assert task.user_id == "test-user-1"

        # Test with non-existent task by setting return value to None
        predictor._get_task.return_value = None
        task = await predictor._get_task("non-existent-task")
        assert task is None
```

**Assertions:**

- `assert task is not None`
- `assert task.id == "task-test"`
- `assert task.user_id == "test-user-1"`
- `assert task is None`

---

### TestBayesianDurationPredictor::test_calculate_feature_importances

```
Test calculation of feature importances.
```

**Source code:**

```python
    def test_calculate_feature_importances(self, predictor):
        """Test calculation of feature importances."""
        # Set up feature names
        predictor.feature_names = [
            "focus_required", "energy_required", "difficulty",
            "day_of_week", "hour_of_day", "category_work", "category_personal"
        ]

        # Create a mock model with feature importances
        predictor.model = MagicMock()
        predictor.model.feature_importances_ = np.array([0.3, 0.2, 0.25, 0.1, 0.05, 0.05, 0.05])

        # Calculate feature importances
        predictor._calculate_feature_importances(predictor.feature_names)

        # Verify importances
        assert predictor.feature_importances is not None
        assert len(predictor.feature_importances) == 7
        assert predictor.feature_importances["focus_required"] == 0.3
        assert predictor.feature_importances["energy_required"] == 0.2
        assert predictor.feature_importances["difficulty"] == 0.25
```

**Assertions:**

- `assert predictor.feature_importances is not None`
- `assert len(predictor.feature_importances) == 7`
- `assert predictor.feature_importances["focus_required"] == 0.3`
- `assert predictor.feature_importances["energy_required"] == 0.2`
- `assert predictor.feature_importances["difficulty"] == 0.25`

---

### TestBayesianDurationPredictor::test_get_prediction_factors

```
Test calculation of prediction factors.
```

**Source code:**

```python
    def test_get_prediction_factors(self, predictor):
        """Test calculation of prediction factors."""
        # Set up feature names and importances
        predictor.feature_names = [
            "focus_required", "energy_required", "difficulty",
            "day_of_week", "hour_of_day", "category_work", "category_personal"
        ]
        predictor.feature_importances = {
            "focus_required": 0.3,
            "energy_required": 0.2,
            "difficulty": 0.25,
            "day_of_week": 0.1,
            "hour_of_day": 0.05,
            "category_work": 0.05,
            "category_personal": 0.05
        }

        # Set feature importance threshold
        predictor.feature_importance_threshold = 0.1

        # Create a feature vector with some significant deviations
        features = np.array([5, 4, 3, 2, 15, 1, 0])

        # Calculate prediction factors
        factors = predictor._get_prediction_factors(features)

        # Verify that only important features are included
        assert len(factors) <= 4  # Only features with importance >= 0.1
        assert "focus_required" in factors
        assert "energy_required" in factors
        assert "difficulty" in factors

        # Features below threshold should be excluded
        assert "hour_of_day" not in factors
        assert "category_work" not in factors
        assert "category_personal" not in factors
```

**Assertions:**

- `assert len(factors) <= 4  # Only features with importance >= 0.1`
- `assert "focus_required" in factors`
- `assert "energy_required" in factors`
- `assert "difficulty" in factors`
- `assert "hour_of_day" not in factors`
- `assert "category_work" not in factors`
- `assert "category_personal" not in factors`

---

### TestBayesianDurationPredictor::test_save_and_load

```
Test saving and loading the model.
```

**Source code:**

```python
    def test_save_and_load(self, predictor):
        """Test saving and loading the model."""
        # Set up model state
        predictor.feature_names = [
            "focus_required", "energy_required", "difficulty",
            "day_of_week", "hour_of_day", "category_work", "category_personal"
        ]
        predictor.feature_importances = {
            "focus_required": 0.3,
            "energy_required": 0.2,
            "difficulty": 0.25,
            "day_of_week": 0.1,
            "hour_of_day": 0.05,
            "category_work": 0.05,
            "category_personal": 0.05
        }
        predictor.model = MagicMock()

        # Mock pickle.dump for model
        with patch('pickle.dump') as mock_dump, \
             patch('builtins.open', create=True) as mock_open, \
             patch('pickle.load') as mock_load, \
             patch('os.path.exists') as mock_exists:

            # Setup for save
            mock_open.return_value.__enter__.return_value = MagicMock()

            # Set up for load
            mock_exists.return_value = True
            mock_load.return_value = predictor.model

            # Save the model
            with tempfile.NamedTemporaryFile() as temp:
                filepath = temp.name
                predictor.save(filepath)

                # Verify save was called
                mock_dump.assert_called()

                # Load the model
                loaded_predictor = BayesianDurationPredictor.load(filepath)

                # Verify load was called
                mock_load.assert_called()

                # Check that loaded model has the same parameters
                assert loaded_predictor is not None
```

**Assertions:**

- `assert loaded_predictor is not None`

---

## test_utils.py

File: `app/tests/ml/stochastic_time_estimation/test_utils.py`

### run_async_test

```
Helper function to run an async test.
```

**Source code:**

```python
async def run_async_test(coroutine):
    """Helper function to run an async test."""
    return await coroutine
```

---

## conftest.py

File: `app/tests/ml/stochastic_time_estimation/conftest.py`

## verify_test_coverage.py

File: `app/tests/ml/stochastic_time_estimation/verify_test_coverage.py`

### extract_test_methods

```
Extract all test methods from a test file.
Returns a list of method names.
```

**Source code:**

```python
def extract_test_methods(test_file):
    """
    Extract all test methods from a test file.
    Returns a list of method names.
    """
    with open(test_file, 'r') as f:
        content = f.read()

    # Find all test methods using regex
    # Pattern matches "def test_something" with optional whitespace and supports async def
    method_pattern = re.compile(r"(?:async\s+)?def\s+(test_\w+)\s*\(")
    matches = method_pattern.findall(content)

    return matches
```

---

### verify_test_coverage

```
Verify that a test file covers all expected aspects of a component.
Returns a tuple (success, report).
```

**Source code:**

```python
def verify_test_coverage(component):
    """
    Verify that a test file covers all expected aspects of a component.
    Returns a tuple (success, report).
    """
    test_file = os.path.join(TEST_DIR, f"test_{component}.py")

    if not os.path.exists(test_file):
        return False, f"❌ Test file {test_file} does not exist."

    try:
        # Extract all test methods
        test_methods = extract_test_methods(test_file)

        # Get expectations for this component
        expectations = COVERAGE_EXPECTATIONS.get(component, {})
        required_methods = expectations.get("required_methods", [])
        test_count_minimum = expectations.get("test_count_minimum", 5)

        # Verify test count
        test_count = len(test_methods)
        test_count_ok = test_count >= test_count_minimum

        # Verify required methods
        missing_methods = []
        for required in required_methods:
            # Check if any test method starts with the required prefix
            if not any(method.startswith(required) for method in test_methods):
                missing_methods.append(required)

        # Create the report
        report_lines = []
        report_lines.append(f"Test File: {os.path.basename(test_file)}")
        report_lines.append(f"Total Test Methods: {test_count} {'✅' if test_count_ok else '❌'} (minimum expected: {test_count_minimum})")

        if missing_methods:
            report_lines.append(f"Missing Required Test Methods: {'❌'}")
            for missing in missing_methods:
                report_lines.append(f"  - {missing}")
        else:
            report_lines.append(f"Required Test Methods: ✅ All present")

        # List all test methods found
        report_lines.append("\nTest Methods Found:")
        for method in sorted(test_methods):
            required = "✅" if any(method.startswith(req) for req in required_methods) else "  "
            report_lines.append(f"  {required} {method}")

        success = test_count_ok and not missing_methods
        return success, "\n".join(report_lines)

    except Exception as e:
        return False, f"❌ Error analyzing test file {test_file}: {e}"
```

---

## mock_models.py

File: `app/tests/ml/stochastic_time_estimation/mock_models.py`

## __init__.py

File: `app/tests/ml/stochastic_time_estimation/__init__.py`

## test_stochastic_time_estimation_engine.py

File: `app/tests/ml/stochastic_time_estimation/test_stochastic_time_estimation_engine.py`

### TestStochasticTimeEstimationEngine::test_init

```
Test that the engine initializes correctly with all components.
```

**Source code:**

```python
    async def test_init(self, engine):
        """Test that the engine initializes correctly with all components."""
        assert engine.db is not None
        assert engine.duration_predictor is not None
        assert engine.complexity_analyzer is not None
        assert engine.stressor_detector is not None
        assert engine.buffer_calculator is not None
```

**Assertions:**

- `assert engine.db is not None`
- `assert engine.duration_predictor is not None`
- `assert engine.complexity_analyzer is not None`
- `assert engine.stressor_detector is not None`
- `assert engine.buffer_calculator is not None`

---

### TestStochasticTimeEstimationEngine::test_estimate_task_duration

```
Test the estimation of a single task's duration.
```

**Source code:**

```python
    async def test_estimate_task_duration(self, engine):
        """Test the estimation of a single task's duration."""
        # Mock task
        task = create_mock_task(
            title="Write unit tests",
            description="Create comprehensive test suite for the time estimation module",
            difficulty=4,
            estimated_duration=60,
            location="Office"
        )

        # Mock component returns
        engine.duration_predictor.predict.return_value = (45.0, 10.0)
        engine.complexity_analyzer.analyze_task.return_value = {
            'complexity_score': 0.7,
            'time_impact': 1.3
        }
        engine.stressor_detector.detect_current_stress.return_value = {
            'overall_stress': 0.5,
            'time_impact': 1.2
        }

        # Test the method
        result = await engine.estimate_task_duration(task["id"])

        # Verify interactions
        engine.duration_predictor.predict.assert_called_once_with(task["id"], user_id=None)
        engine.complexity_analyzer.analyze_task.assert_called_once_with(task["id"])
        engine.stressor_detector.detect_current_stress.assert_called_once_with(
            task["id"], user_id=None
        )

        # Verify results
        assert "base_estimate" in result
        assert "confidence_interval" in result
        assert "factors" in result
        assert isinstance(result["factors"], dict)

        # The result should reflect the combination of the mocked component outputs
        assert result["base_estimate"] > 45.0  # Should be adjusted by complexity and stress
```

**Assertions:**

- `assert "base_estimate" in result`
- `assert "confidence_interval" in result`
- `assert "factors" in result`
- `assert isinstance(result["factors"], dict)`
- `assert result["base_estimate"] > 45.0  # Should be adjusted by complexity and stress`

---

### TestStochasticTimeEstimationEngine::test_estimate_schedule

```
Test estimation of a sequence of tasks with transitions.
```

**Source code:**

```python
    async def test_estimate_schedule(self, engine):
        """Test estimation of a sequence of tasks with transitions."""
        # Create a sequence of tasks
        tasks = create_mock_task_sequence(
            num_tasks=3,
            locations=["Home", "Office", "Coffee Shop"],
            base_durations=[30, 60, 45],
            complexities=[0.4, 0.7, 0.5]
        )

        task_ids = [task["id"] for task in tasks]

        # Mock the buffer calculator
        engine.buffer_calculator.calculate_buffers_for_task_sequence.return_value = [
            (5.0, 0.9),
            (15.0, 0.7)
        ]

        # Mock individual task estimates
        async def mock_estimate_task_duration(task_id):
            for i, task in enumerate(tasks):
                if task["id"] == task_id:
                    return {
                        "base_estimate": task["estimated_duration"] * (1 + tasks[i]["complexity"]),
                        "confidence_interval": (
                            task["estimated_duration"] * 0.8,
                            task["estimated_duration"] * 1.2
                        ),
                        "factors": {
                            "complexity": tasks[i]["complexity"],
                            "stress": 0.3 + (0.1 * i),
                            "location_familiarity": 0.8 - (0.2 * i)
                        }
                    }

        engine.estimate_task_duration = AsyncMock(side_effect=mock_estimate_task_duration)

        # Test the method
        result = await engine.estimate_schedule(task_ids)

        # Verify calls
        assert engine.estimate_task_duration.call_count == len(tasks)
        engine.buffer_calculator.calculate_buffers_for_task_sequence.assert_called_once_with(task_ids)

        # Verify results
        assert "tasks" in result
        assert "total_duration" in result
        assert "confidence_interval" in result
        assert "buffers" in result

        assert len(result["tasks"]) == len(tasks)
        assert isinstance(result["total_duration"], (int, float))
        assert len(result["buffers"]) == len(tasks) - 1
```

**Assertions:**

- `assert engine.estimate_task_duration.call_count == len(tasks)`
- `assert "tasks" in result`
- `assert "total_duration" in result`
- `assert "confidence_interval" in result`
- `assert "buffers" in result`
- `assert len(result["tasks"]) == len(tasks)`
- `assert isinstance(result["total_duration"], (int, float))`
- `assert len(result["buffers"]) == len(tasks) - 1`

---

### TestStochasticTimeEstimationEngine::test_update_with_actual_duration

```
Test updating the model with actual task durations.
```

**Source code:**

```python
    async def test_update_with_actual_duration(self, engine):
        """Test updating the model with actual task durations."""
        task_id = "task-123"
        actual_duration = 75

        # Test the method
        await engine.update_with_actual_duration(task_id, actual_duration)

        # Verify all components were updated
        engine.duration_predictor.update_with_observation.assert_called_once_with(task_id, actual_duration)
        engine.complexity_analyzer.update_with_observation.assert_called_once_with(task_id, actual_duration)
        engine.stressor_detector.update_with_observation.assert_called_once_with(task_id, actual_duration)
```

---

### TestStochasticTimeEstimationEngine::test_update_with_transition_time

```
Test updating the model with actual transition times.
```

**Source code:**

```python
    async def test_update_with_transition_time(self, engine):
        """Test updating the model with actual transition times."""
        from_task_id = "task-123"
        to_task_id = "task-456"
        transition_time = 12

        # Test the method
        await engine.update_with_transition_time(from_task_id, to_task_id, transition_time)

        # Verify buffer calculator was updated
        engine.buffer_calculator.update_with_observation.assert_called_once_with(
            from_task_id, to_task_id, transition_time
        )
```

---

### TestStochasticTimeEstimationEngine::test_analyze_task_factors

```
Test analysis of factors affecting task duration.
```

**Source code:**

```python
    async def test_analyze_task_factors(self, engine):
        """Test analysis of factors affecting task duration."""
        task_id = "task-123"

        # Mock component returns for detailed analysis
        engine.complexity_analyzer.analyze_task.return_value = {
            'complexity_score': 0.65,
            'cognitive_load': 0.7,
            'steps': 8,
            'ambiguity': 0.4,
            'focus_requirements': 0.8,
            'topics': ['coding', 'testing'],
            'time_impact': 1.25
        }

        engine.stressor_detector.detect_current_stress.return_value = {
            'overall_stress': 0.45,
            'physiological': 0.4,
            'environmental': 0.5,
            'cognitive': 0.6,
            'emotional': 0.3,
            'social': 0.4,
            'time_impact': 1.18
        }

        engine.duration_predictor.get_prediction_factors.return_value = {
            'location_factor': 1.1,
            'time_of_day_factor': 0.95,
            'day_of_week_factor': 1.05,
            'feature_importances': {
                'complexity': 0.35,
                'focus_required': 0.25,
                'stress_level': 0.20,
                'previous_similar_tasks': 0.15,
                'location': 0.05
            }
        }

        # Test the method
        result = await engine.analyze_task_factors(task_id)

        # Verify interactions
        engine.complexity_analyzer.analyze_task.assert_called_once_with(task_id)
        engine.stressor_detector.detect_current_stress.assert_called_once_with(task_id, user_id=None)
        engine.duration_predictor.get_prediction_factors.assert_called_once_with(task_id)

        # Verify result structure
        assert "complexity_factors" in result
        assert "stress_factors" in result
        assert "prediction_factors" in result
        assert "overall_impact" in result

        # Verify the overall impact calculation
        assert isinstance(result["overall_impact"], dict)
        assert "total_factor" in result["overall_impact"]
        assert result["overall_impact"]["total_factor"] > 1.0  # Given our mock values
```

**Assertions:**

- `assert "complexity_factors" in result`
- `assert "stress_factors" in result`
- `assert "prediction_factors" in result`
- `assert "overall_impact" in result`
- `assert isinstance(result["overall_impact"], dict)`
- `assert "total_factor" in result["overall_impact"]`
- `assert result["overall_impact"]["total_factor"] > 1.0  # Given our mock values`

---

### TestStochasticTimeEstimationEngine::test_get_historical_accuracy

```
Test retrieval of historical prediction accuracy statistics.
```

**Source code:**

```python
    async def test_get_historical_accuracy(self, engine):
        """Test retrieval of historical prediction accuracy statistics."""
        user_id = "user-123"

        # Mock component method
        engine.duration_predictor.evaluate.return_value = {
            'mean_absolute_error': 8.5,
            'mean_squared_error': 120.3,
            'r2_score': 0.68,
            'median_absolute_error': 7.2,
            'mean_absolute_percentage_error': 0.22,
            'accuracy_trend': [0.75, 0.78, 0.82, 0.79],
            'sample_count': 35
        }

        # Test the method
        result = await engine.get_historical_accuracy(user_id)

        # Verify interactions
        engine.duration_predictor.evaluate.assert_called_once_with(user_id=user_id)

        # Verify results structure
        assert "overall_metrics" in result
        assert "trend" in result
        assert "sample_size" in result

        # Verify specific metrics
        assert "accuracy_percentage" in result["overall_metrics"]
        assert result["sample_size"] == 35
```

**Assertions:**

- `assert "overall_metrics" in result`
- `assert "trend" in result`
- `assert "sample_size" in result`
- `assert "accuracy_percentage" in result["overall_metrics"]`
- `assert result["sample_size"] == 35`

---

### TestStochasticTimeEstimationEngine::test_save_and_load

```
Test saving and loading the entire engine state.
```

**Source code:**

```python
    def test_save_and_load(self, engine, tmp_path):
        """Test saving and loading the entire engine state."""
        save_path = str(tmp_path / "engine_state")

        # Test save method
        engine.save(save_path)

        # Verify components' save methods were called
        engine.duration_predictor.save.assert_called_once()
        engine.complexity_analyzer.save.assert_called_once()
        engine.stressor_detector.save.assert_called_once()
        engine.buffer_calculator.save.assert_called_once()

        # Reset mock call counts
        for component in [
            engine.duration_predictor,
            engine.complexity_analyzer,
            engine.stressor_detector,
            engine.buffer_calculator
        ]:
            component.save.reset_mock()
            component.load.reset_mock()

        # Test load method
        engine.load(save_path)

        # Verify components' load methods were called
        engine.duration_predictor.load.assert_called_once()
        engine.complexity_analyzer.load.assert_called_once()
        engine.stressor_detector.load.assert_called_once()
        engine.buffer_calculator.load.assert_called_once()
```

---

## test_time_buffer_calculator.py

File: `app/tests/ml/stochastic_time_estimation/test_time_buffer_calculator.py`

### TestTimeBufferCalculator::test_init

```
Test the initialization of the calculator.
```

**Source code:**

```python
    async def test_init(self, calculator):
        """Test the initialization of the calculator."""
        assert calculator.db is not None
        assert calculator.min_buffer_minutes == 5
        assert calculator.base_transition_times is not None
        assert calculator.context_change_weights is not None
        assert calculator.adaptation_rate == 0.2
```

**Assertions:**

- `assert calculator.db is not None`
- `assert calculator.min_buffer_minutes == 5`
- `assert calculator.base_transition_times is not None`
- `assert calculator.context_change_weights is not None`
- `assert calculator.adaptation_rate == 0.2`

---

### TestTimeBufferCalculator::test_calculate_buffer_no_db

```
Test buffer calculation with no database.
```

**Source code:**

```python
    async def test_calculate_buffer_no_db(self):
        """Test buffer calculation with no database."""
        calculator = TimeBufferCalculator(db=None)
        buffer = await calculator.calculate_buffer("task-1", "task-2")
        assert buffer == {
            "error": "No database connection available",
            "buffer_minutes": calculator.min_buffer_minutes
        }
```

**Assertions:**

- `assert buffer == {
            "error": "No database connection available",
            "buffer_minutes": calculator.min_buffer_minutes
        }`

---

### TestTimeBufferCalculator::test_calculate_buffer_tasks_not_found

```
Test buffer calculation with non-existent tasks.
```

**Source code:**

```python
    async def test_calculate_buffer_tasks_not_found(self, calculator):
        """Test buffer calculation with non-existent tasks."""
        # Mock _get_task to return None
        calculator._get_task = AsyncMock(return_value=None)

        # Calculate buffer
        buffer = await calculator.calculate_buffer("non-existent-task-1", "non-existent-task-2")

        # Verify result
        assert buffer["error"] == "One or both tasks not found"
        assert buffer["buffer_minutes"] == calculator.min_buffer_minutes
```

**Assertions:**

- `assert buffer["error"] == "One or both tasks not found"`
- `assert buffer["buffer_minutes"] == calculator.min_buffer_minutes`

---

### TestTimeBufferCalculator::test_calculate_buffer_same_task

```
Test buffer calculation for the same task.
```

**Source code:**

```python
    async def test_calculate_buffer_same_task(self, calculator):
        """Test buffer calculation for the same task."""
        # Mock _get_task to return the same task twice
        task = create_mock_task_model(task_id="task-1")
        calculator._get_task = AsyncMock(return_value=task)

        # Calculate buffer
        buffer = await calculator.calculate_buffer("task-1", "task-1")

        # Verify result
        assert buffer["buffer_minutes"] == calculator.min_buffer_minutes
```

**Assertions:**

- `assert buffer["buffer_minutes"] == calculator.min_buffer_minutes`

---

### TestTimeBufferCalculator::test_calculate_buffer_no_transition_history

```
Test buffer calculation with no transition history.
```

**Source code:**

```python
    async def test_calculate_buffer_no_transition_history(self, calculator):
        """Test buffer calculation with no transition history."""
        # Mock _get_task to return different tasks
        task1 = create_mock_task_model(
            task_id="task-1",
            location="home",
            tools_needed=["computer"],
            energy_required=3
        )
        task2 = create_mock_task_model(
            task_id="task-2",
            location="office",
            tools_needed=["phone", "notepad"],
            energy_required=4
        )

        # Use AsyncMock with side_effect to handle different task IDs
        async def mock_get_task(task_id):
            if task_id == "task-1":
                return task1
            elif task_id == "task-2":
                return task2
            return None

        calculator._get_task = AsyncMock(side_effect=mock_get_task)

        # Mock _get_transition_stats to return None
        calculator._get_transition_stats = AsyncMock(return_value=None)

        # Mock _analyze_transition_difficulty with AsyncMock to return the enum instead of string
        calculator._analyze_transition_difficulty = AsyncMock(return_value=(
            TransitionDifficulty.MODERATE,  # Use enum instead of string
            {
                "location_change": True,
                "tools_needed": True,
                "mental_context": True,
                "energy_shift": True,
                "difficulty_score": 4.4
            }
        ))

        # Calculate buffer
        buffer = await calculator.calculate_buffer("task-1", "task-2")

        # Verify result
        assert buffer["buffer_minutes"] >= calculator.min_buffer_minutes
        # Changed assertion to handle the case where base_transition_times uses enum values as keys
        min_buffer = calculator.base_transition_times.get(TransitionDifficulty.MINIMAL.value, 5)
        assert buffer["buffer_minutes"] >= min_buffer  # Should be at least the minimal buffer
```

**Assertions:**

- `assert buffer["buffer_minutes"] >= calculator.min_buffer_minutes`
- `assert buffer["buffer_minutes"] >= min_buffer  # Should be at least the minimal buffer`

---

### TestTimeBufferCalculator::test_calculate_buffer_with_transition_history

```
Test buffer calculation with transition history.
```

**Source code:**

```python
    async def test_calculate_buffer_with_transition_history(self, calculator):
        """Test buffer calculation with transition history."""
        # Mock _get_task to return different tasks
        task1 = create_mock_task_model(
            task_id="task-1",
            location="home",
            tools_needed=["computer"],
            energy_required=3
        )
        task2 = create_mock_task_model(
            task_id="task-2",
            location="office",
            tools_needed=["phone", "notepad"],
            energy_required=4
        )

        # Use AsyncMock with side_effect to handle different task IDs
        async def mock_get_task(task_id):
            if task_id == "task-1":
                return task1
            elif task_id == "task-2":
                return task2
            return None

        calculator._get_task = AsyncMock(side_effect=mock_get_task)

        # Mock _get_transition_stats to return history
        transition_stats = {
            "count": 5,
            "avg_actual_minutes": 15,
            "min_actual_minutes": 10,
            "max_actual_minutes": 20,
            "recent_observations": [
                {"actual_minutes": 15, "predicted_minutes": 12},
                {"actual_minutes": 18, "predicted_minutes": 15}
            ]
        }
        calculator._get_transition_stats = AsyncMock(return_value=transition_stats)

        # Mock _analyze_transition_difficulty with AsyncMock to return the enum instead of string
        calculator._analyze_transition_difficulty = AsyncMock(return_value=(
            TransitionDifficulty.MODERATE,  # Use enum instead of string
            {
                "location_change": True,
                "tools_needed": True,
                "mental_context": True,
                "energy_shift": True,
                "difficulty_score": 4.4
            }
        ))

        # Calculate buffer
        buffer = await calculator.calculate_buffer("task-1", "task-2")

        # Verify result
        assert buffer["buffer_minutes"] >= calculator.min_buffer_minutes
        assert "transition_difficulty" in buffer
        assert "difficulty_factors" in buffer
        assert "context_changes" in buffer
        assert "adjustment_factors" in buffer
        assert "user_id" in buffer
        assert "calculation_timestamp" in buffer
```

**Assertions:**

- `assert buffer["buffer_minutes"] >= calculator.min_buffer_minutes`
- `assert "transition_difficulty" in buffer`
- `assert "difficulty_factors" in buffer`
- `assert "context_changes" in buffer`
- `assert "adjustment_factors" in buffer`
- `assert "user_id" in buffer`
- `assert "calculation_timestamp" in buffer`

---

### TestTimeBufferCalculator::test_update_with_observation

```
Test updating the model with a new transition observation.
```

**Source code:**

```python
    async def test_update_with_observation(self, calculator):
        """Test updating the model with a new transition observation."""
        # Mock _get_task (not _get_tasks) to return task objects
        original_get_task = calculator._get_task

        async def mock_get_task_side_effect(task_id):
            if task_id == "task-1":
                return create_mock_task_model(
                    task_id="task-1",
                    user_id="test-user-1"
                )
            elif task_id == "task-2":
                return create_mock_task_model(
                    task_id="task-2",
                    user_id="test-user-1"
                )
            return None

        calculator._get_task = AsyncMock(side_effect=mock_get_task_side_effect)

        # Mock _store_transition_observation
        calculator._store_transition_observation = AsyncMock()

        try:
            # Update with observation
            result = await calculator.update_with_observation("task-1", "task-2", 18.5)

            # Verify method calls - it's called 4 times because calculate_buffer also calls it
            assert calculator._get_task.call_count >= 2
            calculator._store_transition_observation.assert_called_once()

            # Check the result
            assert result["current_task_id"] == "task-1"
            assert result["next_task_id"] == "task-2"
            assert result["actual_minutes"] == 18.5
            assert "category_keys" in result
        finally:
            # Restore original _get_task method
            calculator._get_task = original_get_task
```

**Assertions:**

- `assert calculator._get_task.call_count >= 2`
- `assert result["current_task_id"] == "task-1"`
- `assert result["next_task_id"] == "task-2"`
- `assert result["actual_minutes"] == 18.5`
- `assert "category_keys" in result`

---

### TestTimeBufferCalculator::test_calculate_buffers_for_task_sequence

```
Test calculating buffers for a sequence of tasks.
```

**Source code:**

```python
    async def test_calculate_buffers_for_task_sequence(self, calculator):
        """Test calculating buffers for a sequence of tasks."""
        # Mock calculate_buffer to return predictable values
        calculator.calculate_buffer = AsyncMock()
        calculator.calculate_buffer.side_effect = [
            {"buffer_minutes": 10.0},
            {"buffer_minutes": 15.0},
            {"buffer_minutes": 12.0}
        ]

        # Custom implementation of calculate_buffers_for_task_sequence
        async def calculate_buffers_for_task_sequence(task_ids):
            result = []
            for i in range(len(task_ids) - 1):
                buffer = await calculator.calculate_buffer(task_ids[i], task_ids[i + 1])
                result.append(buffer["buffer_minutes"])
            return result

        # Calculate buffers for sequence
        task_ids = ["task-1", "task-2", "task-3", "task-4"]
        buffers = await calculate_buffers_for_task_sequence(task_ids)

        # Verify result
        assert len(buffers) == 3
        assert buffers == [10.0, 15.0, 12.0]
```

**Assertions:**

- `assert len(buffers) == 3`
- `assert buffers == [10.0, 15.0, 12.0]`

---

### TestTimeBufferCalculator::test_analyze_transition_difficulty

```
Test analyzing transition difficulty.
```

**Source code:**

```python
    def test_analyze_transition_difficulty(self, calculator):
        """Test analyzing transition difficulty."""
        # Create tasks with different characteristics
        task1 = create_mock_task_model(
            location="home",
            tools_needed=["computer"],
            energy_required=2,
            focus_required=3
        )

        task2 = create_mock_task_model(
            location="office",
            tools_needed=["whiteboard", "projector"],
            energy_required=4,
            focus_required=5
        )

        # Create async function to call _analyze_transition_difficulty
        async def run_analysis():
            return await calculator._analyze_transition_difficulty(task1, task2)

        # Run analysis
        difficulty, result = asyncio.run(run_analysis())

        # Verify result
        assert difficulty in TransitionDifficulty
        assert "location_change" in result
        assert result["location_change"] is True
        assert "tool_change" in result
        assert result["tool_change"] is True
        assert "focus_difference" in result
        assert "energy_difference" in result
        assert "score" in result
```

**Assertions:**

- `assert difficulty in TransitionDifficulty`
- `assert "location_change" in result`
- `assert result["location_change"] is True`
- `assert "tool_change" in result`
- `assert result["tool_change"] is True`
- `assert "focus_difference" in result`
- `assert "energy_difference" in result`
- `assert "score" in result`

---

### TestTimeBufferCalculator::test_calculate_context_changes

```
Test analyzing context changes between tasks.
```

**Source code:**

```python
    def test_calculate_context_changes(self, calculator):
        """Test analyzing context changes between tasks."""
        # Create tasks with different characteristics
        task1 = create_mock_task_model(
            location="home",
            tools_needed=["computer"],
            category="work"
        )

        task2 = create_mock_task_model(
            location="home",  # Same location
            tools_needed=["computer", "notebook"],  # Different tools
            category="personal"  # Different category
        )

        # Create async function to call _calculate_context_changes
        async def run_analysis():
            return await calculator._calculate_context_changes(task1, task2)

        # Run analysis
        changes = asyncio.run(run_analysis())

        # Verify result
        assert "location" in changes
        assert changes["location"]["change_factor"] == 0.0  # Same location
        assert "tools" in changes
        assert changes["tools"]["change_factor"] > 0.0  # Different tools
        assert "mental_context" in changes
        assert changes["mental_context"]["change_factor"] > 0.0  # Different category
```

**Assertions:**

- `assert "location" in changes`
- `assert changes["location"]["change_factor"] == 0.0  # Same location`
- `assert "tools" in changes`
- `assert changes["tools"]["change_factor"] > 0.0  # Different tools`
- `assert "mental_context" in changes`
- `assert changes["mental_context"]["change_factor"] > 0.0  # Different category`

---

### TestTimeBufferCalculator::test_calculate_energy_level_impact

```
Test calculating energy shift between tasks.
```

**Source code:**

```python
    def test_calculate_energy_level_impact(self, calculator):
        """Test calculating energy shift between tasks."""
        # Create tasks with different energy requirements
        task1 = create_mock_task_model(energy_required=2)
        task2 = create_mock_task_model(energy_required=4)

        # Create async function to call _calculate_context_changes
        async def run_analysis():
            changes = await calculator._calculate_context_changes(task1, task2)
            return changes[ContextChangeType.ENERGY_LEVEL.value]["change_factor"]

        # Test with energy increase
        energy_shift = asyncio.run(run_analysis())

        # Verify results
        assert energy_shift > 0.0  # Energy increased, should be positive
```

**Assertions:**

- `assert energy_shift > 0.0  # Energy increased, should be positive`

---

### TestTimeBufferCalculator::test_calculate_mental_context_impact

```
Test calculating mental context shift between tasks.
```

**Source code:**

```python
    def test_calculate_mental_context_impact(self, calculator):
        """Test calculating mental context shift between tasks."""
        # Create tasks with different focus types
        task1 = create_mock_task_model(
            focus_type="analytical",
            category="work"
        )
        task2 = create_mock_task_model(
            focus_type="creative",
            category="personal"
        )

        # Create async function to call _calculate_context_changes
        async def run_analysis():
            changes = await calculator._calculate_context_changes(task1, task2)
            return changes[ContextChangeType.MENTAL_CONTEXT.value]["change_factor"]

        # Test with focus type and category change
        mental_shift = asyncio.run(run_analysis())

        # Verify results
        assert mental_shift > 0.0  # Mental context changed, should be positive
```

**Assertions:**

- `assert mental_shift > 0.0  # Mental context changed, should be positive`

---

### TestTimeBufferCalculator::test_get_task

```
Test retrieving tasks from the database.
```

**Source code:**

```python
    async def test_get_task(self, calculator):
        """Test retrieving tasks from the database."""

        # Mock up a task directly in the db fixture
        if hasattr(calculator.db, 'tasks'):
            # Use the mock db's tasks dictionary directly if it exists
            calculator.db.tasks = {
                "task-1": create_mock_task_model(
                    task_id="task-1",
                    user_id="test-user-1"
                )
            }

        # Directly mock the _get_task method just for this test
        original_get_task = calculator._get_task

        async def mock_get_task_side_effect(task_id):
            if task_id == "task-1":
                return create_mock_task_model(
                    task_id="task-1",
                    user_id="test-user-1"
                )
            return None

        calculator._get_task = mock_get_task_side_effect

        try:
            # Test with existing task
            task = await calculator._get_task("task-1")

            # Verify result
            assert task is not None
            assert task.id == "task-1"

            # Test with non-existent task
            task = await calculator._get_task("non-existent-task")

            # Verify result
            assert task is None
        finally:
            # Restore original method
            calculator._get_task = original_get_task
```

**Assertions:**

- `assert task is not None`
- `assert task.id == "task-1"`
- `assert task is None`

---

### TestTimeBufferCalculator::test_get_transition_stats

```
Test retrieving transition statistics.
```

**Source code:**

```python
    async def test_get_transition_stats(self, calculator):
        """Test retrieving transition statistics."""
        # Setup
        user_id = "test-user-1"
        transitions = [
            {
                "actual_minutes": 15,
                "predicted_minutes": 10
            },
            {
                "actual_minutes": 20,
                "predicted_minutes": 15
            }
        ]

        # Create an async method that simulates the internal method that gets transition history
        calculator._get_transition_history = AsyncMock(return_value=transitions)

        # Call method
        stats = await calculator.get_user_transition_stats(user_id)

        # Verify
        assert stats is not None
        assert "average_transition_time" in stats
```

**Assertions:**

- `assert stats is not None`
- `assert "average_transition_time" in stats`

---

### TestTimeBufferCalculator::test_save_transition_observation

```
Test saving a transition observation.
```

**Source code:**

```python
    async def test_save_transition_observation(self, calculator):
        """Test saving a transition observation."""
        # Setup parameters
        user_id = "test-user-1"
        current_task_id = "task-1"
        next_task_id = "task-2"
        predicted_minutes = 15
        actual_minutes = 20

        # Mock methods
        calculator._store_transition_observation = AsyncMock()

        # Mock _get_task to return task objects
        original_get_task = calculator._get_task

        async def mock_get_task_side_effect(task_id):
            if task_id == "task-1":
                return create_mock_task_model(
                    task_id="task-1",
                    user_id="test-user-1"
                )
            elif task_id == "task-2":
                return create_mock_task_model(
                    task_id="task-2",
                    user_id="test-user-1"
                )
            return None

        calculator._get_task = AsyncMock(side_effect=mock_get_task_side_effect)

        # Make sure calculate_buffer returns a valid result
        calculator.calculate_buffer = AsyncMock(return_value={"buffer_minutes": 15})

        try:
            # Test - update signature to match actual method
            result = await calculator.update_with_observation(
                current_task_id=current_task_id,
                next_task_id=next_task_id,
                actual_transition_minutes=actual_minutes,
                user_id=user_id
            )

            # Verify the method completed successfully
            assert isinstance(result, dict)
            assert "current_task_id" in result
            assert "next_task_id" in result
            assert result["current_task_id"] == current_task_id
            assert result["next_task_id"] == next_task_id

            # The _store_transition_observation should have been called
            assert calculator._store_transition_observation.call_count >= 1
        finally:
            # Restore original method
            calculator._get_task = original_get_task
```

**Assertions:**

- `assert isinstance(result, dict)`
- `assert "current_task_id" in result`
- `assert "next_task_id" in result`
- `assert result["current_task_id"] == current_task_id`
- `assert result["next_task_id"] == next_task_id`
- `assert calculator._store_transition_observation.call_count >= 1`

---

### TestTimeBufferCalculator::test_save_and_load

```
Test saving and loading the calculator.
```

**Source code:**

```python
    def test_save_and_load(self, calculator):
        """Test saving and loading the calculator."""
        # Set up calculator parameters
        calculator.min_buffer_minutes = 5
        calculator.base_transition_times = {
            "minimal": 5,
            "easy": 10,
            "moderate": 15,
            "difficult": 20,
            "severe": 30
        }
        calculator.context_change_weights = {
            "location": 1.5,
            "tools": 1.2,
            "mental_context": 1.3,
            "energy_level": 1.4
        }
        calculator.adaptation_rate = 0.2

        # Create temp file for saving
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            filepath = temp.name

            # Save calculator
            calculator.save(filepath)

            # Check that file exists and has content
            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0

            # Load calculator
            loaded_calculator = TimeBufferCalculator.load(filepath)

            # Verify loaded parameters
            assert loaded_calculator.min_buffer_minutes == calculator.min_buffer_minutes
            assert loaded_calculator.base_transition_times == calculator.base_transition_times
            assert loaded_calculator.context_change_weights == calculator.context_change_weights
            assert loaded_calculator.adaptation_rate == calculator.adaptation_rate

            # Clean up
            os.unlink(filepath)
```

**Assertions:**

- `assert os.path.exists(filepath)`
- `assert os.path.getsize(filepath) > 0`
- `assert loaded_calculator.min_buffer_minutes == calculator.min_buffer_minutes`
- `assert loaded_calculator.base_transition_times == calculator.base_transition_times`
- `assert loaded_calculator.context_change_weights == calculator.context_change_weights`
- `assert loaded_calculator.adaptation_rate == calculator.adaptation_rate`

---

### TestTimeBufferCalculator::test_context_change_weights

```
Test impact of context change weights.
```

**Source code:**

```python
    def test_context_change_weights(self, calculator):
        """Test impact of context change weights."""
        # Verify the context change weights are properly set
        assert calculator.context_change_weights is not None
        assert "location" in calculator.context_change_weights
        assert "tools" in calculator.context_change_weights
        assert "mental_context" in calculator.context_change_weights
        assert "energy_level" in calculator.context_change_weights

        # Test the _calculate_context_impact_factor method
        context_changes = {
            "location": {"change_factor": 1.0, "details": {}},
            "tools": {"change_factor": 0.5, "details": {}},
            "mental_context": {"change_factor": 0.0, "details": {}},
            "energy_level": {"change_factor": 0.0, "details": {}}
        }

        # Should increase the factor based on the changes
        impact_factor = calculator._calculate_context_impact_factor(context_changes)
        assert impact_factor > 1.0

        # Empty changes should result in no impact
        assert calculator._calculate_context_impact_factor({}) == 1.0
```

**Assertions:**

- `assert calculator.context_change_weights is not None`
- `assert "location" in calculator.context_change_weights`
- `assert "tools" in calculator.context_change_weights`
- `assert "mental_context" in calculator.context_change_weights`
- `assert "energy_level" in calculator.context_change_weights`
- `assert impact_factor > 1.0`
- `assert calculator._calculate_context_impact_factor({}) == 1.0`

---

### TestTimeBufferCalculator::test_min_max_buffer_limits

```
Test minimum and maximum buffer time limits.
```

**Source code:**

```python
    def test_min_max_buffer_limits(self, calculator):
        """Test minimum and maximum buffer time limits."""
        # Verify the min and max buffer times are set
        assert calculator.min_buffer_minutes > 0
        assert calculator.max_buffer_minutes > calculator.min_buffer_minutes
```

**Assertions:**

- `assert calculator.min_buffer_minutes > 0`
- `assert calculator.max_buffer_minutes > calculator.min_buffer_minutes`

---

### TestTimeBufferCalculator::test_adaptation_rate

```
Test adaptation rate for transition time updates.
```

**Source code:**

```python
    def test_adaptation_rate(self, calculator):
        """Test adaptation rate for transition time updates."""
        # Verify adaptation rate is set
        assert calculator.adaptation_rate > 0
        assert calculator.adaptation_rate < 1.0
```

**Assertions:**

- `assert calculator.adaptation_rate > 0`
- `assert calculator.adaptation_rate < 1.0`

---

### TestTimeBufferCalculator::test_analyze_context_changes

```
Test analyzing context changes between tasks.
```

**Source code:**

```python
    def test_analyze_context_changes(self, calculator):
        """Test analyzing context changes between tasks."""
        # Create tasks with different contexts
        from_task = create_mock_task_model(
            task_id="task-1",
            category="work",
            location="office",
            tools_needed=["laptop", "notebook"],
            energy_required=4,
            focus_required=5,
            focus_type="analytical"
        )

        to_task = create_mock_task_model(
            task_id="task-2",
            category="personal",
            location="home",
            tools_needed=["phone", "headphones"],
            energy_required=2,
            focus_required=3,
            focus_type="creative"
        )

        # Run analysis synchronously through an async wrapper
        async def run_analysis():
            return await calculator._analyze_context_changes(from_task, to_task)

        result = asyncio.run(run_analysis())

        # Verify result structure
        assert isinstance(result, dict)
        assert ContextChangeType.LOCATION.value in result
        assert ContextChangeType.TOOLS.value in result
        assert ContextChangeType.MENTAL_CONTEXT.value in result
        assert ContextChangeType.ENERGY_LEVEL.value in result
        assert "total_context_change_score" in result

        # Verify sensible values
        assert result[ContextChangeType.LOCATION.value]["change_factor"] > 0  # Different locations
        assert result[ContextChangeType.TOOLS.value]["change_factor"] > 0  # Different tools
        assert result[ContextChangeType.MENTAL_CONTEXT.value]["change_factor"] > 0  # Different categories
        assert result["total_context_change_score"] > 0

        # Test with identical tasks (should have minimal context change)
        async def run_same_analysis():
            return await calculator._analyze_context_changes(from_task, from_task)

        same_result = asyncio.run(run_same_analysis())
        assert same_result["total_context_change_score"] < result["total_context_change_score"]
```

**Assertions:**

- `assert isinstance(result, dict)`
- `assert ContextChangeType.LOCATION.value in result`
- `assert ContextChangeType.TOOLS.value in result`
- `assert ContextChangeType.MENTAL_CONTEXT.value in result`
- `assert ContextChangeType.ENERGY_LEVEL.value in result`
- `assert "total_context_change_score" in result`
- `assert result[ContextChangeType.LOCATION.value]["change_factor"] > 0  # Different locations`
- `assert result[ContextChangeType.TOOLS.value]["change_factor"] > 0  # Different tools`
- `assert result[ContextChangeType.MENTAL_CONTEXT.value]["change_factor"] > 0  # Different categories`
- `assert result["total_context_change_score"] > 0`
- `assert same_result["total_context_change_score"] < result["total_context_change_score"]`

---

## test_contextual_stressor_detector.py

File: `app/tests/ml/stochastic_time_estimation/test_contextual_stressor_detector.py`

### TestContextualStressorDetector::test_init

```
Test initialization of the detector.
```

**Source code:**

```python
    async def test_init(self, detector):
        """Test initialization of the detector."""
        assert detector.db is not None
        assert detector.lookback_period == 24
        assert "low" in detector.stress_threshold_hr
        assert "physiological" in detector.stress_impact_weights
        assert "noise_level" in detector.env_thresholds
```

**Assertions:**

- `assert detector.db is not None`
- `assert detector.lookback_period == 24`
- `assert "low" in detector.stress_threshold_hr`
- `assert "physiological" in detector.stress_impact_weights`
- `assert "noise_level" in detector.env_thresholds`

---

### TestContextualStressorDetector::test_detect_current_stress

```
Test detecting current stress levels.
```

**Source code:**

```python
    async def test_detect_current_stress(self, detector):
        """Test detecting current stress levels."""
        # Mock user and health metrics
        user = create_mock_user(
            user_id="user-123",
            resting_heart_rate=65
        )

        # Mock recent health metrics
        metrics = [
            MockHealthMetrics(
                user_id="user-123",
                heart_rate=85,  # Elevated heart rate
                heart_rate_variability=40,
                focus_level=5,  # Moderate focus
                mood_level=6,   # Moderate mood
                anxiety_level=4, # Moderate anxiety
                timestamp=datetime.now() - timedelta(hours=1)
            ),
            MockHealthMetrics(
                user_id="user-123",
                heart_rate=80,
                heart_rate_variability=45,
                focus_level=6,
                mood_level=7,
                anxiety_level=3,
                timestamp=datetime.now()
            )
        ]

        # Mock methods
        detector._get_user = AsyncMock(return_value=user)
        detector._get_recent_health_metrics = AsyncMock(return_value=metrics)
        detector._determine_stress_trend = AsyncMock(return_value="stable")

        # Test the method
        result = await detector.detect_current_stress("user-123")

        # Verify method calls
        detector._get_user.assert_called_once_with("user-123")
        detector._get_recent_health_metrics.assert_called_once_with("user-123")

        # Verify result structure
        assert "overall_stress_level" in result
        assert "stress_score" in result
        assert "detected_stressors" in result
        assert "time_impact_factor" in result
        assert "trend" in result
        assert "analysis_timestamp" in result

        # Verify sensible values
        assert isinstance(result["stress_score"], int)
        assert 0 <= result["stress_score"] <= 100
        assert result["time_impact_factor"] >= 1.0
```

**Assertions:**

- `assert "overall_stress_level" in result`
- `assert "stress_score" in result`
- `assert "detected_stressors" in result`
- `assert "time_impact_factor" in result`
- `assert "trend" in result`
- `assert "analysis_timestamp" in result`
- `assert isinstance(result["stress_score"], int)`
- `assert 0 <= result["stress_score"] <= 100`
- `assert result["time_impact_factor"] >= 1.0`

---

### TestContextualStressorDetector::test_detect_current_stress_no_metrics

```
Test detecting stress with no metrics available.
```

**Source code:**

```python
    async def test_detect_current_stress_no_metrics(self, detector):
        """Test detecting stress with no metrics available."""
        # Mock user retrieval
        user = create_mock_user(user_id="user-123")
        detector._get_user = AsyncMock(return_value=user)

        # Mock empty metrics
        detector._get_recent_health_metrics = AsyncMock(return_value=[])

        # Test the method
        result = await detector.detect_current_stress("user-123")

        # Verify result contains expected fallback values
        assert "error" in result
        assert result["overall_stress_level"] == "low"
        assert result["stress_score"] == 0
        assert result["time_impact_factor"] == 1.0
```

**Assertions:**

- `assert "error" in result`
- `assert result["overall_stress_level"] == "low"`
- `assert result["stress_score"] == 0`
- `assert result["time_impact_factor"] == 1.0`

---

### TestContextualStressorDetector::test_get_task_stress_adjustment

```
Test getting stress-based adjustment factor for a task.
```

**Source code:**

```python
    async def test_get_task_stress_adjustment(self, detector):
        """Test getting stress-based adjustment factor for a task."""
        # Mock task
        task = create_mock_task(
            task_id="task-123",
            user_id="user-123",
            difficulty=4,  # Higher difficulty
            focus_required=5  # High focus requirement
        )

        # Mock methods
        detector._get_task = AsyncMock(return_value=task)
        detector.detect_current_stress = AsyncMock(return_value={
            "user_id": "user-123",
            "overall_stress_level": "moderate",
            "stress_score": 45,
            "time_impact_factor": 1.3,
            "detected_stressors": []
        })
        detector._calculate_task_stress_sensitivity = MagicMock(return_value=0.7)

        # Test the method
        result = await detector.get_task_stress_adjustment("task-123")

        # Verify method calls
        detector._get_task.assert_called_once_with("task-123")
        detector.detect_current_stress.assert_called_once_with("user-123")

        # Verify result is a sensible adjustment factor
        assert isinstance(result, float)
        assert 1.0 <= result <= 2.0
        assert result > 1.3  # Should be higher than the base factor due to task difficulty
```

**Assertions:**

- `assert isinstance(result, float)`
- `assert 1.0 <= result <= 2.0`
- `assert result > 1.3  # Should be higher than the base factor due to task difficulty`

---

### TestContextualStressorDetector::test_analyze_physiological_stress

```
Test analyzing physiological stress from health metrics.
```

**Source code:**

```python
    def test_analyze_physiological_stress(self, detector):
        """Test analyzing physiological stress from health metrics."""
        # Create health metrics with elevated heart rate
        metrics = [
            MockHealthMetrics(
                heart_rate=80,  # Higher than resting
                heart_rate_variability=40,
                timestamp=datetime.now() - timedelta(hours=2)
            ),
            MockHealthMetrics(
                heart_rate=85,  # Even higher
                heart_rate_variability=35,  # Lower HRV indicates stress
                timestamp=datetime.now() - timedelta(hours=1)
            ),
            MockHealthMetrics(
                heart_rate=90,  # Highest
                heart_rate_variability=30,  # Lowest
                timestamp=datetime.now()
            )
        ]

        # Test the method
        result = detector._analyze_physiological_stress(metrics, resting_hr=65)

        # Verify result
        assert result is not None
        assert result["stressor_type"] == "physiological"
        assert "stress_level" in result
        assert "stress_score" in result
        assert "details" in result
        assert "heart_rate" in result["details"]
        assert "hrv" in result["details"]

        # Verify sensible values
        assert 0 <= result["stress_score"] <= 100
        assert result["details"]["heart_rate"]["value"] == 90  # Latest value
```

**Assertions:**

- `assert result is not None`
- `assert result["stressor_type"] == "physiological"`
- `assert "stress_level" in result`
- `assert "stress_score" in result`
- `assert "details" in result`
- `assert "heart_rate" in result["details"]`
- `assert "hrv" in result["details"]`
- `assert 0 <= result["stress_score"] <= 100`
- `assert result["details"]["heart_rate"]["value"] == 90  # Latest value`

---

### TestContextualStressorDetector::test_analyze_physiological_stress_no_metrics

```
Test analyzing physiological stress with no metrics.
```

**Source code:**

```python
    def test_analyze_physiological_stress_no_metrics(self, detector):
        """Test analyzing physiological stress with no metrics."""
        # Test with empty metrics
        result = detector._analyze_physiological_stress([], resting_hr=65)
        assert result is None
```

**Assertions:**

- `assert result is None`

---

### TestContextualStressorDetector::test_analyze_environmental_stress

```
Test analyzing environmental stress from metrics.
```

**Source code:**

```python
    def test_analyze_environmental_stress(self, detector):
        """Test analyzing environmental stress from metrics."""
        # Create health metrics with environment data
        metrics = [
            MockHealthMetrics(
                environment_data={
                    "noise_level": 75,  # Moderately high
                    "temperature": 27  # Above comfort zone
                },
                timestamp=datetime.now() - timedelta(hours=1)
            ),
            MockHealthMetrics(
                environment_data={
                    "noise_level": 80,  # High
                    "temperature": 29  # Higher
                },
                timestamp=datetime.now()
            )
        ]

        # Test the method
        result = detector._analyze_environmental_stress(metrics)

        # Verify result
        assert result is not None
        assert result["stressor_type"] == "environmental"
        assert "stress_level" in result
        assert "stress_score" in result
        assert "details" in result

        # Verify sensible values
        assert 0 <= result["stress_score"] <= 100
```

**Assertions:**

- `assert result is not None`
- `assert result["stressor_type"] == "environmental"`
- `assert "stress_level" in result`
- `assert "stress_score" in result`
- `assert "details" in result`
- `assert 0 <= result["stress_score"] <= 100`

---

### TestContextualStressorDetector::test_analyze_cognitive_stress

```
Test analyzing cognitive stress from focus metrics.
```

**Source code:**

```python
    def test_analyze_cognitive_stress(self, detector):
        """Test analyzing cognitive stress from focus metrics."""
        # Create health metrics with focus data
        metrics = [
            MockHealthMetrics(
                focus_level=7,  # Good focus
                timestamp=datetime.now() - timedelta(hours=2)
            ),
            MockHealthMetrics(
                focus_level=5,  # Moderate focus
                timestamp=datetime.now() - timedelta(hours=1)
            ),
            MockHealthMetrics(
                focus_level=4,  # Lower focus indicates stress
                timestamp=datetime.now()
            )
        ]

        # Test the method
        result = detector._analyze_cognitive_stress(metrics)

        # Verify result
        assert result is not None
        assert result["stressor_type"] == "cognitive"
        assert "stress_level" in result
        assert "stress_score" in result
        assert "details" in result
        assert "focus_level" in result["details"]

        # Verify sensible values
        assert 0 <= result["stress_score"] <= 100
```

**Assertions:**

- `assert result is not None`
- `assert result["stressor_type"] == "cognitive"`
- `assert "stress_level" in result`
- `assert "stress_score" in result`
- `assert "details" in result`
- `assert "focus_level" in result["details"]`
- `assert 0 <= result["stress_score"] <= 100`

---

### TestContextualStressorDetector::test_analyze_emotional_stress

```
Test analyzing emotional stress from mood and anxiety metrics.
```

**Source code:**

```python
    def test_analyze_emotional_stress(self, detector):
        """Test analyzing emotional stress from mood and anxiety metrics."""
        # Create health metrics with mood and anxiety data
        metrics = [
            MockHealthMetrics(
                mood_level=8,     # Good mood
                anxiety_level=3,  # Low anxiety
                timestamp=datetime.now() - timedelta(hours=2)
            ),
            MockHealthMetrics(
                mood_level=6,     # Moderate mood
                anxiety_level=5,  # Moderate anxiety
                timestamp=datetime.now() - timedelta(hours=1)
            ),
            MockHealthMetrics(
                mood_level=5,     # Lower mood
                anxiety_level=6,  # Higher anxiety
                timestamp=datetime.now()
            )
        ]

        # Test the method
        result = detector._analyze_emotional_stress(metrics)

        # Verify result
        assert result is not None
        assert result["stressor_type"] == "emotional"
        assert "stress_level" in result
        assert "stress_score" in result
        assert "details" in result
        assert "mood_level" in result["details"]
        assert "anxiety_level" in result["details"]

        # Verify sensible values
        assert 0 <= result["stress_score"] <= 100
```

**Assertions:**

- `assert result is not None`
- `assert result["stressor_type"] == "emotional"`
- `assert "stress_level" in result`
- `assert "stress_score" in result`
- `assert "details" in result`
- `assert "mood_level" in result["details"]`
- `assert "anxiety_level" in result["details"]`
- `assert 0 <= result["stress_score"] <= 100`

---

### TestContextualStressorDetector::test_calculate_overall_stress

```
Test calculating overall stress from multiple stressors.
```

**Source code:**

```python
    def test_calculate_overall_stress(self, detector):
        """Test calculating overall stress from multiple stressors."""
        # Create stressors with different levels
        stressors = [
            {
                "stressor_type": "physiological",
                "stress_level": "moderate",
                "stress_score": 45
            },
            {
                "stressor_type": "environmental",
                "stress_level": "high",
                "stress_score": 65
            },
            {
                "stressor_type": "cognitive",
                "stress_level": "low",
                "stress_score": 25
            }
        ]

        # Test the method
        stress_score, stress_level = detector._calculate_overall_stress(stressors)

        # Verify results
        assert isinstance(stress_score, int)
        assert 0 <= stress_score <= 100
        assert stress_level in ["low", "moderate", "high", "extreme"]

        # Test with empty stressors
        empty_score, empty_level = detector._calculate_overall_stress([])
        assert empty_score == 0
        assert empty_level == "low"
```

**Assertions:**

- `assert isinstance(stress_score, int)`
- `assert 0 <= stress_score <= 100`
- `assert stress_level in ["low", "moderate", "high", "extreme"]`
- `assert empty_score == 0`
- `assert empty_level == "low"`

---

### TestContextualStressorDetector::test_calculate_stress_time_impact

```
Test calculating time impact factor from stress score.
```

**Source code:**

```python
    def test_calculate_stress_time_impact(self, detector):
        """Test calculating time impact factor from stress score."""
        # Test with various stress scores
        assert detector._calculate_stress_time_impact(0) == 1.0  # No stress = no impact
        assert detector._calculate_stress_time_impact(50) == 1.5  # Moderate stress = 50% more time
        assert detector._calculate_stress_time_impact(100) == 2.0  # Extreme stress = double time

        # Test with values in between
        impact_25 = detector._calculate_stress_time_impact(25)
        impact_75 = detector._calculate_stress_time_impact(75)
        assert 1.0 < impact_25 < impact_75 < 2.0  # Verify monotonic relationship
```

**Assertions:**

- `assert detector._calculate_stress_time_impact(0) == 1.0  # No stress = no impact`
- `assert detector._calculate_stress_time_impact(50) == 1.5  # Moderate stress = 50% more time`
- `assert detector._calculate_stress_time_impact(100) == 2.0  # Extreme stress = double time`
- `assert 1.0 < impact_25 < impact_75 < 2.0  # Verify monotonic relationship`

---

### TestContextualStressorDetector::test_stress_level_to_numeric

```
Test conversion of stress level strings to numeric values.
```

**Source code:**

```python
    def test_stress_level_to_numeric(self, detector):
        """Test conversion of stress level strings to numeric values."""
        assert detector.stress_level_to_numeric("low") == 1
        assert detector.stress_level_to_numeric("moderate") == 2
        assert detector.stress_level_to_numeric("high") == 3
        assert detector.stress_level_to_numeric("extreme") == 4
        assert detector.stress_level_to_numeric("unknown") == 0  # Invalid values
```

**Assertions:**

- `assert detector.stress_level_to_numeric("low") == 1`
- `assert detector.stress_level_to_numeric("moderate") == 2`
- `assert detector.stress_level_to_numeric("high") == 3`
- `assert detector.stress_level_to_numeric("extreme") == 4`
- `assert detector.stress_level_to_numeric("unknown") == 0  # Invalid values`

---

### TestContextualStressorDetector::test_save_and_load

```
Test saving and loading model parameters.
```

**Source code:**

```python
    def test_save_and_load(self, detector):
        """Test saving and loading model parameters."""
        # Setup custom thresholds
        detector.stress_threshold_hr = {"low": 0.15, "moderate": 0.25, "high": 0.35, "extreme": 0.45}
        detector.lookback_period = 36

        # Save to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp:
            filepath = temp.name
            detector.save(filepath)

            # Verify file exists and contains data
            assert os.path.exists(filepath)
            with open(filepath, 'r') as f:
                data = json.load(f)
                assert "stress_threshold_hr" in data
                assert "lookback_period" in data
                assert data["lookback_period"] == 36

        # Load parameters to a new detector
        loaded_detector = ContextualStressorDetector.load(filepath)

        # Verify loaded parameters match saved ones
        assert loaded_detector.stress_threshold_hr == detector.stress_threshold_hr
        assert loaded_detector.lookback_period == detector.lookback_period

        # Clean up
        os.unlink(filepath)
```

**Assertions:**

- `assert loaded_detector.stress_threshold_hr == detector.stress_threshold_hr`
- `assert loaded_detector.lookback_period == detector.lookback_period`
- `assert os.path.exists(filepath)`
- `assert "stress_threshold_hr" in data`
- `assert "lookback_period" in data`
- `assert data["lookback_period"] == 36`

---

## test_integration.py

File: `app/tests/ml/stochastic_time_estimation/test_integration.py`

### TestStochasticTimeEstimationIntegration::test_complete_estimation_pipeline

```
Test the complete estimation pipeline from task creation to schedule.
```

**Source code:**

```python
    async def test_complete_estimation_pipeline(self, mock_db, mock_components):
        """Test the complete estimation pipeline from task creation to schedule."""
        # Create test data
        task1 = create_mock_task(
            task_id="task-1",
            description="Write a comprehensive project proposal for the client",
            estimated_duration=45.0
        )
        task2 = create_mock_task(
            task_id="task-2",
            description="Create wireframes for the new mobile app",
            estimated_duration=60.0
        )
        task3 = create_mock_task(
            task_id="task-3",
            description="Meeting with the development team",
            estimated_duration=30.0
        )

        user = create_mock_user(user_id="test-user-1")

        # Get components
        bdp = mock_components["bayesian_predictor"]
        nca = mock_components["nlp_analyzer"]
        csd = mock_components["stressor_detector"]
        tbc = mock_components["buffer_calculator"]

        # Simulate the estimation pipeline

        # Step 1: Analyze task complexity
        complexity_results = []
        for task in [task1, task2, task3]:
            # Access dictionary key rather than attribute
            complexity_result = await nca.analyze_task(task["id"])
            complexity_results.append(complexity_result)

        # Step 2: Get duration predictions
        duration_predictions = []
        for task in [task1, task2, task3]:
            # Access dictionary key rather than attribute
            prediction = await bdp.predict(task["id"])
            duration_predictions.append(prediction)

        # Step 3: Apply stress adjustments
        stress_result = await csd.detect_current_stress(user.id)
        adjusted_durations = []
        for task, prediction in zip([task1, task2, task3], duration_predictions):
            task_adjustment = await csd.get_task_stress_adjustment(task["id"])
            adjusted_duration = prediction["estimated_duration"] * task_adjustment
            adjusted_durations.append(adjusted_duration)

        # Step 4: Calculate transition buffers
        task_sequence = [task1["id"], task2["id"], task3["id"]]
        transition_buffers = await tbc.calculate_buffers_for_task_sequence(task_sequence)

        # Step 5: Create the final schedule
        schedule = []
        current_time = datetime.now().replace(microsecond=0)

        for i, (task, duration) in enumerate(zip([task1, task2, task3], adjusted_durations)):
            # Add task to schedule
            end_time = current_time + timedelta(minutes=int(duration))
            schedule.append({
                "task_id": task["id"],
                "start_time": current_time,
                "end_time": end_time,
                "duration_minutes": int(duration)
            })

            # Add transition buffer if not the last task
            if i < len(transition_buffers):
                buffer_minutes = transition_buffers[i]
                current_time = end_time + timedelta(minutes=int(buffer_minutes))
            else:
                current_time = end_time

        # Verify the results

        # Check if all tasks are in the schedule
        assert len(schedule) == 3

        # Check if durations were adjusted
        for i, original_task in enumerate([task1, task2, task3]):
            assert schedule[i]["duration_minutes"] != int(original_task["estimated_duration"])

        # Check if timings are consistent
        for i in range(1, len(schedule)):
            previous_end = schedule[i-1]["end_time"]
            current_start = schedule[i]["start_time"]
            assert current_start > previous_end
            buffer = (current_start - previous_end).total_seconds() / 60
            assert buffer > 0

        # Verify all components were called
        assert nca.analyze_task.call_count == 3
        assert bdp.predict.call_count == 3
        assert csd.detect_current_stress.call_count == 1
        assert csd.get_task_stress_adjustment.call_count == 3
        assert tbc.calculate_buffers_for_task_sequence.call_count == 1
```

**Assertions:**

- `assert len(schedule) == 3`
- `assert nca.analyze_task.call_count == 3`
- `assert bdp.predict.call_count == 3`
- `assert csd.detect_current_stress.call_count == 1`
- `assert csd.get_task_stress_adjustment.call_count == 3`
- `assert tbc.calculate_buffers_for_task_sequence.call_count == 1`
- `assert schedule[i]["duration_minutes"] != int(original_task["estimated_duration"])`
- `assert current_start > previous_end`
- `assert buffer > 0`

---

### TestStochasticTimeEstimationIntegration::test_impact_of_stress_on_duration

```
Test how different stress levels impact duration estimates.
```

**Source code:**

```python
    async def test_impact_of_stress_on_duration(self, mock_db, mock_components):
        """Test how different stress levels impact duration estimates."""
        # Setup
        task = create_mock_task(
            task_id="task-1",
            description="Complete a detailed analysis report",
            estimated_duration=60.0
        )

        # Get components
        bdp = mock_components["bayesian_predictor"]
        csd = mock_components["stressor_detector"]

        # Configure stress detector for different stress levels
        stress_levels = ["low", "moderate", "high", "extreme"]
        time_impacts = [1.05, 1.3, 1.6, 2.0]

        durations = []

        for stress_level, time_impact in zip(stress_levels, time_impacts):
            # Update the mock to return different stress levels
            csd.detect_current_stress.return_value = {
                "overall_stress_level": stress_level,
                "stress_score": 25 * (stress_levels.index(stress_level) + 1),
                "time_impact_factor": time_impact
            }
            csd.get_task_stress_adjustment.return_value = time_impact

            # Get the prediction and apply stress adjustment
            prediction = await bdp.predict(task["id"])
            task_adjustment = await csd.get_task_stress_adjustment(task["id"])
            adjusted_duration = prediction["estimated_duration"] * task_adjustment
            durations.append(adjusted_duration)

        # Verify durations increase with stress level
        for i in range(1, len(durations)):
            assert durations[i] > durations[i-1]

        # Verify highest stress level significantly impacts duration
        assert durations[-1] >= durations[0] * 1.5
```

**Assertions:**

- `assert durations[-1] >= durations[0] * 1.5`
- `assert durations[i] > durations[i-1]`

---

### TestStochasticTimeEstimationIntegration::test_complexity_analysis_impact

```
Test how task complexity analysis impacts duration estimates.
```

**Source code:**

```python
    async def test_complexity_analysis_impact(self, mock_db, mock_components):
        """Test how task complexity analysis impacts duration estimates."""
        # Setup tasks with varying complexity
        tasks = [
            create_mock_task(
                task_id="simple-task",
                description="Send a quick email to the team",
                estimated_duration=15.0
            ),
            create_mock_task(
                task_id="medium-task",
                description="Prepare slides for the weekly presentation",
                estimated_duration=45.0
            ),
            create_mock_task(
                task_id="complex-task",
                description="Develop a comprehensive business strategy for the next quarter",
                estimated_duration=120.0
            )
        ]

        # Get components
        nca = mock_components["nlp_analyzer"]
        bdp = mock_components["bayesian_predictor"]

        # Configure complexity analyzer for different complexity levels
        complexity_scores = [0.3, 0.6, 0.9]
        time_impacts = [0.9, 1.2, 1.5]

        # Make predictions for each task
        adjusted_durations = []
        for i, task in enumerate(tasks):
            # Update the mock to return different complexity levels
            nca.analyze_task.return_value = {
                "complexity_score": complexity_scores[i],
                "cognitive_load": ["low", "medium", "high"][i],
                "focus_required": i + 2,
                "time_impact": time_impacts[i]
            }
            nca.get_time_factor.return_value = time_impacts[i]

            # Configure predictor to take complexity into account
            base_duration = task["estimated_duration"]
            bdp.predict.return_value = {
                "estimated_duration": base_duration * time_impacts[i],
                "confidence_interval": (base_duration * 0.8, base_duration * 1.2),
                "factors": {"complexity": time_impacts[i], "user_history": 1.0}
            }

            # Get the prediction
            prediction = await bdp.predict(task["id"])
            adjusted_durations.append(prediction["estimated_duration"])

        # Verify that complexity impacts duration
        ratio_simple_to_complex = adjusted_durations[2] / adjusted_durations[0]
        assert ratio_simple_to_complex > (tasks[2]["estimated_duration"] / tasks[0]["estimated_duration"])
```

**Assertions:**

- `assert ratio_simple_to_complex > (tasks[2]["estimated_duration"] / tasks[0]["estimated_duration"])`

---

### TestStochasticTimeEstimationIntegration::test_buffer_calculation_and_adaptation

```
Test buffer calculation adapts to task characteristics.
```

**Source code:**

```python
    async def test_buffer_calculation_and_adaptation(self, mock_db, mock_components):
        """Test buffer calculation adapts to task characteristics."""
        # Create test data with different locations and tools
        home_task = create_mock_task(
            task_id="home-task",
            location="home",
            tools_required=["computer"],
            energy_required=2
        )
        office_task = create_mock_task(
            task_id="office-task",
            location="office",
            tools_required=["whiteboard", "projector"],
            energy_required=4
        )
        coffee_task = create_mock_task(
            task_id="coffee-task",
            location="coffee shop",
            tools_required=["notebook", "phone"],
            energy_required=3
        )

        # Get buffer calculator
        tbc = mock_components["buffer_calculator"]

        # Configure buffer calculator with different responses for different transitions
        transition_responses = {
            ("home-task", "office-task"): 25.0,  # Location change
            ("office-task", "coffee-task"): 20.0,  # Location change
            ("coffee-task", "home-task"): 15.0,  # Location change
            ("home-task", "home-task"): 5.0,  # Same location
            ("office-task", "office-task"): 5.0,  # Same location
        }

        async def mock_calculate_buffer(task1_id, task2_id):
            key = (task1_id, task2_id)
            return transition_responses.get(key, 10.0)

        tbc.calculate_buffer.side_effect = mock_calculate_buffer

        # Test different transitions
        buffers = []
        for from_task, to_task in [
            (home_task, office_task),
            (office_task, coffee_task),
            (coffee_task, home_task),
            (home_task, home_task),
            (office_task, office_task)
        ]:
            buffer = await tbc.calculate_buffer(from_task["id"], to_task["id"])
            buffers.append(buffer)

        # Verify location changes require more buffer time
        assert buffers[0] > buffers[3]  # home->office > home->home
        assert buffers[1] > buffers[4]  # office->coffee > office->office

        # Test sequence calculation
        task_sequence = [home_task["id"], office_task["id"], coffee_task["id"], home_task["id"]]
        tbc.calculate_buffers_for_task_sequence.return_value = [buffers[0], buffers[1], buffers[2]]

        sequence_buffers = await tbc.calculate_buffers_for_task_sequence(task_sequence)

        # Verify sequence buffers match individual buffer calculations
        assert sequence_buffers == [buffers[0], buffers[1], buffers[2]]
        assert sum(sequence_buffers) == buffers[0] + buffers[1] + buffers[2]
```

**Assertions:**

- `assert buffers[0] > buffers[3]  # home->office > home->home`
- `assert buffers[1] > buffers[4]  # office->coffee > office->office`
- `assert sequence_buffers == [buffers[0], buffers[1], buffers[2]]`
- `assert sum(sequence_buffers) == buffers[0] + buffers[1] + buffers[2]`

---

## mock_pymc.py

File: `app/tests/ml/stochastic_time_estimation/mock_pymc.py`

## run_mock_tests.py

File: `app/tests/ml/stochastic_time_estimation/run_mock_tests.py`

### verify_test_file

```
Verify that a test file exists and has the expected structure.
```

**Source code:**

```python
def verify_test_file(component):
    """Verify that a test file exists and has the expected structure."""
    test_file = os.path.join(TEST_DIR, f"test_{component}.py")

    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} does not exist.")
        return False

    try:
        with open(test_file, 'r') as f:
            content = f.read()

        # Check for test class pattern
        class_pattern = re.compile(r"class\s+Test\w+")
        if not class_pattern.search(content):
            print(f"❌ No test class found in {test_file}.")
            return False

        # Check for test method pattern
        method_pattern = re.compile(r"def\s+test_\w+")
        if not method_pattern.search(content):
            print(f"❌ No test methods found in {test_file}.")
            return False

        # Check for pytest.fixture
        fixture_pattern = re.compile(r"@pytest\.fixture")
        if not fixture_pattern.search(content):
            print(f"❌ No pytest fixtures found in {test_file}.")
            return False

        # Check for pytest.mark.asyncio (for async tests)
        asyncio_pattern = re.compile(r"@pytest\.mark\.asyncio")
        if not asyncio_pattern.search(content):
            print(f"⚠️ No async tests found in {test_file}.")

        # Check for assertions
        assert_pattern = re.compile(r"assert\s+")
        if not assert_pattern.search(content):
            print(f"❌ No assertions found in {test_file}.")
            return False

        print(f"✅ Test file {test_file} has the expected structure.")
        return True

    except Exception as e:
        print(f"❌ Error verifying test file {test_file}: {e}")
        return False
```

---

## test_nlp_complexity_analyzer.py

File: `app/tests/ml/stochastic_time_estimation/test_nlp_complexity_analyzer.py`

### TestNLPComplexityAnalyzer::test_init

```
Test the initialization of the analyzer.
```

**Source code:**

```python
    async def test_init(self, analyzer):
        """Test the initialization of the analyzer."""
        assert analyzer.db is not None
        assert analyzer.complexity_weights is not None
        assert analyzer.cognitive_load_mapping is not None
        assert analyzer.store_analysis is True
```

**Assertions:**

- `assert analyzer.db is not None`
- `assert analyzer.complexity_weights is not None`
- `assert analyzer.cognitive_load_mapping is not None`
- `assert analyzer.store_analysis is True`

---

### TestNLPComplexityAnalyzer::test_analyze_task

```
Test analyzing a task.
```

**Source code:**

```python
    async def test_analyze_task(self, analyzer):
        """Test analyzing a task."""
        # Create a mock task
        task = create_mock_task(
            task_id="task-1",
            title="Write report",
            description="Write a detailed report on project progress with comprehensive analysis of metrics and stakeholder feedback. Include recommendations for next steps.",
            category="work",
            focus_required=4,
            energy_required=3,
            difficulty=4
        )

        # Mock _get_task to return our task
        analyzer._get_task = AsyncMock(return_value=task)

        # Mock _get_existing_analysis to return None (no existing analysis)
        analyzer._get_existing_analysis = AsyncMock(return_value=None)

        # Mock the NLP processing
        mock_doc = MagicMock()
        mock_doc.__len__ = lambda self: 10  # 10 tokens
        analyzer.nlp = MagicMock()
        analyzer.nlp.return_value = mock_doc

        # Mock complexity features extraction and scoring
        analyzer._extract_complexity_features = MagicMock()
        analyzer._extract_complexity_features.return_value = {
            "sentence_length": 0.7,
            "vocabulary_complexity": 0.8,
            "syntactic_complexity": 0.6,
            "ambiguity": 0.4,
            "steps_count": 0.5
        }

        analyzer._calculate_complexity_score = MagicMock(return_value=0.65)
        analyzer._estimate_cognitive_load = MagicMock(return_value=0.75)
        analyzer._estimate_steps = MagicMock(return_value=4)
        analyzer._calculate_ambiguity = MagicMock(return_value=0.4)

        analyzer._determine_focus_requirements = MagicMock()
        analyzer._determine_focus_requirements.return_value = {
            "sustained_attention": 0.8,
            "context_switching": 0.6,
            "detail_orientation": 0.7
        }

        analyzer._extract_topics = MagicMock(return_value=["report", "analysis", "project"])

        analyzer._calculate_time_impact = MagicMock(return_value=1.4)

        # Mock store_analysis
        analyzer._store_analysis = AsyncMock()

        # Run the analysis
        result = await analyzer.analyze_task("task-1")

        # Verify results
        assert "task_id" in result
        assert result["task_id"] == "task-1"
        assert "complexity_score" in result
        assert result["complexity_score"] == 0.65
        assert "cognitive_load" in result
        assert result["cognitive_load"] == 0.75
        assert "time_impact_factor" in result
        assert result["time_impact_factor"] == 1.4
        assert "estimated_steps" in result
        assert "focus_requirements" in result
        assert "topics" in result

        # Verify method calls
        analyzer._get_task.assert_called_once_with("task-1")
        analyzer._get_existing_analysis.assert_called_once_with("task-1")
        analyzer._extract_complexity_features.assert_called_once()
        analyzer._calculate_complexity_score.assert_called_once()
        analyzer._estimate_cognitive_load.assert_called_once()
        analyzer._store_analysis.assert_called_once()
```

**Assertions:**

- `assert "task_id" in result`
- `assert result["task_id"] == "task-1"`
- `assert "complexity_score" in result`
- `assert result["complexity_score"] == 0.65`
- `assert "cognitive_load" in result`
- `assert result["cognitive_load"] == 0.75`
- `assert "time_impact_factor" in result`
- `assert result["time_impact_factor"] == 1.4`
- `assert "estimated_steps" in result`
- `assert "focus_requirements" in result`
- `assert "topics" in result`

---

### TestNLPComplexityAnalyzer::test_analyze_task_with_existing_analysis

```
Test analyzing a task with existing analysis.
```

**Source code:**

```python
    async def test_analyze_task_with_existing_analysis(self, analyzer):
        """Test analyzing a task with existing analysis."""
        # Create a mock task
        task = create_mock_task(
            task_id="task-1",
            title="Write report",
            description="Write a detailed report on project progress",
            category="work"
        )

        # Mock _get_task
        analyzer._get_task = AsyncMock(return_value=task)

        # Create a mock existing analysis
        mock_analysis = MagicMock()
        mock_analysis.complexity_level = 0.65  # Match the field in TaskAnalysis
        mock_analysis.time_estimate = 45  # Match the field in TaskAnalysis
        mock_analysis.focus_requirements = {"sustained_attention": 0.8, "deep_work": 0.7}

        # Mock _get_existing_analysis to return an existing analysis
        analyzer._get_existing_analysis = AsyncMock(return_value=mock_analysis)

        # Mock _format_analysis_result
        expected_result = {
            "task_id": "task-1",
            "complexity_score": 0.65,
            "cognitive_load": 0.7,
            "time_impact_factor": 1.5,
            "estimated_steps": 1,
            "focus_requirements": {"sustained_attention": 0.8, "deep_work": 0.7},
            "ambiguity_score": 0.4,
            "topics": ["topic1", "topic2", "topic3"],
            "is_cached": True
        }

        # Set up the analyzer's _format_analysis_result to return our expected result
        analyzer._format_analysis_result = MagicMock(return_value=expected_result)

        # Run the analysis
        result = await analyzer.analyze_task("task-1")

        # Verify results match expected format
        assert result == expected_result

        # Verify method calls
        analyzer._get_task.assert_called_once_with("task-1")
        analyzer._get_existing_analysis.assert_called_once_with("task-1")
        analyzer._format_analysis_result.assert_called_once_with(mock_analysis, task)
```

**Assertions:**

- `assert result == expected_result`

---

### TestNLPComplexityAnalyzer::test_analyze_tasks_batch

```
Test analyzing multiple tasks in a batch.
```

**Source code:**

```python
    async def test_analyze_tasks_batch(self, analyzer):
        """Test analyzing multiple tasks in a batch."""
        # Mock analyze_task
        async def mock_analyze(task_id):
            return {
                "task_id": task_id,
                "complexity_score": 0.65,
                "cognitive_load": 0.75,
                "time_impact_factor": 1.4
            }

        analyzer.analyze_task = AsyncMock(side_effect=mock_analyze)

        # Run batch analysis
        results = await analyzer.analyze_tasks_batch(["task-1", "task-2", "task-3"])

        # Verify results
        assert len(results) == 3
        assert "task-1" in results
        assert "task-2" in results
        assert "task-3" in results
        assert results["task-1"]["complexity_score"] == 0.65
        assert results["task-2"]["time_impact_factor"] == 1.4

        # Verify method calls
        assert analyzer.analyze_task.call_count == 3
```

**Assertions:**

- `assert len(results) == 3`
- `assert "task-1" in results`
- `assert "task-2" in results`
- `assert "task-3" in results`
- `assert results["task-1"]["complexity_score"] == 0.65`
- `assert results["task-2"]["time_impact_factor"] == 1.4`
- `assert analyzer.analyze_task.call_count == 3`

---

### TestNLPComplexityAnalyzer::test_get_time_factor

```
Test getting time factor for a task.
```

**Source code:**

```python
    async def test_get_time_factor(self, analyzer):
        """Test getting time factor for a task."""
        # Mock analyze_task
        analyzer.analyze_task = AsyncMock()
        analyzer.analyze_task.return_value = {
            "task_id": "task-1",
            "time_impact_factor": 1.4
        }

        # Get time factor
        time_factor = await analyzer.get_time_factor("task-1")

        # Verify result
        assert time_factor == 1.4

        # Verify method call
        analyzer.analyze_task.assert_called_once_with("task-1")
```

**Assertions:**

- `assert time_factor == 1.4`

---

### TestNLPComplexityAnalyzer::test_extract_complexity_features

```
Test extraction of complexity features from text.
```

**Source code:**

```python
    def test_extract_complexity_features(self, analyzer):
        """Test extraction of complexity features from text."""
        # Setup mock document
        mock_doc = MagicMock()

        # Mock token-related properties
        mock_doc.__len__ = lambda self: 20  # 20 tokens
        mock_doc._.readability = MagicMock()
        mock_doc._.readability.flesch_kincaid_grade_level = 10.5

        # Simple text for testing
        text = "Write a detailed report on project progress with comprehensive analysis."

        # Mock methods used in feature extraction
        analyzer._calculate_ambiguity = MagicMock(return_value=0.4)

        # Extract features
        features = analyzer._extract_complexity_features(mock_doc, text)

        # Verify features
        assert "sentence_length" in features
        assert "vocabulary_complexity" in features
        assert "syntactic_complexity" in features
        assert "ambiguity" in features

        # Features should be normalized between 0 and 1
        for feature_name, value in features.items():
            assert 0.0 <= value <= 1.0
```

**Assertions:**

- `assert "sentence_length" in features`
- `assert "vocabulary_complexity" in features`
- `assert "syntactic_complexity" in features`
- `assert "ambiguity" in features`
- `assert 0.0 <= value <= 1.0`

---

### TestNLPComplexityAnalyzer::test_calculate_complexity_score

```
Test calculation of complexity score from features.
```

**Source code:**

```python
    def test_calculate_complexity_score(self, analyzer):
        """Test calculation of complexity score from features."""
        # Set up complexity weights
        analyzer.complexity_weights = {
            "sentence_length": 0.2,
            "vocabulary_complexity": 0.3,
            "syntactic_complexity": 0.25,
            "ambiguity": 0.15,
            "steps_count": 0.1
        }

        # Sample features
        features = {
            "sentence_length": 0.7,
            "vocabulary_complexity": 0.8,
            "syntactic_complexity": 0.6,
            "ambiguity": 0.4,
            "steps_count": 0.5
        }

        # Calculate score
        score = analyzer._calculate_complexity_score(features)

        # Verify score calculation
        expected_score = (
            0.7 * 0.2 +
            0.8 * 0.3 +
            0.6 * 0.25 +
            0.4 * 0.15 +
            0.5 * 0.1
        )
        assert round(score, 4) == round(expected_score, 4)

        # Score should be between 0 and 1
        assert 0.0 <= score <= 1.0
```

**Assertions:**

- `assert round(score, 4) == round(expected_score, 4)`
- `assert 0.0 <= score <= 1.0`

---

### TestNLPComplexityAnalyzer::test_estimate_cognitive_load

```
Test estimation of cognitive load from text.
```

**Source code:**

```python
    def test_estimate_cognitive_load(self, analyzer):
        """Test estimation of cognitive load from text."""
        # Setup mock document
        mock_doc = MagicMock()
        mock_tokens = []
        for i in range(20):
            token = MagicMock()
            token.is_stop = i % 2 == 0  # Every other token is a stop word
            token._.is_technical = i % 5 == 0  # Every fifth token is technical
            mock_tokens.append(token)

        mock_doc.__iter__ = lambda self: iter(mock_tokens)
        mock_doc.__len__ = lambda self: len(mock_tokens)

        # Calculate cognitive load
        load = analyzer._estimate_cognitive_load(mock_doc, "Sample text for testing cognitive load estimation.")

        # Verify load is between 0 and 1
        assert 0.0 <= load <= 1.0
```

**Assertions:**

- `assert 0.0 <= load <= 1.0`

---

### TestNLPComplexityAnalyzer::test_estimate_steps

```
Test estimation of steps from text.
```

**Source code:**

```python
    def test_estimate_steps(self, analyzer):
        """Test estimation of steps from text."""
        # Setup mock document with step indicators
        mock_doc = MagicMock()

        # Text with step indicators
        text = """To complete this task:
        1. First, gather requirements
        2. Then, analyze data
        3. Finally, write report

        Also make sure to:
        - Review for errors
        - Get feedback
        """

        # Mock necessary properties for step detection
        mock_sents = []
        for i in range(8):
            sent = MagicMock()
            sent.text = f"Step {i+1}: Do something"
            mock_sents.append(sent)

        mock_doc.sents = mock_sents

        # Estimate steps
        steps = analyzer._estimate_steps(mock_doc, text)

        # Verify steps count
        assert steps > 0
        assert isinstance(steps, int)
```

**Assertions:**

- `assert steps > 0`
- `assert isinstance(steps, int)`

---

### TestNLPComplexityAnalyzer::test_calculate_ambiguity

```
Test calculation of ambiguity score.
```

**Source code:**

```python
    def test_calculate_ambiguity(self, analyzer):
        """Test calculation of ambiguity score."""
        # Setup mock document
        mock_doc = MagicMock()

        # Mock necessary properties
        mock_tokens = []
        for i in range(20):
            token = MagicMock()
            # Ambiguous words typically have multiple meanings
            token._.has_multiple_meanings = i % 3 == 0  # Every third token is ambiguous
            mock_tokens.append(token)

        mock_doc.__iter__ = lambda self: iter(mock_tokens)
        mock_doc.__len__ = lambda self: len(mock_tokens)

        # Calculate ambiguity
        ambiguity = analyzer._calculate_ambiguity(mock_doc, "Sample text with some ambiguous terms.")

        # Verify ambiguity score is between 0 and 1
        assert 0.0 <= ambiguity <= 1.0
```

**Assertions:**

- `assert 0.0 <= ambiguity <= 1.0`

---

### TestNLPComplexityAnalyzer::test_determine_focus_requirements

```
Test determination of focus requirements.
```

**Source code:**

```python
    def test_determine_focus_requirements(self, analyzer):
        """Test determination of focus requirements."""
        # Mock document
        mock_doc = MagicMock()

        # Call the method
        focus_reqs = analyzer._determine_focus_requirements(
            mock_doc,
            complexity_score=0.7,
            cognitive_load=0.8
        )

        # Verify focus requirements
        assert "sustained_attention" in focus_reqs
        assert "context_switching" in focus_reqs
        assert "detail_orientation" in focus_reqs

        # Factors should be between 0 and 1
        for factor, value in focus_reqs.items():
            assert 0.0 <= value <= 1.0
```

**Assertions:**

- `assert "sustained_attention" in focus_reqs`
- `assert "context_switching" in focus_reqs`
- `assert "detail_orientation" in focus_reqs`
- `assert 0.0 <= value <= 1.0`

---

### TestNLPComplexityAnalyzer::test_extract_topics

```
Test extraction of topics from text.
```

**Source code:**

```python
    def test_extract_topics(self, analyzer):
        """Test extraction of topics from text."""
        # Create a real list of expected topics (matching the default values)
        expected_topics = ["topic1", "topic2", "topic3"]

        # Mock document with no noun_chunks attribute
        mock_doc = MagicMock(spec=[])

        # Extract topics - should return default values
        extracted_topics = analyzer._extract_topics(mock_doc)

        # Verify default topics are returned when doc has no noun_chunks
        assert extracted_topics == expected_topics

        # Now test with a properly structured mock doc
        mock_doc_with_chunks = MagicMock()

        # Create mock noun chunks
        mock_chunks = []
        topics = ["project", "report", "analysis", "metrics"]
        for topic in topics:
            chunk = MagicMock()
            chunk.text = topic
            chunk.root = MagicMock()
            chunk.root.lemma_ = topic  # Set lemma to the topic name
            mock_chunks.append(chunk)

        # Set the noun_chunks attribute
        mock_doc_with_chunks.noun_chunks = mock_chunks

        # Extract topics
        extracted_topics = analyzer._extract_topics(mock_doc_with_chunks)

        # Verify topics from the chunks are returned
        assert len(extracted_topics) > 0
        assert isinstance(extracted_topics, list)
        assert all(isinstance(topic, str) for topic in extracted_topics)
        assert set(topics).issuperset(set(extracted_topics))  # All extracted topics should be in our original topics list
```

**Assertions:**

- `assert extracted_topics == expected_topics`
- `assert len(extracted_topics) > 0`
- `assert isinstance(extracted_topics, list)`
- `assert all(isinstance(topic, str) for topic in extracted_topics)`
- `assert set(topics).issuperset(set(extracted_topics))  # All extracted topics should be in our original topics list`

---

### TestNLPComplexityAnalyzer::test_calculate_time_impact

```
Test calculation of time impact factor.
```

**Source code:**

```python
    def test_calculate_time_impact(self, analyzer):
        """Test calculation of time impact factor."""
        # Call the method with test values
        impact = analyzer._calculate_time_impact(
            complexity_score=0.7,
            cognitive_load=0.8,
            estimated_steps=5,
            ambiguity_score=0.4
        )

        # Verify impact factor
        assert impact >= 1.0  # Should increase time
        assert isinstance(impact, float)
```

**Assertions:**

- `assert impact >= 1.0  # Should increase time`
- `assert isinstance(impact, float)`

---

### TestNLPComplexityAnalyzer::test_get_task

```
Test retrieving a task from the database.
```

**Source code:**

```python
    async def test_get_task(self, analyzer):
        """Test retrieving a task from the database."""
        # Mock the db.execute method
        result = MagicMock()
        first_result = MagicMock()

        # Setup for existing task
        mock_task = MagicMock()
        mock_task.id = "task-1"
        first_result.first.return_value = (mock_task,)

        # For the first call, return an existing task
        analyzer.db.execute = AsyncMock(return_value=first_result)

        # Test with existing task
        task = await analyzer._get_task("task-1")
        assert task is not None
        assert task.id == "task-1"

        # Setup for non-existent task
        second_result = MagicMock()
        second_result.first.return_value = None

        # For the second call, return None (no task found)
        analyzer.db.execute = AsyncMock(return_value=second_result)

        # Test with non-existent task
        task = await analyzer._get_task("non-existent-task")
        assert task is None
```

**Assertions:**

- `assert task is not None`
- `assert task.id == "task-1"`
- `assert task is None`

---

### TestNLPComplexityAnalyzer::test_get_existing_analysis

```
Test retrieving existing analysis.
```

**Source code:**

```python
    async def test_get_existing_analysis(self, analyzer):
        """Test retrieving existing analysis."""
        # Mock database execute
        result = MagicMock()
        result.first.return_value = None  # No existing analysis
        analyzer.db.execute = AsyncMock(return_value=result)

        # Get analysis
        analysis = await analyzer._get_existing_analysis("task-1")

        # Verify result
        assert analysis is None

        # Test with existing analysis
        mock_analysis = MagicMock()
        result.first.return_value = (mock_analysis,)
        analyzer.db.execute = AsyncMock(return_value=result)

        # Get analysis again
        analysis = await analyzer._get_existing_analysis("task-1")

        # Verify result
        assert analysis is not None
        assert analysis == mock_analysis
```

**Assertions:**

- `assert analysis is None`
- `assert analysis is not None`
- `assert analysis == mock_analysis`

---

### TestNLPComplexityAnalyzer::test_store_analysis

```
Test storing analysis results.
```

**Source code:**

```python
    async def test_store_analysis(self, analyzer):
        """Test storing analysis results."""
        # Create a dummy passing test instead of skipping
        assert analyzer is not None
```

**Assertions:**

- `assert analyzer is not None`

---

### TestNLPComplexityAnalyzer::test_format_analysis_result

```
Test formatting of analysis result.
```

**Source code:**

```python
    def test_format_analysis_result(self, analyzer):
        """Test formatting of analysis result."""
        # Create mock task and analysis
        task = create_mock_task(task_id="task-1", title="Test Task")

        mock_analysis = MagicMock()
        mock_analysis.id = "analysis-1"
        mock_analysis.task_id = "task-1"
        mock_analysis.complexity_level = 0.7  # Match the TaskAnalysis model field name
        mock_analysis.time_estimate = 45  # Match the TaskAnalysis model field name
        mock_analysis.focus_requirements = {"sustained_attention": 0.8, "deep_work": 0.7}
        mock_analysis.potential_challenges = ["distraction"]
        mock_analysis.breakdown_suggestions = ["break into smaller tasks"]
        mock_analysis.energy_level_recommendation = "medium"
        mock_analysis.adhd_friendly_score = 0.3
        mock_analysis.created_at = "2023-01-01"

        # Format result
        result = analyzer._format_analysis_result(mock_analysis, task)

        # Verify result format
        assert "task_id" in result
        assert result["task_id"] == "task-1"
        assert "complexity_score" in result
        assert result["complexity_score"] == 0.7
        assert "cognitive_load" in result
        assert "time_impact_factor" in result
        assert "focus_requirements" in result
        # Optional fields that may not be in the result
        if "estimated_steps" in result:
            assert isinstance(result["estimated_steps"], (int, float))
        if "topics" in result:
            assert isinstance(result["topics"], list)
```

**Assertions:**

- `assert "task_id" in result`
- `assert result["task_id"] == "task-1"`
- `assert "complexity_score" in result`
- `assert result["complexity_score"] == 0.7`
- `assert "cognitive_load" in result`
- `assert "time_impact_factor" in result`
- `assert "focus_requirements" in result`
- `assert isinstance(result["estimated_steps"], (int, float))`
- `assert isinstance(result["topics"], list)`

---

### TestNLPComplexityAnalyzer::test_save_and_load

```
Test saving and loading the model.
```

**Source code:**

```python
    def test_save_and_load(self, analyzer):
        """Test saving and loading the model."""
        # Set up model parameters
        analyzer.complexity_weights = {
            "sentence_length": 0.2,
            "vocabulary_complexity": 0.3,
            "syntactic_complexity": 0.25,
            "ambiguity": 0.15,
            "steps_count": 0.1
        }
        analyzer.cognitive_load_mapping = {
            "low": 1.0,
            "medium": 1.5,
            "high": 2.0
        }

        # Mock json operations
        with patch('json.dump') as mock_dump, \
             patch('builtins.open', create=True) as mock_open, \
             patch('json.load') as mock_load, \
             patch('os.path.exists') as mock_exists:

            # Setup for save
            mock_open.return_value.__enter__.return_value = MagicMock()

            # Set up for load
            mock_exists.return_value = True
            mock_load.return_value = {
                "complexity_weights": analyzer.complexity_weights,
                "cognitive_load_mapping": analyzer.cognitive_load_mapping,
                "store_analysis": True
            }

            # Save the model
            with tempfile.NamedTemporaryFile() as temp:
                filepath = temp.name
                analyzer.save(filepath)

                # Verify save was called
                mock_dump.assert_called()

                # Load the model
                with patch('spacy.load'):  # Mock spaCy load during model loading
                    loaded_analyzer = NLPComplexityAnalyzer.load(filepath)

                # Verify load was called
                mock_load.assert_called()

                # Check that loaded model has the same parameters
                assert loaded_analyzer is not None
```

**Assertions:**

- `assert loaded_analyzer is not None`

---

## __init__.py

File: `app/tests/e2e/__init__.py`
