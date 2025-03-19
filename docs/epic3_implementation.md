# Epic 3: Proactive Forgetfulness and Distraction Mitigation - Implementation Details

## Architecture Overview

Epic 3 implements a service-based architecture with three primary components that work together to address forgetfulness and distraction issues common in ADHD:

1. **CommitmentDetectionService**: Identifies commitments from text sources
2. **DialogueSystemService**: Provides interactive dialogue for commitment management
3. **SmartReminderService**: Delivers contextually-aware reminders

The implementation follows a modular design pattern, allowing each component to be independently tested, maintained, and extended.

## Architecture Diagram

```
┌───────────────────────┐     ┌───────────────────────┐     ┌───────────────────────┐
│                       │     │                       │     │                       │
│  User Input Sources   │────▶│  CommitmentDetection  │────▶│      Database         │
│  (Text, Voice, Email) │     │       Service         │     │  (Commitment Storage) │
│                       │     │                       │     │                       │
└───────────────────────┘     └───────────────────────┘     └───────────────────────┘
                                        │                              │
                                        │                              │
                                        ▼                              ▼
┌───────────────────────┐     ┌───────────────────────┐     ┌───────────────────────┐
│                       │     │                       │     │                       │
│  Dialogue System      │◀───▶│  Context Management   │◀───▶│  Smart Reminder       │
│  Interface            │     │  Service              │     │  Service              │
│                       │     │                       │     │                       │
└───────────────────────┘     └───────────────────────┘     └───────────────────────┘
                                                                     │
                                                                     │
                                                                     ▼
                                                      ┌───────────────────────┐
                                                      │                       │
                                                      │  Notification         │
                                                      │  Service              │
                                                      │                       │
                                                      └───────────────────────┘
```

## Data Flow

1. **Input Processing Flow**:
   - User text is captured from multiple sources
   - Text is processed through CommitmentDetectionService
   - Detected commitments are stored in the database
   - Confidence scores determine whether commitments are auto-saved or presented for confirmation

2. **Dialogue System Flow**:
   - User initiates dialogue or system proactively engages user
   - Context management service maintains conversation state
   - Dialogue system retrieves relevant commitments
   - System generates natural language responses
   - New commitments detected during dialogue are processed by CommitmentDetectionService

3. **Reminder Flow**:
   - SmartReminderService regularly evaluates stored commitments
   - Contextual factors and priority levels are assessed
   - Reminder timing is calculated based on adaptive algorithms
   - Notifications are sent through appropriate channels
   - User response to reminders is captured and used for learning

## Component Details

### CommitmentDetectionService

**Purpose**: Detect explicit and implicit commitments from various text sources including journal entries, chat messages, and emails.

**Implementation Location**: `app/services/commitment_detection_service.py`

**Key Methods**:
- `detect_commitments(text)`: Main detection pipeline
- `_detect_with_regex(text)`: Pattern-based detection using regex
- `_detect_with_llm(text)`: LLM-based detection for more complex or implicit commitments
- `_merge_commitment_detections(commitments)`: Deduplication and confidence boosting for similar commitments
- `_extract_temporal_elements(text, commitment)`: Extract due dates and time frames
- `_classify_priority(commitment, context)`: Determine commitment priority

**Dependencies**:
- LLM service for advanced text analysis
- Database for commitment storage
- NLP utilities for text processing

**Algorithms**:
- Hybrid detection approach combining rule-based and ML-based methods
- Confidence scoring with source-based weighting
- Semantic similarity for deduplication

**Error Handling**:
- Invalid input handling with descriptive error messages
- LLM service failure fallback to regex-only detection
- Confidence thresholds to prevent false positives

**Performance Optimizations**:
- Caching of similar text patterns
- Batch processing for multiple commitment detection
- Asynchronous LLM calls to prevent blocking

### DialogueSystemService

**Purpose**: Provide natural language interface for commitment management, allowing users to check what they might have forgotten.

**Implementation Location**: `app/services/dialogue_system_service.py`

**Key Methods**:
- `create_session(user_id)`: Initialize dialogue session
- `process_message(session_id, message)`: Process user message and generate response
- `_generate_system_response(session, context)`: Generate context-aware response
- `_detect_commitments_in_message(message)`: Extract commitments from user input
- `_update_session_context(session, message, detected_commitments)`: Maintain conversation context

**Dependencies**:
- CommitmentDetectionService for identifying commitments in dialogue
- Database for session storage and retrieval
- NLP utilities for language understanding

**Algorithms**:
- Dialogue state tracking
- Context-aware response generation
- Commitment extraction during conversation

**Error Handling**:
- Session expiration management
- Invalid message format recovery
- Fallback responses for uncertain contexts

**Performance Optimizations**:
- Context caching to reduce database access
- Response template pre-compilation
- Lazy loading of language models

### SmartReminderService

**Purpose**: Deliver contextually-aware reminders for commitments, optimized for ADHD users' needs.

**Implementation Location**: `app/services/smart_reminder_service.py`

**Key Methods**:
- `process_smart_reminders(user_id)`: Process all pending reminders
- `_prioritize_reminders(reminders)`: Prioritize reminders by importance, urgency, and context
- `get_contextual_reminders(user_id, context)`: Get context-relevant reminders
- `send_commitment_reminder(user_id, commitment, context)`: Send personalized reminder
- `_generate_reminder_content(commitment, context)`: Create contextually-relevant reminder content

**Dependencies**:
- NotificationService for delivering reminders
- CommitmentDetectionService for accessing commitment data
- Database for commitment and context storage

**Algorithms**:
- Multi-factor prioritization algorithm
- Contextual relevance scoring
- Adaptive timing based on user patterns and context

**Error Handling**:
- Notification delivery failure retry logic
- Missing context graceful degradation
- Rate limiting to prevent notification fatigue

**Performance Optimizations**:
- Batch processing of reminders
- Caching of user preferences
- Precalculation of common reminder templates

## Data Models

### CommitmentModel

**Purpose**: Store detected commitments and their metadata.

**Implementation Location**: `app/models/commitment_model.py`

**Fields**:
- `id`: Unique identifier
- `user_id`: Associated user
- `text`: Commitment text
- `source`: Source of the commitment (journal, chat, email, etc.)
- `confidence`: Detection confidence (0-1)
- `due_date`: Due date/time
- `time_frame`: Time frame description
- `priority`: Priority level (high, medium, low)
- `cross_references`: Related commitments (JSON field)
- `related_task_id`: Associated task
- `status`: Current status (pending, completed, etc.)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Indexes**:
- `(user_id, status)`: For efficient retrieval of active commitments
- `(user_id, due_date)`: For time-based queries
- `(user_id, priority)`: For priority-based filtering

**Constraints**:
- Foreign key to User table
- Check constraints on priority values
- Null constraints for required fields

### DialogueSessionModel

**Purpose**: Maintain dialogue session state.

**Implementation Location**: `app/models/dialogue_session_model.py`

**Fields**:
- `id`: Session identifier
- `user_id`: Associated user
- `context`: Current conversation context (JSON field)
- `message_history`: Previous messages
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `last_active`: Last activity timestamp

**Indexes**:
- `(user_id, last_active)`: For active session retrieval
- `session_id`: For direct session access

**Constraints**:
- Foreign key to User table
- Automatic session expiration logic
- Maximum message history size

### ReminderModel

**Purpose**: Store reminder information.

**Implementation Location**: `app/models/reminder_model.py`

**Fields**:
- `id`: Unique identifier
- `commitment_id`: Associated commitment
- `user_id`: Associated user
- `scheduled_time`: Delivery time
- `context`: Delivery context (JSON field)
- `priority`: Reminder priority
- `status`: Delivery status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Indexes**:
- `(user_id, scheduled_time)`: For time-based processing
- `(user_id, status)`: For status filtering
- `commitment_id`: For commitment-based lookup

**Constraints**:
- Foreign keys to User and Commitment tables
- Check constraints on status values
- Scheduling time validation

## Database Migrations

Migrations for Epic 3 data models are located in:
- `app/migrations/versions/20230401_create_commitments.py`
- `app/migrations/versions/20230402_create_dialogue_sessions.py`
- `app/migrations/versions/20230403_create_reminders.py`
- `app/migrations/versions/20230415_add_commitment_indexes.py`

To apply migrations:
```bash
alembic upgrade head
```

To generate new migration:
```bash
alembic revision --autogenerate -m "description"
```

## Integration Points

The Epic 3 components integrate with other system components through the following points:

### Database Integration
- All services use the database session for data persistence
- Async database operations support high-performance processing
- Transaction management ensures data consistency

### NLP Service Integration
- CommitmentDetectionService uses NLP utilities for text analysis
- DialogueSystemService uses NLP for language understanding
- Shared NLP models reduce memory footprint

### Task Management Integration
- Commitments can be linked to tasks in the task management system
- Task status updates can affect commitment status
- Bidirectional sync ensures data consistency

### Notification Service Integration
- SmartReminderService uses the notification service for reminder delivery
- Supports multiple notification channels (push, email, in-app)
- Delivery confirmation tracking

## Performance Considerations

### Optimizations
- Caching for frequently accessed commitments
- Asynchronous processing for detection and analysis
- Batch processing for reminders
- Lazy loading of expensive resources

### Scalability
- Services designed for horizontal scaling
- Database indexing optimized for commitment queries
- Efficient context management in dialogue system
- Background workers for reminder processing

### Performance Metrics
- Commitment detection: <500ms per text entry
- Dialogue response: <1s per interaction
- Reminder processing: <5ms per reminder
- Database queries: <50ms for common operations

## Security Considerations

### Data Protection
- All commitment data is encrypted at rest
- Sensitive information is redacted from commitment text
- Personal data access is limited to the owning user

### Authentication & Authorization
- All APIs require proper authentication
- User permissions are verified for each operation
- Rate limiting prevents abuse

### Privacy 
- LLM processing adheres to data minimization principles
- Users can opt out of specific data processing
- Data retention policies automatically clean up old data

### Audit Logging
- All commitment creation and modification is logged
- Reminder delivery has delivery confirmation tracking
- Session activities are recorded for troubleshooting

## Error Handling & Resilience

### Failure Modes
- LLM service unavailability: fallback to simpler detection
- Database connection issues: retry with exponential backoff
- Notification failures: queued for retry

### Circuit Breakers
- Automatic detection of failing dependencies
- Graceful degradation of service capabilities
- Self-healing when dependencies recover

### Monitoring
- Error rate tracking per component
- Performance anomaly detection
- User-impacting failure alerts

## Future Enhancements

While the current implementation meets all acceptance criteria, several enhancements have been identified for future iterations:

1. **Fine-tuned Commitment Models**: Train domain-specific models for improved detection
2. **Mobile Integration**: Add real-time context from mobile devices for better awareness
3. **Voice Interface**: Support multi-modal input including voice commands
4. **Location Awareness**: Add geofencing for location-based reminders
5. **Relationship Visualization**: Create interactive visualizations of commitment relationships
6. **Cross-user Commitments**: Support for shared commitments and team accountability
7. **ML-powered Timing**: Machine learning models for optimal reminder timing
8. **Emotion-aware Responses**: Adapt dialogue tone based on detected user emotions

## Implementation Roadmap

| Phase | Feature | Timeline | Status |
|-------|---------|----------|--------|
| 1 | Core commitment detection | Completed | ✅ |
| 1 | Basic dialogue system | Completed | ✅ |
| 1 | Simple reminders | Completed | ✅ |
| 2 | Enhanced detection accuracy | Completed | ✅ |
| 2 | Context-aware dialogue | Completed | ✅ |
| 2 | Smart timing for reminders | Completed | ✅ |
| 3 | Advanced priority algorithms | Completed | ✅ |
| 3 | Multi-channel notifications | Completed | ✅ |
| 4 | Voice interface | Planned Q2 2023 | 🔄 |
| 4 | Location awareness | Planned Q3 2023 | 📅 |
| 5 | Cross-user commitments | Planned Q4 2023 | 📅 | 