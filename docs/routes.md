# Route System Documentation

## Overview
This document details the routing system for the ADHD Calendar Backend.

## Route Architecture

### Base Router
All routers inherit from `BaseRouter` which provides:
- Request validation
- Response formatting
- Error handling
- Authentication
- Rate limiting
- Logging
- Metrics

### Route Factory
The `RouteFactory` manages route creation:
- Route registration
- Middleware application
- Dependency injection
- Version management
- Documentation generation

## Core Routes

### Task Routes
`TaskRouter` manages task endpoints:
```python
@router.post("/tasks")
async def create_task(
    task: TaskSchema,
    service: TaskService = Depends(get_task_service)
):
    """Create a new task."""
    return await service.create_task(task)

@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service)
):
    """Get task by ID."""
    return await service.get_task(task_id)
```

### Calendar Routes
`CalendarRouter` manages calendar endpoints:
```python
@router.post("/calendar/events")
async def create_event(
    event: CalendarEventSchema,
    service: CalendarService = Depends(get_calendar_service)
):
    """Create a new calendar event."""
    return await service.create_event(event)

@router.get("/calendar/events/{date}")
async def get_events(
    date: datetime,
    service: CalendarService = Depends(get_calendar_service)
):
    """Get events for a specific date."""
    return await service.get_events(date)
```

### Focus Routes
`FocusRouter` manages focus session endpoints:
```python
@router.post("/focus/pomodoro")
async def start_pomodoro(
    session: PomodoroSessionSchema,
    service: PomodoroService = Depends(get_pomodoro_service)
):
    """Start a new pomodoro session."""
    return await service.start_session(session)

@router.post("/focus/body-doubling")
async def create_body_doubling(
    session: BodyDoublingSessionSchema,
    service: BodyDoublingService = Depends(get_body_doubling_service)
):
    """Create a new body doubling session."""
    return await service.create_session(session)
```

## Route Middleware

### Authentication
Protect routes with authentication:
```python
@router.get("/protected", dependencies=[Depends(auth_required)])
async def protected_route():
    """This route requires authentication."""
    return {"message": "Authenticated"}
```

### Rate Limiting
Apply rate limiting:
```python
@router.get("/limited", dependencies=[Depends(rate_limiter)])
async def limited_route():
    """This route is rate limited."""
    return {"message": "Rate limited"}
```

### Validation
Validate request data:
```python
@router.post("/validated")
async def validated_route(
    data: ValidatedSchema = Depends(validate_request)
):
    """This route validates input data."""
    return {"data": data}
```

## Response Formatting

### Success Response
Format successful responses:
```python
@router.get("/success")
async def success_route():
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "data": {"message": "Success"}
        }
    )
```

### Error Response
Format error responses:
```python
@router.get("/error")
async def error_route():
    raise HTTPException(
        status_code=400,
        detail={
            "status": "error",
            "message": "Bad request",
            "code": "BAD_REQUEST"
        }
    )
```

## Route Documentation

### OpenAPI Documentation
Document routes with OpenAPI:
```python
@router.get(
    "/documented",
    response_model=ResponseSchema,
    responses={
        200: {"description": "Successful response"},
        400: {"description": "Bad request"}
    }
)
async def documented_route():
    """
    This route is documented.
    
    Returns:
        ResponseSchema: The response data
    """
    return {"data": "documented"}
```

### Route Tags
Organize routes with tags:
```python
@router.get("/tagged", tags=["category"])
async def tagged_route():
    """This route is tagged."""
    return {"message": "Tagged"}
```

## Route Versioning

### Version Prefix
Version routes with prefixes:
```python
v1_router = APIRouter(prefix="/v1")
v2_router = APIRouter(prefix="/v2")
```

### Version Compatibility
Handle version compatibility:
```python
@router.get("/v1/legacy")
async def legacy_route():
    """Legacy route for v1."""
    return {"version": "1.0"}

@router.get("/v2/updated")
async def updated_route():
    """Updated route for v2."""
    return {"version": "2.0"}
```

## WebSocket Routes

### WebSocket Handlers
Handle WebSocket connections:
```python
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"echo": data})
    except WebSocketDisconnect:
        await websocket.close()
```

### WebSocket Authentication
Authenticate WebSocket connections:
```python
@router.websocket("/ws/auth")
async def auth_websocket(
    websocket: WebSocket,
    token: str = Query(...)
):
    if not verify_token(token):
        await websocket.close()
    await websocket.accept()
```

## Best Practices

### Route Design
1. Use clear, descriptive route paths
2. Follow REST conventions
3. Version routes appropriately
4. Document all routes
5. Use proper HTTP methods

### Security
1. Implement authentication
2. Apply rate limiting
3. Validate input data
4. Handle sensitive data
5. Use HTTPS

### Performance
1. Optimize database queries
2. Cache responses
3. Use async handlers
4. Batch operations
5. Monitor performance

### Error Handling
1. Use proper status codes
2. Provide clear error messages
3. Handle edge cases
4. Log errors properly
5. Return consistent error formats

## Testing

### Route Tests
Test route functionality:
```python
async def test_create_task():
    response = await client.post(
        "/tasks",
        json={"title": "Test Task"}
    )
    assert response.status_code == 200
```

### Integration Tests
Test route integration:
```python
async def test_task_workflow():
    task = await client.post("/tasks", json=task_data)
    event = await client.get(f"/calendar/events/{task.id}")
    assert event is not None
```

### Load Tests
Test route performance:
```python
async def test_route_performance():
    async with client.parallel(10) as parallel:
        responses = await parallel.get("/tasks")
        assert all(r.status_code == 200 for r in responses)
```

## Monitoring

### Route Metrics
Monitor route performance:
```python
@router.get("/monitored")
async def monitored_route():
    with metrics.timer("route_duration"):
        return await process_request()
```

### Health Checks
Implement health check routes:
```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }
```

### Status Routes
Implement status routes:
```python
@router.get("/status")
async def status_check():
    return {
        "api_version": "1.0",
        "database": "connected",
        "cache": "available"
    }
``` 