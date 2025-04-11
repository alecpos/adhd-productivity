# Epic 1: Visual Reference Document - Part 1
# Temporal Pattern Recognition (TPR) Models

## System Architecture Diagrams

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Applications                         │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       API Gateway / Load Balancer                    │
└───────────┬──────────────────┬───────────────────┬──────────────────┘
            │                  │                   │
            ▼                  ▼                   ▼
┌────────────────────┐ ┌────────────────┐ ┌────────────────────┐
│ProductivityPattern │ │CircadianRhythm │ │Productivity        │
│LSTM Service        │ │Model Service   │ │Correlation Service │
└─────────┬──────────┘ └────────┬───────┘ └──────────┬─────────┘
          │                     │                    │
          │                     ▼                    │
          │         ┌────────────────────────┐      │
          └────────►│Temporal Pattern Database◄──────┘
                    └────────────┬───────────┘
                                 │
                                 ▼
                   ┌─────────────────────────────┐
                   │MentalHealthFederatedModel   │
                   │Service                      │
                   └──────────┬──────────────────┘
                              │
                              ▼
                   ┌─────────────────────────┐
                   │Federated Learning Node  │
                   │(On-Device)              │
                   └─────────────────────────┘
```

### Service Communication Patterns

```
┌───────────────────┐      HTTP/REST       ┌───────────────────┐
│                   │◄────────────────────►│                   │
│   API Gateway     │                      │  Client App       │
│                   │                      │                   │
└────────┬──────────┘                      └───────────────────┘
         │
         │ gRPC
         │
┌────────▼──────────┐                     ┌───────────────────┐
│                   │      Pub/Sub        │                   │
│  Service Registry │◄────────────────────►│  Event Bus        │
│                   │                     │                   │
└────────┬──────────┘                     └───────────────────┘
         │
         │ gRPC
         ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    Microservice Mesh                        │
│                                                             │
└──┬─────────────┬───────────────┬────────────────┬───────────┘
   │             │               │                │
   │ gRPC        │ gRPC          │ gRPC           │ gRPC
   ▼             ▼               ▼                ▼
┌─────────┐  ┌─────────┐  ┌─────────────┐  ┌───────────────┐
│         │  │         │  │             │  │               │
│LSTM     │  │Circadian│  │Correlation  │  │Federated      │
│Service  │  │Service  │  │Service      │  │Learning       │
│         │  │         │  │             │  │Service        │
└─────────┘  └─────────┘  └─────────────┘  └───────────────┘
```

### Database Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Database Cluster                      │
│                                                         │
│  ┌─────────────┐     ┌─────────────┐    ┌─────────────┐ │
│  │             │     │             │    │             │ │
│  │   Primary   │────►│  Read       │    │  Read       │ │
│  │   Node      │     │  Replica    │    │  Replica    │ │
│  │             │     │             │    │             │ │
│  └─────────────┘     └─────────────┘    └─────────────┘ │
│         ▲                                               │
└─────────┼───────────────────────────────────────────────┘
          │
          │ Write Operations
          │
┌─────────▼───────────────────────────────────────────────┐
│                                                         │
│                 Application Services                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
          │
          │ Read Operations
          ▼
┌─────────────────────────────────────────────────────────┐
│                    Cache Layer                          │
│                                                         │
│  ┌─────────────┐     ┌─────────────┐    ┌─────────────┐ │
│  │             │     │             │    │             │ │
│  │  Redis      │     │  In-Memory  │    │  CDN        │ │
│  │  Cache      │     │  Cache      │    │  Cache      │ │
│  │             │     │             │    │             │ │
│  └─────────────┘     └─────────────┘    └─────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### MongoDB Collection Relationships

```
┌───────────────────────────────┐
│      ProductivitySession      │
├───────────────────────────────┤
│ _id: ObjectId                 │
│ user_id: UUID                 │──────┐
│ start_time: DateTime          │      │
│ end_time: DateTime            │      │
│ task_category: String         │      │
│ productivity_score: Float     │      │
│ focus_score: Float            │      │
│ interruption_count: Integer   │      │
│ created_at: DateTime          │      │
└───────────────────────────────┘      │
                                       │
┌───────────────────────────────┐      │
│   CircadianRhythmData         │      │
├───────────────────────────────┤
│ _id: ObjectId                 │
│ user_id: UUID  ───────────────┼──────┘
│ date: Date                    │
│ hour: Integer                 │
│ energy_level: Float           │
│ focus_capacity: Float         │
│ sleep_data: Object            │
│ created_at: DateTime          │
└───────────────────────────────┘

┌───────────────────────────────┐
│   ProductivityCorrelation     │
├───────────────────────────────┤
│ _id: ObjectId                 │
│ user_id: UUID                 │
│ factor: String                │
│ metric: String                │
│ correlation_coefficient: Float│
│ significance: Float           │
│ time_period: String           │
│ created_at: DateTime          │
└───────────────────────────────┘

┌───────────────────────────────┐
│   FederatedModelMetadata      │
├───────────────────────────────┤
│ _id: ObjectId                 │
│ user_id: UUID                 │
│ model_version: String         │
│ last_contribution_time: Date  │
│ privacy_budget: Float         │
│ created_at: DateTime          │
└───────────────────────────────┘
```

# Epic 1: Visual Reference Document - Part 2
# Data Flow and Component Interaction

## Data Flow Diagrams

### Productivity Pattern Analysis Flow

```
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│               │    │                 │    │                 │
│ User Activity │───►│ Data Collection │───►│ Feature         │
│ Data          │    │ API             │    │ Extraction      │
│               │    │                 │    │                 │
└───────────────┘    └─────────────────┘    └────────┬────────┘
                                                     │
┌───────────────┐    ┌─────────────────┐    ┌────────▼────────┐
│               │    │                 │    │                 │
│ Optimal Time  │◄───│ Pattern         │◄───│ LSTM Model      │
│ Windows       │    │ Identification  │    │ Processing      │
│               │    │                 │    │                 │
└───────┬───────┘    └─────────────────┘    └─────────────────┘
        │
        │                     ┌─────────────────┐
        │                     │                 │
        └────────────────────►│ Scheduling      │
                              │ Recommendation  │
                              │                 │
                              └─────────────────┘
```

### Circadian Rhythm Model Flow

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│              │      │              │      │              │
│ Sleep Data   │─────►│ Physiological│─────►│ Feature      │
│ (Wearables)  │      │ Data Fusion  │      │ Engineering  │
│              │      │              │      │              │
└──────────────┘      └──────────────┘      └──────┬───────┘
                                                   │
┌──────────────┐      ┌──────────────┐      ┌──────▼───────┐
│              │      │              │      │              │
│ Energy       │◄─────│ Prediction   │◄─────│ Bayesian     │
│ Curve API    │      │ Refinement   │      │ Model Fitting│
│              │      │              │      │              │
└──────────────┘      └──────────────┘      └──────────────┘
```

### Federated Learning Data Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│ User Mental   │────►│ Local Feature │────►│ Local Model   │
│ Health Data   │     │ Extraction    │     │ Training      │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│ Global Model  │◄────│ Secure        │◄────│ Model Update  │
│ Aggregation   │     │ Aggregation   │     │ Extraction    │
│               │     │               │     │               │
└───────┬───────┘     └───────────────┘     └───────────────┘
        │
        │
        ▼
┌───────────────┐     ┌───────────────┐
│               │     │               │
│ Model         │────►│ Local Model   │
│ Distribution  │     │ Update        │
│               │     │               │
└───────────────┘     └───────────────┘
```

### Correlation Analysis Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│ Multiple Data │────►│ Feature       │────►│ Correlation   │
│ Sources       │     │ Alignment     │     │ Calculation   │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│ Insights      │◄────│ Insight       │◄────│ Statistical   │
│ Dashboard     │     │ Generation    │     │ Analysis      │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

## Component Interaction Diagrams

### ProductivityPatternLSTM Components

```
┌─────────────────────────────────────────────────────────────┐
│                   ProductivityPatternLSTM                   │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Data          │──►│ Preprocessing │──►│ Feature       │  │
│  │ Collection    │   │ Pipeline      │   │ Engineering   │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────┬───────┘  │
│                                                  │          │
│  ┌───────────────┐   ┌───────────────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ Sequence      │◄──┤ Bidirectional │◄──┤ Input         │  │
│  │ Prediction    │   │ LSTM Core     │   │ Embedding     │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────────────┘   └───────────────┘  │
│          │                                                  │
│  ┌───────▼───────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Pattern       │──►│ Optimal Time  │──►│ Recommendation│  │
│  │ Identification│   │ Windowing     │   │ Generation    │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### CircadianRhythmModel Components

```
┌─────────────────────────────────────────────────────────────┐
│                     CircadianRhythmModel                    │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Data          │──►│ Wearable      │──►│ Sleep Data    │  │
│  │ Collection    │   │ Integration   │   │ Processing    │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────┬───────┘  │
│                                                  │          │
│  ┌───────────────┐   ┌───────────────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ Baseline      │◄──┤ Rhythm        │◄──┤ Physiological │  │
│  │ Rhythm        │   │ Detection     │   │ Data Fusion   │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────────────┘   └───────────────┘  │
│          │                                                  │
│  ┌───────▼───────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Energy        │──►│ Adaptive      │──►│ Energy Curve  │  │
│  │ Prediction    │   │ Calibration   │   │ Generation    │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### ProductivityCorrelationSystem Components

```
┌─────────────────────────────────────────────────────────────┐
│                 ProductivityCorrelationSystem               │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Data Source   │──►│ Data          │──►│ Feature       │  │
│  │ Connectors    │   │ Normalization │   │ Extraction    │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────┬───────┘  │
│                                                  │          │
│  ┌───────────────┐   ┌───────────────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ Significance  │◄──┤ Correlation   │◄──┤ Pattern       │  │
│  │ Testing       │   │ Analysis      │   │ Detection     │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────────────┘   └───────────────┘  │
│          │                                                  │
│  ┌───────▼───────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Insight       │──►│ Visualization │──►│ Recommendation│  │
│  │ Generation    │   │ Engine        │   │ Engine        │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### MentalHealthFederatedModel Components

```
┌─────────────────────────────────────────────────────────────┐
│                   MentalHealthFederatedModel                │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Local Data    │──►│ Privacy       │──►│ Feature       │  │
│  │ Processing    │   │ Preserving    │   │ Extraction    │  │
│  │               │   │ Pipeline      │   │               │  │
│  └───────────────┘   └───────────────┘   └───────┬───────┘  │
│                                                  │          │
│  ┌───────────────┐   ┌───────────────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ Secure        │◄──┤ Differential  │◄──┤ Local Model   │  │
│  │ Aggregation   │   │ Privacy       │   │ Training      │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────────────┘   └───────────────┘  │
│          │                                                  │
│  ┌───────▼───────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Global Model  │──►│ Local Model   │──►│ Insight       │  │
│  │ Distribution  │   │ Application   │   │ Generation    │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

# Epic 1: Visual Reference Document - Part 3
# UI/UX Mockups and User Interaction Flows

## User Interface Mockups

### Productivity Pattern Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Productivity Patterns Dashboard                    X  [_] [■]      │
│  ──────────────────────────────────────────────────────────────     │
│                                                                     │
│  Time Period: [Apr 1, 2023 - Apr 30, 2023] ▼                        │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │                  Weekly Productivity Heatmap              │      │
│  │                                                           │      │
│  │         Mon    Tue    Wed    Thu    Fri    Sat    Sun     │      │
│  │  9:00   ████   ████   ████   ████   ████   ▓▓▓▓   ░░░░    │      │
│  │ 10:00   ████   ████   ████   ████   ████   ▓▓▓▓   ░░░░    │      │
│  │ 11:00   ████   ████   ████   ████   ████   ▓▓▓▓   ░░░░    │      │
│  │ 12:00   ▓▓▓▓   ▓▓▓▓   ▓▓▓▓   ▓▓▓▓   ▓▓▓▓   ▓▓▓▓   ░░░░    │      │
│  │ 13:00   ▓▓▓▓   ▓▓▓▓   ▓▓▓▓   ▓▓▓▓   ▓▓▓▓   ████   ▓▓▓▓    │      │
│  │ 14:00   ████   ████   ████   ████   ▓▓▓▓   ████   ▓▓▓▓    │      │
│  │ 15:00   ████   ████   ████   ████   ████   ▓▓▓▓   ▓▓▓▓    │      │
│  │ 16:00   ▓▓▓▓   ▓▓▓▓   ████   ▓▓▓▓   ▓▓▓▓   ░░░░   ░░░░    │      │
│  │ 17:00   ▓▓▓▓   ▓▓▓▓   ▓▓▓▓   ▓▓▓▓   ▓▓▓▓   ░░░░   ░░░░    │      │
│  │                                                           │      │
│  │  ████ High Productivity    ▓▓▓▓ Medium     ░░░░ Low       │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌───────────────────────┐   ┌───────────────────────────────┐      │
│  │ Optimal Time Windows  │   │ Task Type Performance         │      │
│  │                       │   │                               │      │
│  │ Deep Work:            │   │ Coding:      9-11am, 2-4pm    │      │
│  │  Mon-Fri: 9-11am      │   │ Meetings:    1-3pm            │      │
│  │  Sat: 2-4pm           │   │ Creative:    10am-12pm        │      │
│  │                       │   │ Planning:    9-10am           │      │
│  │ Meetings:             │   │ Email/Admin: 4-5pm            │      │
│  │  Mon-Fri: 1-3pm       │   │                               │      │
│  │                       │   │                               │      │
│  └───────────────────────┘   └───────────────────────────────┘      │
│                                                                     │
│  [ Export Data ]   [ View Recommendations ]   [ Settings ]          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Circadian Rhythm Visualization

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Circadian Rhythm Analysis                           X  [_] [■]     │
│  ──────────────────────────────────────────────────────────────     │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │                   Your Energy Patterns                    │      │
│  │                                                           │      │
│  │ Energy                                                    │      │
│  │ Level    ┌─── Overall Energy  ┌─── Focus  ┌─── Creativity │      │
│  │          │                    │           │               │      │
│  │     10 ┼                                                  │      │
│  │        │                     ╭╮          ╭╮              │      │
│  │      8 ┼         ╭╮         ╱ ╰╮        ╱ ╰╮             │      │
│  │        │        ╱ ╰╮       ╱   ╰╮      ╱   ╰╮            │      │
│  │      6 ┼       ╱   ╰╮     ╱     ╰╮    ╱     ╰╮           │      │
│  │        │      ╱     ╰╮   ╱       ╰╮  ╱       ╰╮          │      │
│  │      4 ┼     ╱       ╰╮ ╱         ╰╮╱         ╰╮         │      │
│  │        │    ╱         ╰╮           ╰           ╰╮        │      │
│  │      2 ┼   ╱           ╰                         ╰        │      │
│  │        │  ╱                                                │      │
│  │      0 ┼─────────────────────────────────────────────────┐ │      │
│  │        │  2   4   6   8   10  12  14  16  18  20  22  24│ │      │
│  │          Hour of Day                                      │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌───────────────────────┐   ┌───────────────────────────────┐      │
│  │ Energy Pattern Factors│   │ Recommendations               │      │
│  │                       │   │                               │      │
│  │ Sleep Schedule:       │   │ • Schedule deep work between  │      │
│  │  ↳ Bedtime: ~11:30 PM │   │   9-11 AM when focus peaks    │      │
│  │  ↳ Wake: ~7:15 AM     │   │                               │      │
│  │                       │   │ • Take breaks around 1-2 PM   │      │
│  │ Primary Peak:         │   │   during your natural dip     │      │
│  │  ↳ 9:30-11:30 AM      │   │                               │      │
│  │                       │   │ • Schedule creative tasks     │      │
│  │ Secondary Peak:       │   │   during 3-5 PM secondary peak│      │
│  │  ↳ Afternoons 3-5 PM  │   │                               │      │
│  └───────────────────────┘   └───────────────────────────────┘      │
│                                                                     │
│  [ Set Reminders ]        [ Optimize My Schedule ]                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Productivity Correlation Insights

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Productivity Correlation Insights                   X  [_] [■]     │
│  ──────────────────────────────────────────────────────────────     │
│                                                                     │
│  Time Period: [Last 90 Days] ▼        Insight Type: [All] ▼         │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │             Factors Affecting Your Productivity           │      │
│  │                                                           │      │
│  │  Factor                Correlation    Confidence  Impact  │      │
│  │  ────────────────────  ────────────  ──────────  ─────── │      │
│  │  Sleep Duration        +0.72 (Strong)     95%     High   │      │
│  │  Morning Exercise      +0.68 (Strong)     92%     High   │      │
│  │  Meeting-Free Blocks   +0.65 (Strong)     93%     High   │      │
│  │  Working Past 9PM      -0.58 (Moderate)   90%     Medium │      │
│  │  Context Switching     -0.54 (Moderate)   89%     Medium │      │
│  │  Meditation Practice   +0.42 (Moderate)   85%     Medium │      │
│  │  Caffeine After 2PM    -0.40 (Moderate)   83%     Medium │      │
│  │  Outdoor Breaks        +0.38 (Moderate)   82%     Low    │      │
│  │  Social Media Usage    -0.37 (Moderate)   80%     Low    │      │
│  │                                                           │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │                    Key Insights                           │      │
│  │                                                           │      │
│  │  • You're 63% more productive after 7+ hours of sleep     │      │
│  │                                                           │      │
│  │  • Morning exercise (6-8am) correlates with 46% higher    │      │
│  │    focus scores during 9-11am window                      │      │
│  │                                                           │      │
│  │  • 2+ hour meeting-free blocks result in 3x more deep     │      │
│  │    work completion                                        │      │
│  │                                                           │      │
│  │  • Working past 9pm correlates with 37% lower productivity│      │
│  │    the following morning                                  │      │
│  │                                                           │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  [ Download Report ]   [ Experiment with Changes ]   [ Dismiss ]    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Federated Insights Privacy Settings

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Federated Learning Privacy Settings                 X  [_] [■]     │
│  ──────────────────────────────────────────────────────────────     │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ ☑ Participate in Federated Learning Program               │      │
│  │   Your data remains on your device, only model updates are│      │
│  │   shared.                                                 │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  Data Sharing Level:                                                │
│  ○ Basic (Default) - Share minimal data, basic insights             │
│  ● Advanced - Share more data, receive enhanced insights            │
│  ○ Maximum - Share comprehensive data for research                  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │              Privacy Protection Mechanisms                │      │
│  │                                                           │      │
│  │  • Differential Privacy:  [Strong] ▼                      │      │
│  │    Adds mathematical noise to protect individual data     │      │
│  │                                                           │      │
│  │  • Secure Aggregation:    [Enabled]                       │      │
│  │    Aggregates multiple users' updates before processing   │      │
│  │                                                           │      │
│  │  • Training Frequency:    [Weekly] ▼                      │      │
│  │    How often your device contributes to the model         │      │
│  │                                                           │      │
│  │  • Data Retention:        [90 Days] ▼                     │      │
│  │    How long personal data is kept before anonymization    │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ Population Insights Available to You with Current Settings│      │
│  │                                                           │      │
│  │ ✓ ADHD Productivity Patterns Across Demographics          │      │
│  │ ✓ Common Focus Blockers for ADHD Professionals            │      │
│  │ ✓ Effective Medication Timing Patterns                    │      │
│  │ ✓ Work Environment Factor Analysis                        │      │
│  │ ✓ Sleep Pattern Impact Comparison                         │      │
│  │ ✗ Detailed Medication Efficacy Analysis (requires Maximum)│      │
│  │ ✗ Industry-Specific Temporal Patterns (requires Maximum)  │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  [ Save Settings ]    [ Learn More About Data Privacy ]             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## User Interaction Flows

### Productivity Analysis Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  Dashboard    │────►│  Select       │────►│  View         │
│  Home         │     │  Time Period  │     │  Heatmap      │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│  Apply        │◄────│  Review       │◄────│  Explore      │
│  Insights     │     │  Suggestions  │     │  Patterns     │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

### Circadian Rhythm Detection Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  Report       │────►│  Record       │────►│  Submit       │
│  Energy Level │     │  Context      │     │  Data         │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│  Configure    │◄────│  View Energy  │◄────│  Process      │
│  Reminders    │     │  Patterns     │     │  Data         │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

### Correlation Analysis Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  Dashboard    │────►│  Navigate to  │────►│  Configure    │
│  Home         │     │  Insights     │     │  Analysis     │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│  Export       │◄────│  Explore      │◄────│  View         │
│  Report       │     │  Factor Impact│     │  Correlations │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

### Federated Learning Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  Open Privacy │────►│  Configure    │────►│  Review Data  │
│  Settings     │     │  Sharing Level│     │  Protections  │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│  View         │◄────│  Save         │◄────│  Confirm      │
│  Population   │     │  Settings     │     │  Consent      │
│  Insights     │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

# Epic 1: Visual Reference Document - Part 4
# Developer Reference Guides

## Key API Usage Examples

### Accessing Productivity Pattern Data

```typescript
// Example: Retrieving optimal productivity windows for a user
async function getOptimalTimeWindows(userId: string, taskType: string,
                                    dateRange: DateRange): Promise<TimeWindow[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/productivity/optimal-windows`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        task_type: taskType,
        start_date: dateRange.startDate,
        end_date: dateRange.endDate,
        minimum_window_length_minutes: 30
      })
    });

    if (!response.ok) {
      throw new Error(`Optimal windows request failed: ${response.status}`);
    }

    const data = await response.json();

    return data.windows.map(window => ({
      startTime: new Date(window.start_time),
      endTime: new Date(window.end_time),
      productivityScore: window.productivity_score,
      confidence: window.confidence,
      recommendedTaskTypes: window.recommended_task_types
    }));
  } catch (error) {
    console.error('Failed to get optimal time windows:', error);
    // Fallback to pre-computed defaults or cached data
    return getDefaultTimeWindows(taskType);
  }
}
```

### Working with Circadian Rhythm Data

```typescript
// Example: Submitting an energy report and getting predictions
async function reportAndPredictEnergy(
  userId: string,
  energyLevel: number,
  focusLevel: number,
  timestamp: Date
): Promise<EnergyPrediction[]> {
  try {
    // First, submit the current energy report
    const reportResponse = await fetch(`${API_BASE_URL}/circadian/report`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        timestamp: timestamp.toISOString(),
        energy_level: energyLevel,
        focus_level: focusLevel,
        context: {
          location: getCurrentLocation(),
          activity: getCurrentActivity()
        }
      })
    });

    if (!reportResponse.ok) {
      throw new Error(`Energy report submission failed: ${reportResponse.status}`);
    }

    // Then, get updated predictions for the next 24 hours
    const predictionResponse = await fetch(`${API_BASE_URL}/circadian/predict`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json'
      },
      params: {
        user_id: userId,
        hours_ahead: 24,
        include_focus: true,
        include_creativity: true
      }
    });

    if (!predictionResponse.ok) {
      throw new Error(`Energy prediction request failed: ${predictionResponse.status}`);
    }

    const predictionData = await predictionResponse.json();

    return predictionData.predictions.map(pred => ({
      timestamp: new Date(pred.timestamp),
      energyLevel: pred.energy_level,
      focusLevel: pred.focus_level,
      creativityLevel: pred.creativity_level,
      confidence: pred.confidence
    }));
  } catch (error) {
    console.error('Energy report and prediction failed:', error);
    // Return cached predictions if available
    return getCachedEnergyPredictions(userId);
  }
}
```

### Correlation Analysis

```typescript
// Example: Getting productivity correlation insights
async function getProductivityCorrelations(
  userId: string,
  timeFrame: string = 'last_90_days',
  minConfidence: number = 0.7
): Promise<CorrelationInsight[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/correlations/productivity-factors`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json'
      },
      params: {
        user_id: userId,
        time_frame: timeFrame,
        min_confidence: minConfidence,
        limit: 10,
        include_details: true
      }
    });

    if (!response.ok) {
      throw new Error(`Correlation analysis request failed: ${response.status}`);
    }

    const data = await response.json();

    // Transform the response into application-friendly format
    return data.correlations.map(correlation => ({
      factor: correlation.factor_name,
      correlationCoefficient: correlation.coefficient,
      isPositive: correlation.coefficient > 0,
      confidence: correlation.confidence,
      impactLevel: correlation.impact_level,
      description: correlation.description,
      recommendation: correlation.recommendation,
      actionable: correlation.actionable
    }));
  } catch (error) {
    console.error('Failed to get productivity correlations:', error);
    return [];
  }
}
```

## Integration Code Examples

### Calendar Integration with Productivity Patterns

```typescript
// Example: Integrating productivity patterns with calendar scheduling
class ProductivityAwareCalendar {
  private userId: string;
  private calendarService: CalendarService;
  private productivityService: ProductivityPatternService;

  constructor(userId: string, calendarService: CalendarService, productivityService: ProductivityPatternService) {
    this.userId = userId;
    this.calendarService = calendarService;
    this.productivityService = productivityService;
  }

  // Schedule a task optimized for productivity
  async scheduleOptimizedTask(task: Task): Promise<CalendarEvent> {
    try {
      // 1. Get upcoming calendar events for conflict checking
      const existingEvents = await this.calendarService.getEvents({
        userId: this.userId,
        startDate: new Date(),
        endDate: addDays(new Date(), 7)
      });

      // 2. Identify free time blocks
      const freeBlocks = this.identifyFreeTimeBlocks(existingEvents, {
        minBlockDuration: task.estimatedDuration + 10, // Add buffer
        maxDaysAhead: 7
      });

      // 3. Get optimal productivity windows for this task type
      const optimalWindows = await this.productivityService.getOptimalTimeWindows({
        userId: this.userId,
        taskType: task.type,
        dateRange: { startDate: new Date(), endDate: addDays(new Date(), 7) }
      });

      // 4. Find overlapping slots between free time and optimal productivity
      const candidates = this.findOverlappingTimeSlots(freeBlocks, optimalWindows);

      // Sort by productivity score
      candidates.sort((a, b) => b.productivityScore - a.productivityScore);

      if (candidates.length === 0) {
        throw new Error('No suitable time slots found');
      }

      // 5. Schedule the task in the best available slot
      const bestSlot = candidates[0];
      const scheduledEvent = await this.calendarService.createEvent({
        userId: this.userId,
        title: task.title,
        description: task.description,
        startTime: bestSlot.startTime,
        endTime: new Date(bestSlot.startTime.getTime() + task.estimatedDuration * 60000),
        metadata: {
          taskId: task.id,
          productivityScore: bestSlot.productivityScore,
          optimized: true
        }
      });

      return scheduledEvent;
    } catch (error) {
      console.error('Failed to schedule optimized task:', error);

      // Fallback to basic scheduling without optimization
      return this.calendarService.createBasicEvent(this.userId, task);
    }
  }

  // Helper methods
  private identifyFreeTimeBlocks(events: CalendarEvent[], options: FreeBlockOptions): TimeBlock[] {
    // Implementation of time block identification
    // ...
  }

  private findOverlappingTimeSlots(freeBlocks: TimeBlock[], optimalWindows: OptimalWindow[]): TimeSlot[] {
    // Implementation of overlap detection
    // ...
  }
}
```

### Data Visualization for Productivity Patterns

```typescript
// Example: Creating a productivity heatmap visualization using D3.js
function renderProductivityHeatmap(containerId: string, productivityData: ProductivityData[]) {
  const margin = { top: 30, right: 30, bottom: 30, left: 50 };
  const width = 800 - margin.left - margin.right;
  const height = 400 - margin.top - margin.bottom;

  // Process the data into a format suitable for a heatmap
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const hours = Array.from({ length: 12 }, (_, i) => i + 8); // 8AM to 7PM

  const heatmapData = [];
  for (const day of days) {
    for (const hour of hours) {
      const dataPoint = productivityData.find(d => d.day === day && d.hour === hour);
      heatmapData.push({
        day,
        hour,
        productivity: dataPoint ? dataPoint.productivityScore : 0
      });
    }
  }

  // Create SVG container
  const svg = d3.select(`#${containerId}`)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  // Build X scale and axis
  const x = d3.scaleBand()
    .range([0, width])
    .domain(days)
    .padding(0.05);

  svg.append('g')
    .style('font-size', 12)
    .attr('transform', `translate(0, ${height})`)
    .call(d3.axisBottom(x).tickSize(0))
    .select('.domain').remove();

  // Build Y scale and axis
  const y = d3.scaleBand()
    .range([height, 0])
    .domain(hours.map(String))
    .padding(0.05);

  svg.append('g')
    .style('font-size', 12)
    .call(d3.axisLeft(y)
      .tickSize(0)
      .tickFormat(d => `${d}:00`)
    )
    .select('.domain').remove();

  // Build color scale
  const color = d3.scaleSequential()
    .interpolator(d3.interpolateViridis)
    .domain([0, 10]); // Assuming productivity score range of 0-10

  // Add the squares
  svg.selectAll()
    .data(heatmapData, d => `${d.day}:${d.hour}`)
    .enter()
    .append('rect')
    .attr('x', d => x(d.day))
    .attr('y', d => y(String(d.hour)))
    .attr('rx', 4)
    .attr('ry', 4)
    .attr('width', x.bandwidth())
    .attr('height', y.bandwidth())
    .style('fill', d => color(d.productivity))
    .style('stroke-width', 4)
    .style('stroke', 'none')
    .style('opacity', 0.8)
    .on('mouseover', function(event, d) {
      d3.select(this).style('stroke', 'black');

      // Add tooltip
      tooltip
        .style('opacity', 1)
        .html(`Day: ${d.day}<br>Time: ${d.hour}:00<br>Productivity: ${d.productivity.toFixed(1)}`)
        .style('left', `${event.pageX + 10}px`)
        .style('top', `${event.pageY - 10}px`);
    })
    .on('mouseleave', function() {
      d3.select(this).style('stroke', 'none');
      tooltip.style('opacity', 0);
    });

  // Add title
  svg.append('text')
    .attr('x', 0)
    .attr('y', -10)
    .attr('text-anchor', 'left')
    .style('font-size', 16)
    .text('Weekly Productivity Heatmap');

  // Add color legend
  const legend = svg.append('g')
    .attr('transform', `translate(${width - 120}, 0)`);

  const legendScale = d3.scaleLinear()
    .domain([0, 10])
    .range([height, 0]);

  const legendAxis = d3.axisRight(legendScale)
    .tickValues([0, 2.5, 5, 7.5, 10])
    .tickFormat(d3.format('.1f'));

  legend.append('g')
    .call(legendAxis);

  // Create tooltip div
  const tooltip = d3.select(`#${containerId}`)
    .append('div')
    .style('opacity', 0)
    .style('background-color', 'white')
    .style('border', 'solid 1px #ccc')
    .style('border-radius', '5px')
    .style('padding', '10px')
    .style('position', 'absolute');
}
```

### Federated Learning Integration

```typescript
// Example: Integrating with the federated learning system
class FederatedLearningClient {
  private userId: string;
  private modelVersion: string;
  private privacySettings: PrivacySettings;
  private federatedService: FederatedLearningService;

  constructor(userId: string, federatedService: FederatedLearningService) {
    this.userId = userId;
    this.federatedService = federatedService;
    this.modelVersion = '1.0.0';
    this.privacySettings = {
      differentialPrivacyEpsilon: 0.1,
      secureAggregation: true,
      dataRetentionDays: 90,
      sharingLevel: 'basic'
    };
  }

  // Initialize federated learning for this client
  async initialize(): Promise<void> {
    try {
      // Check if user has given consent
      const userConsent = await this.federatedService.getUserConsent(this.userId);

      if (!userConsent.hasConsented) {
        console.log('User has not given consent for federated learning');
        return;
      }

      // Apply user's privacy settings
      this.privacySettings = {
        ...this.privacySettings,
        ...userConsent.privacySettings
      };

      // Initialize the local model
      await this.federatedService.initializeLocalModel({
        userId: this.userId,
        modelVersion: this.modelVersion,
        privacySettings: this.privacySettings
      });

      // Set up update schedule
      this.setupUpdateSchedule();

    } catch (error) {
      console.error('Failed to initialize federated learning client:', error);
    }
  }

  // Contribute to federated model
  async contributeToGlobalModel(): Promise<void> {
    try {
      if (!navigator.onLine) {
        console.log('Device offline, skipping contribution');
        return;
      }

      // Get local training data (without sending raw data)
      const trainingStats = await this.federatedService.trainLocalModel({
        userId: this.userId,
        differentialPrivacyEpsilon: this.privacySettings.differentialPrivacyEpsilon
      });

      // Extract model updates (not the data itself)
      const modelUpdates = await this.federatedService.extractModelUpdates();

      // Send model updates to server
      await this.federatedService.contributeModelUpdates({
        userId: this.userId,
        modelVersion: this.modelVersion,
        updates: modelUpdates,
        trainingStats: {
          samplesCount: trainingStats.samplesCount,
          lossValue: trainingStats.lossValue,
          accuracy: trainingStats.accuracy
        }
      });

      console.log('Successfully contributed to federated model');

    } catch (error) {
      console.error('Failed to contribute to federated model:', error);
    }
  }

  // Get insights from the federated model
  async getFederatedInsights(): Promise<FederatedInsight[]> {
    try {
      // Get insights that match user's sharing level
      const insights = await this.federatedService.getPopulationInsights({
        userId: this.userId,
        sharingLevel: this.privacySettings.sharingLevel
      });

      return insights.map(insight => ({
        category: insight.category,
        title: insight.title,
        description: insight.description,
        populationSize: insight.population_size,
        relevanceScore: insight.relevance_score,
        personalized: insight.personalized
      }));

    } catch (error) {
      console.error('Failed to get federated insights:', error);
      return [];
    }
  }

  // Helper method to schedule updates
  private setupUpdateSchedule(): void {
    // Schedule periodic model updates
    const updateFrequencyMs = 24 * 60 * 60 * 1000; // Daily

    setInterval(() => {
      if (this.isDeviceIdle() && navigator.onLine) {
        this.contributeToGlobalModel();
      }
    }, updateFrequencyMs);
  }

  private isDeviceIdle(): boolean {
    // Implementation to check if device is idle
    // ...
    return true;
  }
}
```

## Error Handling Patterns

### Graceful Degradation with Fallbacks

```typescript
// Example: Multi-level fallback for productivity pattern service
class ProductivityPatternService {
  private apiClient: ApiClient;
  private cacheManager: CacheManager;
  private localStorage: LocalStorage;
  private telemetry: TelemetryService;

  constructor(
    apiClient: ApiClient,
    cacheManager: CacheManager,
    localStorage: LocalStorage,
    telemetry: TelemetryService
  ) {
    this.apiClient = apiClient;
    this.cacheManager = cacheManager;
    this.localStorage = localStorage;
    this.telemetry = telemetry;
  }

  // Get productivity patterns with multi-level fallbacks
  async getProductivityPatterns(
    userId: string,
    dateRange: DateRange,
    options: PatternOptions = {}
  ): Promise<ProductivityPattern> {
    try {
      // Try cache first for fastest response
      const cachedPattern = await this.cacheManager.get(
        `productivity_pattern:${userId}:${dateRange.startDate}:${dateRange.endDate}`
      );

      if (cachedPattern && !this.isCacheStale(cachedPattern)) {
        this.telemetry.trackEvent('productivity_pattern_source', { source: 'cache' });
        return cachedPattern;
      }

      // Cache miss or stale cache, try API
      try {
        const apiPattern = await this.apiClient.get('/productivity/patterns', {
          userId,
          startDate: dateRange.startDate,
          endDate: dateRange.endDate,
          taskTypes: options.taskTypes || [],
          resolution: options.resolution || 'hourly'
        });

        // Cache the fresh result
        await this.cacheManager.set(
          `productivity_pattern:${userId}:${dateRange.startDate}:${dateRange.endDate}`,
          apiPattern,
          { ttl: 3600 } // 1 hour cache
        );

        this.telemetry.trackEvent('productivity_pattern_source', { source: 'api' });
        return apiPattern;
      } catch (apiError) {
        // API failed, try local database (might have synced data)
        try {
          const localPattern = await this.localStorage.getProductivityPattern(userId, dateRange);

          if (localPattern) {
            this.telemetry.trackEvent('productivity_pattern_source', {
              source: 'local_db',
              api_error: apiError.message
            });
            return {
              ...localPattern,
              _metadata: {
                source: 'local_db',
                lastUpdated: localPattern._metadata?.lastUpdated,
                confidence: Math.min(localPattern._metadata?.confidence || 0.8, 0.8) // Cap confidence
              }
            };
          }
        } catch (localDbError) {
          // Local DB failed too, log it
          this.telemetry.trackException('local_db_error', {
            error: localDbError.message,
            context: 'productivity_pattern_fallback'
          });
        }

        // Both API and local DB failed, use default patterns
        const defaultPattern = this.getDefaultPatterns(dateRange);

        this.telemetry.trackEvent('productivity_pattern_source', {
          source: 'defaults',
          api_error: apiError.message
        });

        return {
          ...defaultPattern,
          _metadata: {
            source: 'defaults',
            lastUpdated: new Date(),
            confidence: 0.5, // Low confidence
            message: 'Using default patterns due to connectivity issues'
          }
        };
      }
    } catch (error) {
      // Catch-all for unexpected errors
      this.telemetry.trackException('productivity_pattern_error', {
        error: error.message,
        stack: error.stack
      });

      // Provide bare minimum default pattern to prevent UI crashes
      return this.getEmergencyDefaultPattern(dateRange);
    }
  }

  // Helper methods
  private isCacheStale(cachedData: any): boolean {
    if (!cachedData._metadata?.lastUpdated) return true;

    const cacheTime = new Date(cachedData._metadata.lastUpdated).getTime();
    const now = Date.now();
    const maxAgeMs = 60 * 60 * 1000; // 1 hour

    return (now - cacheTime) > maxAgeMs;
  }

  private getDefaultPatterns(dateRange: DateRange): ProductivityPattern {
    // Implementation of sensible defaults based on population averages
    // ...
  }

  private getEmergencyDefaultPattern(dateRange: DateRange): ProductivityPattern {
    // Simplest possible pattern to prevent app crashes
    // ...
  }
}
```

### Centralized Error Handling

```typescript
// Example: Centralized error handler for consistent error handling
class ErrorHandler {
  private telemetry: TelemetryService;
  private notificationService: NotificationService;
  private retryPolicy: RetryPolicy;

  constructor(
    telemetry: TelemetryService,
    notificationService: NotificationService,
    retryPolicy: RetryPolicy
  ) {
    this.telemetry = telemetry;
    this.notificationService = notificationService;
    this.retryPolicy = retryPolicy;
  }

  // Handle API errors consistently across the application
  handleApiError(error: any, context: ErrorContext): ErrorResult {
    // Log the error with context
    this.telemetry.logError({
      message: error.message,
      code: error.code || 'unknown',
      context: context.operation,
      component: context.component,
      userId: context.userId,
      timestamp: new Date().toISOString()
    });

    // Determine if the error is retryable
    const isRetryable = this.isRetryableError(error);

    // For retryable errors, check if we should retry
    if (isRetryable && this.retryPolicy.shouldRetry(context.operation, context.attempts)) {
      const nextRetryDelay = this.retryPolicy.getNextRetryDelay(context.operation, context.attempts);

      return {
        type: 'retry',
        userMessage: 'Temporary issue connecting to service. Retrying...',
        retryDelay: nextRetryDelay,
        shouldNotifyUser: context.attempts > 2 // Only notify after multiple attempts
      };
    }

    // User-facing error messages by error type
    const userMessage = this.getUserFriendlyMessage(error, context);

    // For authentication errors, redirect to login
    if (error.code === 'unauthorized' || error.code === 'forbidden') {
      return {
        type: 'auth_error',
        userMessage,
        redirectUrl: '/login',
        shouldNotifyUser: true
      };
    }

    // For connectivity errors
    if (error.code === 'network_error' || error.name === 'NetworkError') {
      return {
        type: 'connectivity_error',
        userMessage,
        offlineAction: context.offlineAction,
        shouldNotifyUser: true
      };
    }

    // For service unavailable
    if (error.code === 'service_unavailable') {
      // Notify user and suggest trying later
      this.notificationService.showToast({
        message: userMessage,
        type: 'warning',
        duration: 5000
      });

      return {
        type: 'service_error',
        userMessage,
        shouldNotifyUser: false, // Already notified
        fallbackData: context.fallbackData
      };
    }

    // Default case - general error
    return {
      type: 'error',
      userMessage,
      shouldNotifyUser: true,
      fallbackData: context.fallbackData
    };
  }

  // Helper methods
  private isRetryableError(error: any): boolean {
    const retryableCodes = ['timeout', 'service_unavailable', 'too_many_requests', 'network_error'];
    return retryableCodes.includes(error.code) || error.status === 429 || error.status === 503;
  }

  private getUserFriendlyMessage(error: any, context: ErrorContext): string {
    // Map error codes/types to user-friendly messages
    const errorMessages: Record<string, string> = {
      'network_error': 'Unable to connect. Please check your internet connection.',
      'unauthorized': 'Your session has expired. Please log in again.',
      'forbidden': 'You don\'t have permission to access this feature.',
      'not_found': 'The requested information could not be found.',
      'service_unavailable': 'This service is currently unavailable. Please try again later.',
      'timeout': 'The request took too long to complete. Please try again.'
    };

    // Return specific message or default message
    return errorMessages[error.code] ||
           'An unexpected error occurred. Our team has been notified.';
  }
}
```

## Testing Code Examples

### Unit Testing the Productivity Pattern LSTM Model

```typescript
// Example: Jest tests for the ProductivityPatternLSTM class
describe('ProductivityPatternLSTM', () => {
  let model: ProductivityPatternLSTM;
  let mockData: ProductivityData[];

  beforeEach(() => {
    // Set up test data
    mockData = [
      {
        userId: 'test-user-1',
        timestamp: new Date('2023-05-01T09:00:00Z'),
        productivity: 8,
        focus: 7,
        taskType: 'coding',
        duration: 60
      },
      // Additional test data...
    ];

    // Create model instance with dependencies
    const mockDataService = {
      getUserData: jest.fn().mockResolvedValue(mockData)
    };

    const mockTensorflowService = {
      createModel: jest.fn(),
      trainModel: jest.fn().mockResolvedValue({ loss: 0.15, accuracy: 0.85 }),
      predict: jest.fn().mockImplementation((input) => {
        // Mock prediction logic based on input
        return Array.from({ length: input.length }, () => ({
          productivity: 7 + Math.random() * 2,
          focus: 6 + Math.random() * 3
        }));
      })
    };

    model = new ProductivityPatternLSTM(mockDataService, mockTensorflowService);
  });

  describe('train', () => {
    it('should process training data correctly', async () => {
      // Arrange
      const userId = 'test-user-1';
      const mockProcessedData = { features: [], labels: [] };
      jest.spyOn(model as any, 'processTrainingData').mockReturnValue(mockProcessedData);

      // Act
      const result = await model.train(userId);

      // Assert
      expect(model['dataService'].getUserData).toHaveBeenCalledWith(userId);
      expect(model['processTrainingData']).toHaveBeenCalledWith(mockData);
      expect(model['tensorflowService'].trainModel).toHaveBeenCalledWith(
        expect.any(Object),
        mockProcessedData,
        expect.any(Object)
      );
      expect(result.accuracy).toBeGreaterThan(0.8);
    });

    it('should handle empty training data', async () => {
      // Arrange
      const userId = 'empty-user';
      jest.spyOn(model['dataService'], 'getUserData').mockResolvedValue([]);

      // Act & Assert
      await expect(model.train(userId)).rejects.toThrow('Insufficient training data');
    });
  });

  describe('predictOptimalWindows', () => {
    it('should identify optimal windows for given task type', async () => {
      // Arrange
      const userId = 'test-user-1';
      const taskType = 'coding';
      const dateRange = {
        startDate: new Date('2023-05-10'),
        endDate: new Date('2023-05-11')
      };

      // Mock internal methods
      jest.spyOn(model as any, 'generateTimeSlots').mockReturnValue([
        { dayOfWeek: 1, hour: 9 },
        { dayOfWeek: 1, hour: 10 },
        // ... more time slots
      ]);

      // Act
      const windows = await model.predictOptimalWindows(userId, taskType, dateRange);

      // Assert
      expect(windows.length).toBeGreaterThan(0);
      windows.forEach(window => {
        expect(window.startTime).toBeInstanceOf(Date);
        expect(window.endTime).toBeInstanceOf(Date);
        expect(window.endTime > window.startTime).toBe(true);
        expect(window.productivityScore).toBeGreaterThanOrEqual(0);
        expect(window.productivityScore).toBeLessThanOrEqual(10);
      });
    });

    it('should return windows sorted by productivity score', async () => {
      // Arrange
      const userId = 'test-user-1';
      const taskType = 'coding';
      const dateRange = {
        startDate: new Date('2023-05-10'),
        endDate: new Date('2023-05-11')
      };

      // Act
      const windows = await model.predictOptimalWindows(userId, taskType, dateRange);

      // Assert
      expect(windows).toBeSorted((a, b) => b.productivityScore - a.productivityScore);
    });
  });

  // Additional test cases...
});
```

### Integration Testing the Circadian Rhythm Model

```typescript
// Example: Integration test for CircadianRhythmModel
describe('CircadianRhythmModel Integration', () => {
  let model: CircadianRhythmModel;
  let database: TestDatabase;

  beforeAll(async () => {
    // Set up test database with seed data
    database = new TestDatabase();
    await database.connect();
    await database.seed('./test/fixtures/circadian_test_data.json');

    // Create real instance with test dependencies
    model = new CircadianRhythmModel(
      new DataRepository(database),
      new RhythmProcessor()
    );
  });

  afterAll(async () => {
    await database.disconnect();
  });

  it('should predict energy levels for a full day', async () => {
    // Arrange
    const userId = 'test-user-1';
    const date = new Date('2023-05-15'); // Monday

    // Act
    const predictions = await model.predictDailyEnergyCurve(userId, date);

    // Assert
    expect(predictions).toHaveLength(24); // One prediction per hour
    predictions.forEach((prediction, index) => {
      expect(prediction.hour).toBe(index);
      expect(prediction.energyLevel).toBeGreaterThanOrEqual(1);
      expect(prediction.energyLevel).toBeLessThanOrEqual(10);
      expect(prediction.focusLevel).toBeGreaterThanOrEqual(1);
      expect(prediction.focusLevel).toBeLessThanOrEqual(10);
    });

    // Check morning peak (for this test user)
    const morningPeak = predictions.find(p => p.hour === 10);
    expect(morningPeak.energyLevel).toBeGreaterThan(7);

    // Check afternoon dip
    const afternoonDip = predictions.find(p => p.hour === 14);
    expect(afternoonDip.energyLevel).toBeLessThan(6);
  });

  it('should incorporate recent energy reports', async () => {
    // Arrange
    const userId = 'test-user-1';
    const date = new Date('2023-05-16'); // Tuesday

    // Add a recent energy report that should influence the model
    await model.submitEnergyReport(userId, {
      timestamp: new Date('2023-05-16T08:00:00Z'),
      energyLevel: 9, // Very high morning energy
      focusLevel: 8
    });

    // Act
    const predictions = await model.predictDailyEnergyCurve(userId, date);

    // Assert
    // Morning predictions should be influenced by recent high energy report
    const morningPredictions = predictions.filter(p => p.hour >= 8 && p.hour <= 11);
    morningPredictions.forEach(prediction => {
      expect(prediction.energyLevel).toBeGreaterThan(7);
    });
  });

  it('should detect optimal windows based on energy type', async () => {
    // Arrange
    const userId = 'test-user-1';
    const date = new Date('2023-05-17'); // Wednesday

    // Act
    const focusWindows = await model.detectOptimalWindows(userId, date, {
      energyType: 'focus',
      minLevel: 7,
      minDurationMinutes: 60
    });

    const creativeWindows = await model.detectOptimalWindows(userId, date, {
      energyType: 'creativity',
      minLevel: 7,
      minDurationMinutes: 60
    });

    // Assert
    expect(focusWindows.length).toBeGreaterThan(0);
    expect(creativeWindows.length).toBeGreaterThan(0);

    // Focus windows should be different from creative windows
    const focusStartTimes = focusWindows.map(w => w.startTime.getTime());
    const creativeStartTimes = creativeWindows.map(w => w.startTime.getTime());

    // There should be some difference in the optimal windows
    const differentWindows = focusStartTimes.filter(time => !creativeStartTimes.includes(time));
    expect(differentWindows.length).toBeGreaterThan(0);
  });
});
```
