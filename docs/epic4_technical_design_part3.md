# Epic 4: Technical Design Document - Part 3
# Dynamic Schedule Rebalancing with Circadian Rhythm Optimization

## Data Models and Database Schema

### Database Design

The Dynamic Schedule Rebalancing system relies on a combination of relational and document databases to efficiently store and retrieve different types of data.

#### PostgreSQL Schemas

##### User Profiles

```sql
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    time_zone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    default_work_hours JSONB NOT NULL DEFAULT '{"weekday": {"start": "09:00", "end": "17:00"}, "weekend": {"start": "10:00", "end": "16:00"}}',
    circadian_model_id UUID,
    scheduling_preferences JSONB NOT NULL DEFAULT '{}'
);
```

##### Tasks

```sql
CREATE TABLE tasks (
    task_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    duration_minutes INTEGER NOT NULL,
    deadline TIMESTAMP WITH TIME ZONE,
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    is_flexible BOOLEAN NOT NULL DEFAULT TRUE,
    cognitive_demands JSONB,
    tags TEXT[],
    metadata JSONB
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_status ON tasks(status);
```

##### Schedule Items

```sql
CREATE TABLE schedule_items (
    item_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(task_id) ON DELETE SET NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL CHECK (status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'RESCHEDULED')),
    energy_level NUMERIC(3, 1),
    match_score NUMERIC(3, 2),
    is_manually_scheduled BOOLEAN NOT NULL DEFAULT FALSE,
    original_item_id UUID,
    schedule_optimization_id UUID,
    metadata JSONB
);

CREATE INDEX idx_schedule_items_user_id ON schedule_items(user_id);
CREATE INDEX idx_schedule_items_task_id ON schedule_items(task_id);
CREATE INDEX idx_schedule_items_time_range ON schedule_items(start_time, end_time);
```

##### Energy Reports

```sql
CREATE TABLE energy_reports (
    report_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    energy_level INTEGER NOT NULL CHECK (energy_level BETWEEN 1 AND 10),
    focus_level INTEGER CHECK (focus_level BETWEEN 1 AND 10),
    creative_level INTEGER CHECK (creative_level BETWEEN 1 AND 10),
    executive_function_level INTEGER CHECK (executive_function_level BETWEEN 1 AND 10),
    mood VARCHAR(50),
    context JSONB,
    notes TEXT
);

CREATE INDEX idx_energy_reports_user_id ON energy_reports(user_id);
CREATE INDEX idx_energy_reports_timestamp ON energy_reports(timestamp);
```

##### Optimization Sessions

```sql
CREATE TABLE optimization_sessions (
    optimization_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    time_range_start TIMESTAMP WITH TIME ZONE NOT NULL,
    time_range_end TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'APPLIED')),
    parameters JSONB NOT NULL,
    results JSONB,
    applied_at TIMESTAMP WITH TIME ZONE,
    user_feedback JSONB,
    error_details TEXT
);

CREATE INDEX idx_optimization_sessions_user_id ON optimization_sessions(user_id);
CREATE INDEX idx_optimization_sessions_status ON optimization_sessions(status);
```

#### MongoDB Collections

##### CircadianModels

```json
{
  "_id": "<ObjectId>",
  "model_id": "<UUID>",
  "user_id": "<UUID>",
  "created_at": "<ISODate>",
  "updated_at": "<ISODate>",
  "version": "2.3.1",
  "training_data_points": 342,
  "confidence_score": 0.86,
  "parameters": {
    "base_level": 5.2,
    "primary_amplitude": 2.1,
    "primary_phase": 10.5,
    "secondary_amplitude": 1.2,
    "secondary_phase": 14.0,
    "tertiary_amplitude": 0.5,
    "tertiary_phase": 2.0,
    "day_adjustment": [0.0, 0.1, 0.2, -0.1, -0.2, 0.5, 0.3]
  },
  "dimension_parameters": {
    "focus": {
      "base_level": 4.8,
      "primary_amplitude": 2.3,
      "primary_phase": 9.8,
      // Additional parameters
    },
    "creativity": {
      // Parameters for creativity dimension
    },
    "executive_function": {
      // Parameters for executive function dimension
    }
  },
  "adaptation_speed": "MEDIUM",
  "data_quality": {
    "coverage": 0.78,
    "consistency": 0.82,
    "recency": 0.94
  },
  "recommended_actions": [
    "Report energy levels more consistently on weekends",
    "Add more data about evening energy patterns"
  ]
}
```

##### TaskCognitiveProfiles

```json
{
  "_id": "<ObjectId>",
  "task_id": "<UUID>",
  "user_id": "<UUID>",
  "created_at": "<ISODate>",
  "updated_at": "<ISODate>",
  "task_title": "Quarterly financial report",
  "cognitive_profile": {
    "focus_required": 8.2,
    "executive_function_load": 7.5,
    "creative_required": 4.8,
    "complexity": 7.1
  },
  "confidence": 0.86,
  "nlp_analysis": {
    "cognitive_indicators": {
      "focus": 5,
      "executive_function": 7,
      "creative": 3,
      "memory": 4
    },
    "complexity_indicators": {
      "multi_step": true,
      "interdependencies": 3,
      "information_density": "high"
    },
    "key_verbs": ["analyze", "compile", "create", "write"],
    "time_expressions": ["quarterly", "Q3"]
  },
  "optimal_scheduling": {
    "optimal_time_of_day": "MORNING",
    "suggested_breaks": 2,
    "break_interval_minutes": 45
  },
  "similar_tasks": [
    {"task_id": "<UUID>", "similarity_score": 0.92},
    {"task_id": "<UUID>", "similarity_score": 0.85}
  ]
}
```

##### ScheduleOptimizations

```json
{
  "_id": "<ObjectId>",
  "optimization_id": "<UUID>",
  "user_id": "<UUID>",
  "created_at": "<ISODate>",
  "type": "CIRCADIAN",
  "timeframe": {
    "start": "<ISODate>",
    "end": "<ISODate>"
  },
  "parameters": {
    "optimization_strength": 0.8,
    "respect_existing_events": true,
    "priority_weight": 0.7,
    "deadline_weight": 0.6,
    "cognitive_matching_weight": 0.9,
    "allow_breaks": true,
    "break_duration_minutes": 15,
    "avoid_switching_costs": true,
    "group_similar_tasks": true
  },
  "tasks": [
    {
      "task_id": "<UUID>",
      "cognitive_demands": {
        "focus_required": 8.2,
        "executive_function_load": 7.5,
        "creative_required": 4.8,
        "complexity": 7.1
      },
      "priority": "HIGH",
      "deadline": "<ISODate>",
      "duration_minutes": 120,
      "is_flexible": true
    },
    // Additional tasks
  ],
  "energy_curves": {
    "2023-09-01": {
      "hourly_levels": [
        {"hour": 0, "energy": 2.1, "focus": 1.8, "creativity": 3.2, "executive_function": 1.5},
        // Additional hourly predictions
      ]
    },
    // Additional days
  },
  "result": {
    "schedule_items": [
      {
        "task_id": "<UUID>",
        "start_time": "<ISODate>",
        "end_time": "<ISODate>",
        "energy_level": 8.5,
        "match_score": 0.92,
        "match_explanation": "High focus task scheduled during peak energy window"
      },
      // Additional scheduled items
    ],
    "unscheduled_tasks": [
      {
        "task_id": "<UUID>",
        "reason": "INSUFFICIENT_TIME"
      }
    ],
    "schedule_quality": 0.87,
    "constraints_satisfied": 14,
    "constraints_violated": 1
  },
  "application_status": "APPLIED",
  "applied_at": "<ISODate>",
  "user_feedback": {
    "rating": 4,
    "comments": "Good schedule overall, but would prefer more buffer time between meetings",
    "item_feedback": [
      {"item_id": "<UUID>", "rating": 5},
      {"item_id": "<UUID>", "rating": 3, "comment": "Felt too tired for this task at this time"}
    ]
  }
}
```

#### Redis Caching Structure

1. **Energy Predictions Cache**:
   ```
   Key: user:{user_id}:energy_predictions:{date}
   Value: JSON string containing hourly energy predictions
   TTL: 1 day
   ```

2. **Recent Optimization Results Cache**:
   ```
   Key: user:{user_id}:optimization:{optimization_id}
   Value: JSON string containing optimization results
   TTL: 1 hour
   ```

3. **Task Cognitive Demands Cache**:
   ```
   Key: task:{task_id}:cognitive_demands
   Value: JSON string containing cognitive demand scores
   TTL: 1 week
   ```

### Core Data Structures

#### CircadianOptimizationRequest

```typescript
interface CircadianOptimizationRequest {
  start_date: string;  // ISO 8601 format
  end_date: string;    // ISO 8601 format
  tasks: TaskRequest[];
  preferences?: OptimizationPreferences;
}

interface TaskRequest {
  id?: string;
  title: string;
  description?: string;
  duration_minutes: number;
  focus_required?: number;  // 1-10 scale
  executive_function_load?: number;  // 1-10 scale
  creative_required?: number;  // 1-10 scale
  complexity?: number;  // 1-10 scale
  priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  is_flexible: boolean;
  deadline?: string;  // ISO 8601 format
  constraints?: TaskConstraint[];
}

interface OptimizationPreferences {
  work_hours?: {
    start: string;  // HH:MM format
    end: string;    // HH:MM format
  };
  weekend_different?: boolean;
  weekend_work_hours?: {
    start: string;  // HH:MM format
    end: string;    // HH:MM format
  };
  optimization_strength?: number;  // 0.0-1.0
  respect_existing_events?: boolean;
  allow_breaks?: boolean;
  break_duration_minutes?: number;
  avoid_switching_costs?: boolean;
  group_similar_tasks?: boolean;
  priority_weight?: number;  // 0.0-1.0
  deadline_weight?: number;  // 0.0-1.0
  cognitive_matching_weight?: number;  // 0.0-1.0
}

interface TaskConstraint {
  type: "fixed_time" | "preferred_time" | "not_before" | "not_after" | "sequence";
  parameters: any;  // Constraint-specific parameters
}
```

#### CircadianOptimizationResponse

```typescript
interface CircadianOptimizationResponse {
  optimization_id: string;
  schedule: ScheduleItem[];
  energy_curves: EnergyPrediction[][];
  unscheduled_tasks?: UnscheduledTask[];
  quality_metrics: ScheduleQualityMetrics;
  message: string;
}

interface ScheduleItem {
  task_id: string;
  title: string;
  start_time: string;  // ISO 8601 format
  end_time: string;    // ISO 8601 format
  energy_level: number;
  match_score: number;
  match_explanation: string;
}

interface EnergyPrediction {
  timestamp: string;  // ISO 8601 format
  energy_level: number;
  focus_capacity: number;
  creative_capacity: number;
  executive_function_capacity: number;
}

interface UnscheduledTask {
  task_id: string;
  title: string;
  reason: "INSUFFICIENT_TIME" | "CONSTRAINTS_CONFLICT" | "NO_SUITABLE_SLOT";
  suggested_actions: string[];
}

interface ScheduleQualityMetrics {
  overall_score: number;  // 0.0-1.0
  energy_alignment_score: number;  // 0.0-1.0
  priority_satisfaction_score: number;  // 0.0-1.0
  deadline_compliance_score: number;  // 0.0-1.0
  workload_balance_score: number;  // 0.0-1.0
  context_switching_score: number;  // 0.0-1.0
}
```

#### CircadianModelStatus

```typescript
interface CircadianModelStatus {
  model_id: string;
  version: string;
  created_at: string;
  last_updated: string;
  training_data_points: number;
  confidence_score: number;
  prediction_accuracy: number;
  adaptation_speed: "SLOW" | "MEDIUM" | "FAST";
  data_quality: {
    coverage: number;  // 0.0-1.0
    consistency: number;  // 0.0-1.0
    recency: number;  // 0.0-1.0
  };
  recommendations: {
    needs_more_data: boolean;
    suggested_actions: string[];
  };
}
```

#### EnergyReport

```typescript
interface EnergyReport {
  timestamp: string;  // ISO 8601 format
  energy_level: number;  // 1-10 scale
  focus_level?: number;  // 1-10 scale
  creative_level?: number;  // 1-10 scale
  executive_function_level?: number;  // 1-10 scale
  mood?: string;
  context?: {
    location?: string;
    activity?: string;
    recent_meal?: boolean;
    recent_exercise?: boolean;
    medication_taken?: boolean;
    sleep_quality?: number;  // 1-5 scale
  };
  notes?: string;
}
```

### Database Access Layer

The data access layer follows the repository pattern to provide a clean interface for data operations:

```typescript
interface UserRepository {
  getUserProfile(userId: string): Promise<UserProfile>;
  updateUserProfile(userId: string, updates: Partial<UserProfile>): Promise<UserProfile>;
  getUserSchedulingPreferences(userId: string): Promise<SchedulingPreferences>;
  updateUserSchedulingPreferences(userId: string, preferences: Partial<SchedulingPreferences>): Promise<SchedulingPreferences>;
}

interface TaskRepository {
  getTasks(userId: string, filters?: TaskFilters): Promise<Task[]>;
  getTaskById(taskId: string): Promise<Task>;
  createTask(userId: string, task: NewTask): Promise<Task>;
  updateTask(taskId: string, updates: Partial<Task>): Promise<Task>;
  deleteTask(taskId: string): Promise<void>;
  getTaskCognitiveProfile(taskId: string): Promise<TaskCognitiveProfile>;
  updateTaskCognitiveProfile(taskId: string, profile: Partial<TaskCognitiveProfile>): Promise<TaskCognitiveProfile>;
}

interface ScheduleRepository {
  getSchedule(userId: string, startDate: Date, endDate: Date): Promise<ScheduleItem[]>;
  addScheduleItem(item: NewScheduleItem): Promise<ScheduleItem>;
  updateScheduleItem(itemId: string, updates: Partial<ScheduleItem>): Promise<ScheduleItem>;
  removeScheduleItem(itemId: string): Promise<void>;
  getOptimizationSession(optimizationId: string): Promise<OptimizationSession>;
  createOptimizationSession(session: NewOptimizationSession): Promise<OptimizationSession>;
  updateOptimizationSession(optimizationId: string, updates: Partial<OptimizationSession>): Promise<OptimizationSession>;
}

interface CircadianRepository {
  getEnergyReports(userId: string, startDate: Date, endDate: Date): Promise<EnergyReport[]>;
  addEnergyReport(userId: string, report: NewEnergyReport): Promise<EnergyReport>;
  getCircadianModel(userId: string): Promise<CircadianModel>;
  updateCircadianModel(userId: string, updates: Partial<CircadianModel>): Promise<CircadianModel>;
  getEnergyPredictions(userId: string, date: Date): Promise<HourlyEnergyLevel[]>;
  cacheEnergyPredictions(userId: string, date: Date, predictions: HourlyEnergyLevel[]): Promise<void>;
}
```

## Integration Points

### Integration with External Systems

#### Calendar Integration

The system integrates with external calendar services to synchronize tasks and events:

```typescript
interface CalendarIntegration {
  getEvents(userId: string, calendarId: string, startDate: Date, endDate: Date): Promise<CalendarEvent[]>;
  createEvent(userId: string, calendarId: string, event: NewCalendarEvent): Promise<CalendarEvent>;
  updateEvent(userId: string, calendarId: string, eventId: string, updates: Partial<CalendarEvent>): Promise<CalendarEvent>;
  deleteEvent(userId: string, calendarId: string, eventId: string): Promise<void>;
  getCalendars(userId: string): Promise<Calendar[]>;
  syncScheduleToCalendar(userId: string, calendarId: string, optimizationId: string): Promise<SyncResult>;
}
```

#### Sleep Tracking Integration

Integration with sleep tracking services improves circadian rhythm predictions:

```typescript
interface SleepTrackingIntegration {
  getSleepData(userId: string, startDate: Date, endDate: Date): Promise<SleepRecord[]>;
  getLatestSleepRecord(userId: string): Promise<SleepRecord>;
  subscribeToDailySleepUpdates(userId: string): Promise<void>;
}

interface SleepRecord {
  date: string;  // YYYY-MM-DD
  sleep_start: string;  // ISO 8601
  sleep_end: string;  // ISO 8601
  total_sleep_minutes: number;
  deep_sleep_minutes: number;
  rem_sleep_minutes: number;
  light_sleep_minutes: number;
  sleep_quality: number;  // 0.0-1.0
  wake_count: number;
  source: string;  // e.g., "fitbit", "oura", "apple_health"
}
```

#### Productivity Analytics Integration

Integration with productivity analytics systems for improved feedback loops:

```typescript
interface ProductivityIntegration {
  getProductivityMetrics(userId: string, date: Date): Promise<ProductivityMetrics>;
  getProductivityTrends(userId: string, startDate: Date, endDate: Date): Promise<ProductivityTrend[]>;
  reportTaskCompletion(userId: string, taskId: string, completionData: TaskCompletionData): Promise<void>;
  getFocusSessions(userId: string, startDate: Date, endDate: Date): Promise<FocusSession[]>;
}
```

### Integration with Internal Services

#### Integration with Epic 1 (Temporal Pattern Recognition)

The Dynamic Schedule Rebalancing system integrates with the Temporal Pattern Recognition services from Epic 1:

```typescript
interface TemporalPatternService {
  detectUserPatterns(userId: string, dataType: string, startDate: Date, endDate: Date): Promise<PatternResult>;
  getPredictedProductivity(userId: string, timestamp: Date): Promise<ProductivityPrediction>;
  getOptimalTimeForActivity(userId: string, activityType: string, date: Date): Promise<OptimalTimeWindow[]>;
  getTemporalCorrelations(userId: string, metric: string): Promise<TemporalCorrelation[]>;
}
```

#### Integration with Epic 2 (Task Management)

Integration with Task Management services:

```typescript
interface TaskManagementService {
  getTasks(userId: string, filters: TaskFilters): Promise<Task[]>;
  getTaskHistory(userId: string, filters: TaskHistoryFilters): Promise<TaskHistoryEntry[]>;
  updateTaskStatus(taskId: string, status: TaskStatus, metadata?: any): Promise<Task>;
  getTaskStatistics(userId: string, filters: TaskStatsFilters): Promise<TaskStatistics>;
}
```

#### Integration with Epic 3 (Notification System)

Integration with Notification services:

```typescript
interface NotificationService {
  sendScheduleRebalancingNotification(userId: string, data: ScheduleRebalancingData): Promise<void>;
  sendOptimalTaskTimeNotification(userId: string, taskId: string, optimalTime: Date): Promise<void>;
  scheduleEnergyReportReminder(userId: string, time: Date): Promise<void>;
  sendFeedbackRequest(userId: string, optimizationId: string, delayMinutes: number): Promise<void>;
}
```

## Authentication and Authorization

### Access Control

The Dynamic Schedule Rebalancing API endpoints implement the following access control:

| Endpoint | Required Role | Notes |
|----------|--------------|-------|
| `POST /scheduling/circadian-optimize` | User | Only for own schedule |
| `POST /scheduling/apply-circadian-optimization` | User | Only for own schedule |
| `GET /circadian/energy-curve` | User | Only for own data |
| `POST /circadian/report-energy` | User | Only for own data |
| `POST /tasks/analyze-cognitive-demands` | User | Any task |
| `GET /tasks/cognitive-completion-analytics` | User | Only for own tasks |
| `GET /circadian/model-status` | User | Only for own model |
| `POST /circadian/reset-model` | User | Only for own model |

### Security Considerations

1. **Sensitive Data**: Energy levels and circadian patterns are treated as health-related data with enhanced privacy protections
2. **Data Minimization**: Only necessary data is retained for model training
3. **Consent Management**: Explicit user consent is obtained for:
   - Collecting energy level data
   - Analyzing task completion patterns
   - Integrating with external data sources (sleep, productivity)
4. **Data Retention**: Energy reports older than 90 days are anonymized for long-term storage

## Error Handling

### API Error Responses

All API error responses follow a standardized format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field1": "Problem with this field",
      "field2": "Problem with another field"
    }
  },
  "request_id": "req-abcdef123456"
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_PARAMETERS` | 400 | Request parameters are invalid |
| `INVALID_DATE_RANGE` | 400 | Date range is invalid |
| `INSUFFICIENT_DATA` | 422 | Not enough data to generate accurate predictions |
| `MODEL_NOT_READY` | 422 | Circadian model isn't fully trained yet |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests in a short period |
| `AUTHENTICATION_FAILED` | 401 | Authentication credentials are invalid |
| `AUTHORIZATION_FAILED` | 403 | User doesn't have permission for this action |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource doesn't exist |
| `INTERNAL_ERROR` | 500 | An internal server error occurred |

### Error Handling Strategy

1. **Validation Errors**: Caught and returned at API gateway level
2. **Business Logic Errors**: Caught at service level and transformed to appropriate responses
3. **Unexpected Errors**: Logged with full details, generic message returned to client
4. **Dependency Failures**: Circuit breakers implemented for external dependencies

```typescript
try {
  const result = await service.optimizeSchedule(request);
  return response.status(200).json(result);
} catch (error) {
  if (error instanceof ValidationError) {
    return response.status(400).json({
      error: {
        code: 'INVALID_PARAMETERS',
        message: 'Invalid request parameters',
        details: error.details
      },
      request_id: requestId
    });
  }

  if (error instanceof BusinessLogicError) {
    return response.status(error.statusCode).json({
      error: {
        code: error.code,
        message: error.message,
        details: error.details
      },
      request_id: requestId
    });
  }

  // Unexpected error
  logger.error('Unexpected error in schedule optimization', {
    error: error.toString(),
    stack: error.stack,
    request: sanitizeRequest(request),
    requestId
  });

  return response.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred',
      details: {}
    },
