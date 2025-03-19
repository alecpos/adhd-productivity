# ADHD Calendar Backend Database Schema

This document describes the database schema for the ADHD Calendar Backend application, accurately reflecting the current implementation.

## Core Entities

### UserModel

The central entity representing application users with ADHD-specific profile data.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| email | String | User's email address (unique) |
| username | String | Username for login |
| full_name | String | User's full name |
| hashed_password | String | Securely stored password |
| is_active | Boolean | Account status |
| is_verified | Boolean | Email verification status |
| created_at | DateTime | Account creation timestamp |
| updated_at | DateTime | Last update timestamp |
| energy_level | Integer | Current energy level (1-10) |
| focus_level | Integer | Current focus ability (1-10) |
| refresh_token | String | For JWT auth refresh |
| refresh_token_expires | DateTime | Refresh token expiration |
| reset_token | String | Password reset token |
| reset_token_expires | DateTime | Reset token expiration |

**Relationships:**
- One-to-Many with `TaskModel`
- One-to-Many with `CalendarEventModel`
- One-to-Many with `MentalHealthModel`
- One-to-Many with `EnergyLogModel`
- One-to-Many with `FocusSessionModel`
- One-to-Many with `BodyDoublingSessionModel`
- One-to-Many with `HyperfocusSessionModel`

### TaskModel

Represents tasks with ADHD-specific attributes for better task management.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| title | String | Task title |
| description | String | Detailed description |
| due_date | DateTime | When task is due |
| estimated_duration | Integer | Estimated minutes to complete |
| priority | Integer | Priority level (1-5) |
| difficulty | Integer | Difficulty rating (1-5) |
| energy_required | Integer | Energy needed (1-10) |
| focus_required | Integer | Focus needed (1-10) |
| status | String | Status (pending, in_progress, completed, etc.) |
| is_recurring | Boolean | Whether task repeats |
| recurrence_pattern | String | How task repeats (daily, weekly, etc.) |
| category_id | UUID | Task category reference |
| parent_task_id | UUID | Parent task for hierarchical tasks |
| completed_at | DateTime | When task was completed |
| created_at | DateTime | Task creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `TaskCategoryModel`
- One-to-Many with `TaskModel` (self-referential for subtasks)

### TaskCategoryModel

Categorizes tasks for better organization.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| name | String | Category name |
| color | String | Display color for UI |
| description | String | Optional description |
| created_at | DateTime | Category creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- One-to-Many with `TaskModel`

### CalendarEventModel

Represents calendar events with associated metadata and ADHD-specific attributes.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| calendar_id | UUID | Associated calendar |
| title | String | Event title |
| description | String | Event description |
| location | String | Event location |
| event_type | String | Type of event (meeting, appointment, task, etc.) |
| priority | String | Event priority (low, medium, high, urgent) |
| status | String | Event status (scheduled, completed, cancelled, rescheduled) |
| start_time | DateTime | Event start time |
| end_time | DateTime | Event end time |
| duration | Integer | Duration in minutes |
| energy_required | Integer | Energy needed (1-10) |
| focus_required | Integer | Focus needed (1-10) |
| stress_level | Integer | Stress level associated with event |
| preparation_time | Integer | Time needed for preparation in minutes |
| transition_time | Integer | Time needed for transition in minutes |
| buffer_before | Integer | Buffer time before event in minutes |
| buffer_after | Integer | Buffer time after event in minutes |
| completion_status | String | Detailed completion status |
| completion_time | DateTime | When event was completed |
| actual_duration | Integer | Actual time taken in minutes |
| focus_score | Float | Focus effectiveness score |
| energy_level | Integer | Energy level during event |
| satisfaction_score | Float | User satisfaction with event |
| interruptions | JSON | List of interruptions during event |
| reminders | JSON | Reminder settings for event |
| last_reminder_sent | DateTime | When last reminder was sent |
| reminder_preferences | JSON | User preferences for reminders |
| recurrence_type | String | Type of recurrence (daily, weekly, etc.) |
| recurrence_end_date | DateTime | When recurrence ends |
| recurrence_count | Integer | Number of recurrences |
| recurrence_days | JSON | Days of recurrence for weekly patterns |
| recurring_parent_id | UUID | Parent event for recurring instances |
| instance_date | DateTime | Date for this instance of recurring event |
| sync_status | String | Calendar sync status |
| external_id | String | ID in external calendar system |
| last_synced | DateTime | Last synchronization timestamp |
| meta_data | JSON | Additional metadata |
| custom_fields | JSON | User-defined fields |
| is_all_day | Boolean | Whether event lasts all day |
| is_recurring | Boolean | Whether event repeats |
| recurrence_pattern | String | Pattern for recurrence |
| created_at | DateTime | Event creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `CalendarModel`
- One-to-Many with `TimeBlockModel`
- One-to-Many with `EnergyLogModel`
- One-to-Many with `ScheduleBlockModel`

### EnergyModel

Tracks user's overall energy patterns and thresholds.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| baseline_energy | Integer | User's baseline energy level (1-10) |
| energy_variability | Float | Measure of energy level fluctuation |
| optimal_energy_threshold | Integer | Optimal energy level for productivity |
| circadian_rhythm_pattern | JSON | Daily energy pattern data |
| recovery_rate | Float | Energy recovery rate after depletion |
| depletion_rate | Float | Energy depletion rate during activities |
| task_specific_impact | JSON | Energy impact of different task types |
| sleep_impact_factor | Float | Impact of sleep on energy levels |
| medication_impact_factor | Float | Impact of medication on energy levels |
| nutrition_impact_factor | Float | Impact of nutrition on energy levels |
| exercise_impact_factor | Float | Impact of exercise on energy levels |
| stress_impact_factor | Float | Impact of stress on energy levels |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- One-to-One with `UserModel`
- One-to-Many with `EnergyLog`

### EnergyLogModel

Tracks user energy levels over time for pattern recognition.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| calendar_event_id | UUID | Associated calendar event (optional) |
| energy_level | Integer | Energy level (1-10) |
| timestamp | DateTime | When energy was logged |
| factors | JSON | Contributing factors |
| notes | String | User notes |
| created_at | DateTime | Log creation timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `CalendarEventModel` (optional)

### EnergyStats

Aggregates energy statistics over a time period.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| time_period | String | Period of analysis (daily, weekly, monthly) |
| start_date | DateTime | Start of analysis period |
| end_date | DateTime | End of analysis period |
| average_energy | Float | Average energy level during period |
| energy_variability | Float | Measure of energy level fluctuation |
| peak_energy_time | JSON | Times of day with highest energy |
| low_energy_time | JSON | Times of day with lowest energy |
| energy_stability | Float | Measure of energy level stability |
| energy_recovery_pattern | JSON | Pattern of energy recovery |
| impacting_factors | JSON | Factors impacting energy levels |
| activity_correlation | JSON | Correlation between activities and energy |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`

### MentalHealthModel

Tracks mental health metrics relevant to ADHD management.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| baseline_focus_level | Integer | Baseline focus capability (1-10) |
| baseline_energy_level | Integer | Baseline energy level (1-10) |
| baseline_stress_level | Integer | Baseline stress level (1-10) |
| executive_function_score | Float | Executive function assessment score |
| typical_stress_triggers | String | Common stress triggers |
| current_medication | String | Current ADHD medication |
| medication_effectiveness | Integer | Self-rated medication effectiveness (1-10) |
| coping_strategies | String | Documented coping mechanisms |
| last_assessment_date | DateTime | When profile was last assessed |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- One-to-Many with `MentalHealthLogModel`

### MentalHealthLogModel

Individual mental health log entries for tracking changes over time.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| mental_health_id | UUID | Foreign key to MentalHealthModel |
| mood_score | Integer | Current mood rating (1-10) |
| anxiety_level | Integer | Current anxiety rating (1-10) |
| focus_level | Integer | Current focus capability (1-10) |
| energy_level | Integer | Current energy level (1-10) |
| stress_level | Integer | Current stress level (1-10) |
| sleep_hours | Float | Hours of sleep previous night |
| notes | String | User notes about mental state |
| created_at | DateTime | Log creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `MentalHealthModel`

### FocusSessionModel

Records focus session data for analysis and tracking.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| task_id | UUID | Associated task (optional) |
| duration | Integer | Minutes of focus |
| focus_level | Integer | Self-rated focus level (1-10) |
| energy_level | Integer | Energy level during session (1-10) |
| activity_type | String | Type of activity during focus |
| status | String | Session status |
| start_time | DateTime | Session start |
| end_time | DateTime | Session end (optional) |
| productivity_score | Integer | Self-rated productivity (1-10) |
| completion_rate | Float | Task completion percentage |
| total_breaks | Integer | Number of breaks taken |
| total_break_duration | Integer | Total minutes spent on breaks |
| actual_focus_duration | Integer | Actual minutes of focused work |
| break_frequency | Float | Average breaks per hour |
| interruptions | JSON | Details about interruptions |
| breaks | JSON | Break details and timing |
| metrics | JSON | Additional performance metrics |
| notes | String | User notes |
| meta_data | JSON | Additional metadata |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `TaskModel`

### PomodoroSessionModel

Tracks pomodoro technique usage.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| start_time | DateTime | Session start |
| end_time | DateTime | Session end |
| work_duration | Integer | Work segment minutes |
| break_duration | Integer | Break segment minutes |
| completed_cycles | Integer | Completed pomodoro cycles |
| task_id | UUID | Associated task |
| status | String | Session status |
| created_at | DateTime | Record creation timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `TaskModel`

### HyperfocusSessionModel

Records hyperfocus episodes for analysis.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| start_time | DateTime | Session start |
| end_time | DateTime | Session end |
| duration | Integer | Minutes in hyperfocus |
| task_id | UUID | Associated task |
| intentional | Boolean | Whether planned |
| productivity_score | Integer | Self-rated productivity (1-10) |
| triggers | JSON | What triggered hyperfocus |
| notes | String | User notes |
| created_at | DateTime | Record creation timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `TaskModel`

### BodyDoublingSessionModel

Records body doubling sessions (working alongside others).

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| start_time | DateTime | Session start |
| end_time | DateTime | Session end |
| partner_id | UUID | Doubling partner (optional) |
| task_id | UUID | Associated task |
| productivity_score | Integer | Self-rated productivity (1-10) |
| notes | String | User notes |
| created_at | DateTime | Record creation timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `TaskModel`

### ADHDSettingsModel

Stores user-specific ADHD accommodation settings.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| work_interval_duration | Integer | Duration of work intervals in minutes |
| break_duration | Integer | Duration of short breaks in minutes |
| long_break_duration | Integer | Duration of long breaks in minutes |
| blocks_before_long_break | Integer | Work blocks before a long break |
| notification_preferences | JSON | User's notification settings |
| distraction_sensitivity | Float | Sensitivity to distractions |
| focus_assistance_level | Integer | Level of focus support needed |
| medication_schedule | JSON | Medication schedule details |
| energy_tracking_enabled | Boolean | Whether energy tracking is enabled |
| task_chunking_enabled | Boolean | Whether task chunking is enabled |
| visual_aids_enabled | Boolean | Whether visual aids are enabled |
| sound_sensitivity | Float | Sensitivity to sounds |
| environment_preferences | JSON | Environment preferences |
| focus_settings | JSON | Focus-related settings |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- One-to-One with `UserModel`
- One-to-Many with `DistractionLogModel`
- One-to-Many with `MedicationLogModel`
- One-to-Many with `ADHDMetricsModel`
- One-to-Many with `ADHDPatternsModel`

### DistractionLogModel

Records distractions for pattern recognition.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| settings_id | UUID | Foreign key to ADHDSettingsModel |
| user_id | UUID | Foreign key to UserModel |
| timestamp | DateTime | When distraction occurred |
| distraction_type | Enum | Type of distraction |
| duration | Integer | Minutes distracted |
| severity | Integer | Severity level |
| context | String | Context when distraction occurred |
| activity_interrupted | String | Activity that was interrupted |
| resolution_time | Integer | Time to resolve distraction |
| coping_strategy_used | String | Strategy used to cope |
| effectiveness | Integer | Effectiveness of coping strategy |
| notes | String | User notes |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `ADHDSettingsModel`

### MedicationLogModel

Tracks ADHD medication usage.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| settings_id | UUID | Foreign key to ADHDSettingsModel |
| user_id | UUID | Foreign key to UserModel |
| timestamp | DateTime | When medication log was created |
| medication_type | Enum | Type of medication |
| medication_name | String | Medication name |
| dosage | Float | Medication dosage amount |
| unit | String | Dosage unit |
| effectiveness | Integer | Self-rated effectiveness (1-10) |
| side_effects | JSON | Side effects observed |
| mood | Integer | Mood rating (1-10) |
| focus_level | Integer | Focus level (1-10) |
| notes | String | User notes |
| taken_at | DateTime | When medication was taken |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `ADHDSettingsModel`

### ADHDMetricsModel

Tracks ADHD-related metrics and measurements.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| settings_id | UUID | Foreign key to ADHDSettingsModel |
| user_id | UUID | Foreign key to UserModel |
| timestamp | DateTime | When metrics were logged |
| focus_score | Float | Overall focus score |
| productivity_score | Float | Overall productivity score |
| distraction_count | Integer | Number of distractions |
| medication_taken | Boolean | Whether medication was taken |
| energy_level | Integer | Energy level (1-10) |
| mood_level | Integer | Mood level (1-10) |
| tasks_completed | Integer | Number of completed tasks |
| tasks_total | Integer | Total number of tasks |
| focus_duration | Integer | Total focus duration in minutes |
| break_adherence | Float | Adherence to break schedule (0-1) |
| daily_achievement_score | Float | Daily achievement score |
| stress_level | Integer | Stress level (1-10) |
| sleep_quality | Integer | Sleep quality (1-10) |
| exercise_minutes | Integer | Minutes of exercise |
| completion_rate | Float | Task completion rate (0-1) |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `ADHDSettingsModel`

### NLPAnalysis

Stores natural language processing analysis results.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| task_id | UUID | Associated task |
| complexity_score | Float | Task complexity (0-1) |
| focus_requirements | Integer | Focus needed (1-10) |
| estimated_steps | Integer | Estimated subtasks |
| ambiguity_score | Float | Task ambiguity (0-1) |
| topics | JSON | Identified topics |
| cognitive_load | Integer | Estimated cognitive load (1-10) |
| created_at | DateTime | Analysis timestamp |

**Relationships:**
- One-to-One with `TaskModel`

### ScheduleBlock

Represents a scheduled time block.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| task_id | UUID | Foreign key to TaskModel (optional) |
| calendar_event_id | UUID | Foreign key to CalendarEventModel (optional) |
| title | String | Block title |
| description | String | Block description |
| start_time | DateTime | Block start time |
| end_time | DateTime | Block end time |
| block_type | Enum | Type of block (work, break, etc.) |
| priority | Enum | Priority level |
| status | Enum | Block status |
| is_flexible | Boolean | Whether the block can be moved |
| buffer_before | Integer | Buffer time before block in minutes |
| buffer_after | Integer | Buffer time after block in minutes |
| energy_requirement | Integer | Required energy level (1-10) |
| focus_requirement | Integer | Required focus level (1-10) |
| location | String | Block location |
| actual_start_time | DateTime | When block actually started |
| actual_end_time | DateTime | When block actually ended |
| total_focus_time | Integer | Total minutes of focus |
| total_break_time | Integer | Total minutes of breaks |
| completion_rate | Float | Completion percentage |
| effectiveness_score | Float | Effectiveness score |
| calendar_type | Enum | Type of calendar |
| recurrence_type | Enum | Type of recurrence |
| recurrence_pattern | JSON | Pattern for recurring blocks |
| is_all_day | Boolean | Whether block lasts all day |
| meta_data | JSON | Additional metadata |
| created_at | DateTime | Block creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `TaskModel` (optional)
- Many-to-One with `CalendarEventModel` (optional)
- One-to-Many with `Break`
- One-to-Many with `Interruption`

### Interruption

Tracks disruptions during scheduled blocks.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| schedule_block_id | UUID | Foreign key to ScheduleBlock |
| session_id | UUID | Foreign key to SessionModel (optional) |
| start_time | DateTime | When interruption started |
| end_time | DateTime | When interruption ended |
| duration | Integer | Duration in minutes |
| interruption_type | String | Type of interruption (external, internal, etc.) |
| source | String | Source of interruption |
| priority | Integer | Priority level (1-5) |
| impact | Integer | Impact severity (1-5) |
| resolution | String | How interruption was resolved |
| was_preventable | Boolean | Whether interruption was preventable |
| notes | String | Additional notes |
| meta_data | JSON | Additional metadata |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `ScheduleBlock`
- Many-to-One with `SessionModel`

### Break

Tracks breaks between work sessions.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| work_hours_id | UUID | Foreign key to WorkHours (optional) |
| schedule_block_id | UUID | Foreign key to ScheduleBlock (optional) |
| energy_pattern_id | UUID | Foreign key to EnergyPattern (optional) |
| session_id | UUID | Foreign key to SessionModel (optional) |
| start_time | DateTime | When break started |
| end_time | DateTime | When break ended |
| duration | Integer | Duration in minutes |
| break_type | String | Type of break (short, long, etc.) |
| activity | String | Activity during break |
| effectiveness | Integer | Effectiveness rating (1-10) |
| energy_impact | Integer | Impact on energy (-5 to +5) |
| notes | String | Additional notes |
| meta_data | JSON | Additional metadata |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `WorkHours` (optional)
- Many-to-One with `ScheduleBlock` (optional)
- Many-to-One with `EnergyPattern` (optional)
- Many-to-One with `SessionModel` (optional)

### WorkHours

Defines user's regular working hours.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| start_time | DateTime | Regular start time |
| end_time | DateTime | Regular end time |
| days | JSON | Days of week (0-6) |
| timezone | String | User's timezone |
| is_default | Boolean | Whether this is the default schedule |
| meta_data | JSON | Additional metadata |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- One-to-Many with `Break`

### SchedulePreferences

Stores user preferences for scheduling.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| preferred_start_time | DateTime | Preferred day start time |
| preferred_end_time | DateTime | Preferred day end time |
| preferred_break_duration | Integer | Preferred break length in minutes |
| min_break_interval | Integer | Minimum time between breaks in minutes |
| max_focus_duration | Integer | Maximum focus time in minutes |
| preferred_task_order | JSON | Preferred order of task types |
| location_preferences | JSON | Location preferences for tasks |
| calendar_preferences | JSON | Calendar-specific preferences |
| meta_data | JSON | Additional metadata |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- One-to-Many with `EnergyPattern`

### EnergyPattern

Tracks energy patterns for schedule optimization.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| schedule_preferences_id | UUID | Foreign key to SchedulePreferences |
| time_of_day | DateTime | Time of day for this pattern |
| average_energy | Integer | Average energy level (1-10) |
| average_focus | Integer | Average focus level (1-10) |
| common_activities | JSON | Common activities during this time |
| optimal_recovery_activities | JSON | Best activities for recovery |
| environmental_preferences | JSON | Environmental preferences |
| meta_data | JSON | Additional metadata |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `SchedulePreferences`
- One-to-Many with `Break`

### TimelineEventModel

Records significant timeline events.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| timestamp | DateTime | Event time |
| event_type | String | Event type |
| description | String | Event description |
| related_entity_id | UUID | Related entity (task, etc.) |
| entity_type | String | Type of related entity |
| metadata | JSON | Additional event data |
| created_at | DateTime | Event creation timestamp |

**Relationships:**
- Many-to-One with `UserModel`

### VoiceCommandModel

Records voice commands for the system.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| timestamp | DateTime | Command time |
| command_text | String | Raw command text |
| interpreted_intent | String | Interpreted intent |
| success | Boolean | Command success |
| result | JSON | Command result |
| created_at | DateTime | Command timestamp |

**Relationships:**
- Many-to-One with `UserModel`

### VoicePreferencesModel

Stores voice interaction preferences.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| voice_type | String | Preferred voice type |
| speech_rate | Float | Preferred speech rate |
| enabled_commands | JSON | Enabled command types |
| verification_required | Boolean | Verify before actions |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- One-to-One with `UserModel`

## Data Analysis Models

These models store ML model data and analysis results.

### ADHDPatternsModel

Stores identified ADHD patterns.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| settings_id | UUID | Foreign key to ADHDSettingsModel |
| user_id | UUID | Foreign key to UserModel |
| pattern_type | Enum | Type of pattern |
| confidence_score | Float | Pattern confidence (0-1) |
| frequency | Float | Pattern frequency |
| time_of_day | JSON | Pattern occurrence by time of day |
| day_of_week | JSON | Pattern occurrence by day of week |
| triggers | JSON | Identified triggers for pattern |
| impact_score | Float | Impact rating (0-1) |
| interventions | JSON | Effective interventions |
| success_rate | Float | Intervention success rate (0-1) |
| notes | String | Additional notes |
| detected_at | DateTime | When pattern was detected |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `ADHDSettingsModel`

### TaskAnalysis

Detailed task analysis information.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| task_id | UUID | Associated task |
| complexity_factors | JSON | Complexity breakdown |
| time_estimate_factors | JSON | Time estimate factors |
| energy_requirement_factors | JSON | Energy requirement breakdown |
| focus_requirement_factors | JSON | Focus requirement breakdown |
| created_at | DateTime | Analysis timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- One-to-One with `TaskModel`

### CalendarSyncModel

Tracks external calendar synchronization.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| provider | String | Calendar provider |
| external_id | String | External calendar ID |
| last_synced | DateTime | Last sync time |
| sync_frequency | Integer | Minutes between syncs |
| is_enabled | Boolean | Sync enabled status |
| credentials | JSON | Encrypted credentials |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`

## ADHD Support Models

Models specifically designed for ADHD assistance.

### MindfulnessSessionModel

Tracks mindfulness sessions.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| start_time | DateTime | Session start |
| end_time | DateTime | Session end |
| duration | Integer | Session length in minutes |
| technique | String | Technique used |
| guided | Boolean | Whether guided |
| focus_improvement | Integer | Self-rated improvement (1-10) |
| notes | String | User notes |
| created_at | DateTime | Session timestamp |

**Relationships:**
- Many-to-One with `UserModel`

### CommitmentModel

Stores commitments detected from various sources to support proactive forgetfulness mitigation.

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to UserModel |
| text | Text | Content of the commitment |
| source | Enum | Source of commitment (journal, email, chat, call, meeting, manual, voice_command, other) |
| source_reference | String | Reference to source (e.g., email ID) |
| extracted_from | Text | Original text it was extracted from |
| confidence_score | Float | Model confidence in extraction |
| status | Enum | Status (detected, confirmed, rejected, completed, scheduled, delegated, cancelled) |
| priority | Enum | Priority level (low, medium, high, critical) |
| related_person | String | Person the commitment was made to |
| related_task_id | Integer | Foreign key to TaskModel |
| detected_at | DateTime | When commitment was detected |
| due_date | DateTime | When commitment is due |
| time_frame | String | Textual time frame (e.g., "next week") |
| action_required | String | Action needed to fulfill commitment |
| tags | JSON | Tags for categorization |
| notes | Text | Additional notes |
| should_remind | Boolean | Whether reminders should be sent |
| reminder_frequency | String | How often to remind |
| cross_references | JSON | References to related commitments |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `TaskModel`

### ReminderModel

Stores timely reminders and notifications for tasks and events.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to UserModel |
| task_id | UUID | Foreign key to TaskModel (optional) |
| contact_id | UUID | Foreign key to ContactModel (optional) |
| title | String | Reminder title |
| description | String | Reminder description |
| scheduled_time | DateTime | When to trigger the reminder |
| is_recurring | Boolean | Whether reminder repeats |
| recurrence_pattern | JSON | Pattern for recurring reminders |
| is_sent | Boolean | Whether reminder was sent |
| sent_at | DateTime | When reminder was sent |
| is_acknowledged | Boolean | Whether user acknowledged |
| acknowledged_at | DateTime | When user acknowledged |
| priority | Integer | Reminder priority (1-5) |
| meta_data | JSON | Additional metadata |
| created_at | DateTime | Reminder creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- Many-to-One with `UserModel`
- Many-to-One with `TaskModel` (optional)
- Many-to-One with `ContactModel` (optional)

## Relationship Diagram

The database uses a user-centric design where most entities relate back to the UserModel. Key relationship patterns include:

1. User -> Tasks -> Task Categories (task organization)
2. User -> Calendar Events -> Calendars (time management)
3. User -> Energy/Mental Health/Medication logs (health tracking)
4. User -> Focus/Pomodoro/Hyperfocus sessions (productivity tracking)
5. User -> ADHD patterns/settings (personalization)

This schema is designed to capture comprehensive data about ADHD experiences and enable ML models to provide personalized assistance.

## Database Migration Management

Database migrations are managed using Alembic. For more information on migrations, see the [Alembic Migration Guide](alembic_guide.md).

## Query Optimization

The database schema is optimized for common queries:
- Indexes on frequently queried columns
- Appropriate foreign key constraints
- JSON fields for flexible data storage where appropriate
- Array fields for simple lists (e.g., tags)

## Development Guidelines

When modifying the database schema:
1. Create a new Alembic migration
2. Update the corresponding SQLAlchemy models
3. Update this documentation
4. Ensure backward compatibility if possible 