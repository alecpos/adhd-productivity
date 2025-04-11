# Epic 2: Visual Reference Document - Part 1
# Stochastic Time Estimation Engine

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
│Bayesian Duration   │ │NLP Complexity   │ │Contextual Stressor │
│Predictor Service   │ │Analyzer Service │ │Detector Service    │
└─────────┬──────────┘ └────────┬───────┘ └──────────┬─────────┘
          │                     │                    │
          │                     ▼                    │
          │         ┌────────────────────────┐      │
          └────────►│Time Estimation Database◄──────┘
                    └────────────┬───────────┘
                                 │
                                 ▼
                   ┌─────────────────────────────┐
                   │Time Buffer Calculator       │
                   │Service                      │
                   └──────────┬──────────────────┘
                              │
                              ▼
                   ┌─────────────────────────┐
                   │Calendar & Task          │
                   │Integration Service      │
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
│Bayesian │  │NLP      │  │Stressor     │  │Time Buffer    │
│Predictor│  │Analyzer │  │Detector     │  │Calculator     │
│         │  │         │  │             │  │               │
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
│  │  Redis      │     │  In-Memory  │    │  Model      │ │
│  │  Cache      │     │  Cache      │    │  Cache      │ │
│  │             │     │             │    │             │ │
│  └─────────────┘     └─────────────┘    └─────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### MongoDB Collection Relationships

```
┌───────────────────────────────┐
│      TaskDurationEstimate     │
├───────────────────────────────┤
│ _id: ObjectId                 │
│ user_id: UUID                 │──────┐
│ task_id: UUID                 │──────┼─────┐
│ estimated_duration_minutes:   │      │     │
│ confidence_interval_lower:    │      │     │
│ confidence_interval_upper:    │      │     │
│ contextual_factors: JSON      │      │     │
│ model_version: String         │      │     │
│ created_at: DateTime          │      │     │
└───────────────────────────────┘      │     │
                                       │     │
┌───────────────────────────────┐      │     │
│   TaskComplexityAnalysis      │      │     │
├───────────────────────────────┤      │     │
│ _id: ObjectId                 │      │     │
│ task_id: UUID  ───────────────┼──────┘     │
│ complexity_score: Float       │            │
│ cognitive_load: Float         │            │
│ ambiguity_index: Float        │            │
│ technical_terms: Array        │            │
│ complexity_factors: JSON      │            │
│ created_at: DateTime          │            │
└───────────────────────────────┘            │
                                             │
┌───────────────────────────────┐            │
│   UserStressorRecord          │            │
├───────────────────────────────┤            │
│ _id: ObjectId                 │            │
│ user_id: UUID                 │            │
│ timestamp: DateTime           │            │
│ stressor_type: String         │            │
│ stressor_details: JSON        │            │
│ intensity: Float              │            │
│ focus_impact: Float           │            │
│ cognitive_impact: Float       │            │
│ created_at: DateTime          │            │
└───────────────────────────────┘            │
                                             │
┌───────────────────────────────┐            │
│   TimeBuffer                  │            │
├───────────────────────────────┤            │
│ _id: ObjectId                 │            │
│ user_id: UUID                 │            │
│ prev_task_id: UUID            │            │
│ next_task_id: UUID  ──────────┼────────────┘
│ recommended_buffer_minutes:   │
│ buffer_components: JSON       │
│ transition_difficulty: Float  │
│ context_factors: JSON         │
│ created_at: DateTime          │
└───────────────────────────────┘
```

# Epic 2: Visual Reference Document - Part 2
# Data Flow and Component Interaction

## Data Flow Diagrams

### Task Duration Prediction Flow

```
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│               │    │                 │    │                 │
│ Task Creation │───►│ Task Description│───►│ NLP Complexity  │
│ Event         │    │ Processing      │    │ Analysis        │
│               │    │                 │    │                 │
└───────────────┘    └─────────────────┘    └────────┬────────┘
                                                     │
┌───────────────┐    ┌─────────────────┐    ┌────────▼────────┐
│               │    │                 │    │                 │
│ Duration      │◄───│ Bayesian        │◄───│ Historical Task │
│ Estimate      │    │ Prediction      │    │ Data Retrieval  │
│               │    │                 │    │                 │
└───────────────┘    └─────────────────┘    └─────────────────┘
                            ▲
                            │
                     ┌──────┴──────┐
                     │             │
                     │ Contextual  │
                     │ Stressors   │
                     │             │
                     └─────────────┘
```

### Contextual Stressor Detection Flow

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│              │      │              │      │              │
│ Wearable     │─────►│ Environmental│─────►│ Digital      │
│ Data Sources │      │ Sensors      │      │ Activity     │
│              │      │              │      │              │
└──────────────┘      └──────────────┘      └──────┬───────┘
                                                   │
┌──────────────┐      ┌──────────────┐      ┌──────▼───────┐
│              │      │              │      │              │
│ Stressor     │◄─────│ Pattern      │◄─────│ Data Fusion  │
│ Database     │      │ Recognition  │      │ Engine       │
│              │      │              │      │              │
└──────────────┘      └──────────────┘      └──────────────┘
```

### Time Buffer Calculation Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│ Task Sequence │────►│ Transition    │────►│ Cognitive     │
│ Analysis      │     │ Complexity    │     │ Load Analysis │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│ Buffer        │◄────│ Buffer        │◄────│ Stressor      │
│ Integration   │     │ Optimization  │     │ Impact        │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

### Model Learning Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│ Actual        │────►│ Prediction    │────►│ Error         │
│ Durations     │     │ Comparison    │     │ Analysis      │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│ Updated       │◄────│ Model         │◄────│ Parameter     │
│ Predictions   │     │ Refinement    │     │ Adjustment    │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

## Component Interaction Diagrams

### BayesianDurationPredictor Components

```
┌─────────────────────────────────────────────────────────────┐
│                   BayesianDurationPredictor                 │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Data          │──►│ Prior         │──►│ Hierarchical  │  │
│  │ Collection    │   │ Generation    │   │ Model Builder │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────┬───────┘  │
│                                                  │          │
│  ┌───────────────┐   ┌───────────────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ Confidence    │◄──┤ Monte Carlo   │◄──┤ Bayesian      │  │
│  │ Calculation   │   │ Simulation    │   │ Inference     │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────────────┘   └───────────────┘  │
│          │                                                  │
│  ┌───────▼───────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Prediction    │──►│ Context       │──►│ Explanation   │  │
│  │ Generation    │   │ Adjustment    │   │ Generator     │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### NLPComplexityAnalyzer Components

```
┌─────────────────────────────────────────────────────────────┐
│                     NLPComplexityAnalyzer                   │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Text          │──►│ Preprocessing │──►│ Named Entity  │  │
│  │ Tokenization  │   │ Pipeline      │   │ Recognition   │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────┬───────┘  │
│                                                  │          │
│  ┌───────────────┐   ┌───────────────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ Structural    │◄──┤ Dependency    │◄──┤ Technical     │  │
│  │ Complexity    │   │ Parsing       │   │ Term Analysis │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────────────┘   └───────────────┘  │
│          │                                                  │
│  ┌───────▼───────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Ambiguity     │──►│ Cognitive     │──►│ Composite     │  │
│  │ Detection     │   │ Load Analysis │   │ Score Builder │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### ContextualStressorDetector Components

```
┌─────────────────────────────────────────────────────────────┐
│                 ContextualStressorDetector                  │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Data Source   │──►│ Signal        │──►│ Feature       │  │
│  │ Connectors    │   │ Processing    │   │ Extraction    │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────┬───────┘  │
│                                                  │          │
│  ┌───────────────┐   ┌───────────────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ Stressor      │◄──┤ Pattern       │◄──┤ Multi-modal   │  │
│  │ Classification│   │ Recognition   │   │ Fusion        │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────────────┘   └───────────────┘  │
│          │                                                  │
│  ┌───────▼───────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Impact        │──►│ Historical    │──►│ Prediction    │  │
│  │ Assessment    │   │ Correlation   │   │ Engine        │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### TimeBufferCalculator Components

```
┌─────────────────────────────────────────────────────────────┐
│                   TimeBufferCalculator                      │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Task Sequence │──►│ Cognitive     │──►│ Context       │  │
│  │ Analyzer      │   │ Switch Cost   │   │ Assessment    │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────┬───────┘  │
│                                                  │          │
│  ┌───────────────┐   ┌───────────────┐   ┌───────▼───────┐  │
│  │               │   │               │   │               │  │
│  │ Buffer        │◄──┤ Recovery      │◄──┤ Stressor      │  │
│  │ Optimization  │   │ Estimation    │   │ Integration   │  │
│  │               │   │               │   │               │  │
│  └───────┬───────┘   └───────────────┘   └───────────────┘  │
│          │                                                  │
│  ┌───────▼───────┐   ┌───────────────┐   ┌───────────────┐  │
│  │               │   │               │   │               │  │
│  │ Schedule      │──►│ User          │──►│ Learning      │  │
│  │ Integration   │   │ Feedback      │   │ Engine        │  │
│  │               │   │               │   │               │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

# Epic 2: Visual Reference Document - Part 3
# UI/UX Mockups and User Interaction Flows

## User Interface Mockups

### Task Duration Estimation Interface

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Task Duration Estimation                           X  [_] [■]      │
│  ──────────────────────────────────────────────────────────────     │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ Task Details                                               │      │
│  │                                                           │      │
│  │ Title: Prepare quarterly report for marketing team        │      │
│  │                                                           │      │
│  │ Description:                                              │      │
│  │ Compile data from Q2 sales, organize into presentation    │      │
│  │ format, create executive summary, and add visualization   │      │
│  │ charts for key metrics. Need to coordinate with Sarah     │      │
│  │ about design templates.                                   │      │
│  │                                                           │      │
│  │ Category: [Report Writing     ▼]  Priority: [High     ▼]  │      │
│  │                                                           │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ Duration Estimate                                         │      │
│  │                                                           │      │
│  │  Realistic Duration:  2 hr 45 min                         │      │
│  │                       (Range: 2h 15m - 3h 30m)            │      │
│  │                                                           │      │
│  │  Confidence Level:    85%                                 │      │
│  │                                                           │      │
│  │  [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░]                                  │      │
│  │   0      1h      2h      3h      4h      5h              │      │
│  │                                                           │      │
│  │  Historical Average: 2h 30m for similar tasks             │      │
│  │                                                           │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ Adjustment Factors                                        │      │
│  │                                                           │      │
│  │  Complexity:        Medium-High    (+25 min)              │      │
│  │  Context Switches:  2 expected     (+15 min)              │      │
│  │  Current Focus:     Moderate       (+10 min)              │      │
│  │  Current Stressors: Low            (+5 min)               │      │
│  │  Time of Day:       Morning        (-10 min)              │      │
│  │                                                           │      │
│  │  [View Details]                                           │      │
│  │                                                           │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  [  Save Estimate  ]   [  Schedule  ]   [  Adjust Factors  ]        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Complexity Analysis View

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Task Complexity Analysis                           X  [_] [■]      │
│  ──────────────────────────────────────────────────────────────     │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ Analyzed Task: Prepare quarterly report for marketing team│      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ Complexity Breakdown                                      │      │
│  │                                                           │      │
│  │  Overall Complexity: 68/100                               │      │
│  │  [▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░]                                  │      │
│  │                                                           │      │
│  │  Component Analysis:                                      │      │
│  │                                                           │      │
│  │  Cognitive Load:      7.2/10   [▓▓▓▓▓▓▓▓░░]              │      │
│  │  Ambiguity:           3.5/10   [▓▓▓▓░░░░░░]              │      │
│  │  Technical Content:   6.8/10   [▓▓▓▓▓▓▓░░░]              │      │
│  │  Collaboration Need:  8.5/10   [▓▓▓▓▓▓▓▓▓░]              │      │
│  │  Decision Points:     5.4/10   [▓▓▓▓▓░░░░░]              │      │
│  │                                                           │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ Detected Subtasks                                         │      │
│  │                                                           │      │
│  │  • Data compilation (30-45 min)                           │      │
│  │  • Chart creation (45-60 min)                             │      │
│  │  • Executive summary writing (25-40 min)                  │      │
│  │  • Coordination with design team (15-20 min)              │      │
│  │  • Final assembly and review (20-30 min)                  │      │
│  │                                                           │      │
│  │  Total identified subtasks: 5                             │      │
│  │                                                           │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ Recommendations                                           │      │
│  │                                                           │      │
│  │  • Break into explicit subtasks to track progress         │      │
│  │  • Schedule during your high focus period (9-11am)        │      │
│  │  • Add 30-minute buffer for unexpected complexity         │      │
│  │  • Contact Sarah at least 1 day before for templates      │      │
│  │                                                           │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  [  Apply Recommendations  ]    [  Back to Estimate  ]              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stressor Detection Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Current Stressors                                 X  [_] [■]       │
│  ──────────────────────────────────────────────────────────────     │
│                                                                     │
│  Time Period: [Today   ▼]        View: [Detailed ▼]                │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ Current Stressor Level: 42/100 (Moderate)                 │      │
│  │                                                           │      │
│  │ [▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]│      │
│  │  0   10   20   30   40   50   60   70   80   90   100     │      │
│  │  Low          Moderate           High          Extreme    │      │
│  │                                                           │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ Stressor Breakdown                                        │      │
│  │                                                           │      │
│  │  Environmental Factors:                                   │      │
│  │   • Office noise level: 65dB (Moderate)       [▓▓▓▓▓░░░░░]│      │
│  │   • Interruption frequency: 4/hour (High)     [▓▓▓▓▓▓▓░░░]│      │
│  │   • Meeting load: 2 hours today (Low)         [▓▓░░░░░░░░]│      │
│  │                                                           │      │
│  │  Physiological Factors:                                   │      │
│  │   • Sleep quality: 7.2/10 (Good)              [▓▓░░░░░░░░]│      │
│  │   • Focus stability: Fluctuating              [▓▓▓▓▓░░░░░]│      │
│  │   • Energy level: 65% (Moderate)              [▓▓▓▓░░░░░░]│      │
│  │                                                           │      │
│  │  Deadline Pressure:                                       │      │
│  │   • 2 tasks due today (Moderate)              [▓▓▓▓▓░░░░░]│      │
│  │   • 1 high-priority task approaching          [▓▓▓▓▓▓░░░░]│      │
│  │                                                           │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ Impact on Performance                                     │      │
│  │                                                           │      │
│  │  Estimated focus reduction: 15%                           │      │
│  │  Estimated task duration increase: ~25%                   │      │
│  │  Context switching cost: 8-12 minutes per switch          │      │
│  │                                                           │      │
│  │  Current best for:                                        │      │
│  │   ✓ Administrative tasks                                  │      │
│  │   ✓ Collaborative work                                    │      │
│  │   ✓ Incremental project tasks                             │      │
│  │   ✗ Deep creative work                                    │      │
│  │   ✗ Precision-critical tasks                              │      │
│  │                                                           │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  [  Stressor Mitigation  ]    [  Adjust Schedule  ]    [  Ignore  ] │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Buffer Time Visualization

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Schedule with Buffers                               X  [_] [■]     │
│  ──────────────────────────────────────────────────────────────     │
│                                                                     │
│  Date: Wednesday, June 14, 2023                                     │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ Today's Schedule                                          │      │
│  │                                                           │      │
│  │  9:00 AM ┌────────────────────────────────┐              │      │
│  │          │ Team Standup Meeting           │              │      │
│  │  9:30 AM └────────────────────────────────┘              │      │
│  │          ┌────────────────────────────────┐ Transition   │      │
│  │          │ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒│ Buffer       │      │
│  │ 10:00 AM └────────────────────────────────┘ (15 min)     │      │
│  │          ┌────────────────────────────────┐              │      │
│  │          │ Quarterly Report Preparation   │              │      │
│  │          │                                │              │      │
│  │ 11:00 AM │                                │              │      │
│  │          │                                │              │      │
│  │          │                                │              │      │
│  │ 12:00 PM └────────────────────────────────┘              │      │
│  │          ┌────────────────────────────────┐              │      │
│  │          │ Lunch Break                    │              │      │
│  │  1:00 PM └────────────────────────────────┘              │      │
│  │          ┌────────────────────────────────┐ Recovery     │      │
│  │          │ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒│ Buffer       │      │
│  │  1:30 PM └────────────────────────────────┘ (30 min)     │      │
│  │          ┌────────────────────────────────┐              │      │
│  │          │ Client Call                    │              │      │
│  │  2:30 PM └────────────────────────────────┘              │      │
│  │          ┌────────────────────────────────┐ Context      │      │
│  │          │ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒│ Switch       │      │
│  │  2:45 PM └────────────────────────────────┘ (15 min)     │      │
│  │          ┌────────────────────────────────┐              │      │
│  │          │ Email Processing               │              │      │
│  │  3:45 PM └────────────────────────────────┘              │      │
│  │                                                           │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌───────────────────────────┐   ┌───────────────────────────┐      │
│  │ Buffer Summary            │   │ Estimated Focus Curve     │      │
│  │                           │   │                           │      │
│  │ Total buffer time: 60 min │   │  Focus            ╭╯╲     │      │
│  │                           │   │  Level   ╭─╯╲    ╱        │      │
│  │ Morning buffer: 15 min    │   │     ────╯    ╰──╯         │      │
│  │ Recovery buffer: 30 min   │   │          AM    Lunch   PM │      │
│  │ Context switch: 15 min    │   │                           │      │
│  │                           │   │                           │      │
│  └───────────────────────────┘   └───────────────────────────┘      │
│                                                                     │
│  [  Adjust Buffers  ]   [  Apply to Calendar  ]    [  Export  ]     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## User Interaction Flows

### Task Duration Estimation Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  Create/Edit  │────►│  Enter Task   │────►│  Run Auto     │
│  Task         │     │  Details      │     │  Analysis     │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│  Apply to     │◄────│  Review       │◄────│  View         │
│  Calendar     │     │  Estimate     │     │  Breakdown    │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

### Complexity Analysis Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  Select       │────►│  Submit Text  │────►│  Analyze      │
│  Task         │     │  Description  │     │  Complexity   │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│  Apply        │◄────│  View         │◄────│  Review       │
│  Recommendations    │  Subtasks     │     │  Analysis     │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

### Stressor Detection Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  Automatic    │────►│  Data         │────►│  Stressor     │
│  Monitoring   │     │  Collection   │     │  Analysis     │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│  Adjust       │◄────│  Review       │◄────│  Generate     │
│  Schedule     │     │  Impact       │     │  Report       │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

### Buffer Calculation Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  View         │────►│  Select       │────►│  Analyze      │
│  Calendar     │     │  Tasks        │     │  Transitions  │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
┌───────────────┐     ┌───────────────┐     ┌───────▼───────┐
│               │     │               │     │               │
│  Apply to     │◄────│  Review       │◄────│  Calculate    │
│  Calendar     │     │  Buffers      │     │  Buffers      │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

# Epic 2: Visual Reference Document - Part 4
# Developer Reference Guides

## Key API Usage Examples

### Task Duration Estimation

```typescript
// Example: Requesting a duration estimate for a task
async function estimateTaskDuration(
  taskDescription: string,
  taskCategory: string,
  userId: string
): Promise<DurationEstimate> {
  try {
    const response = await fetch(`${API_BASE_URL}/time-estimation/predict`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        task_description: taskDescription,
        task_category: taskCategory,
        include_factors: true,
        include_confidence: true
      })
    });

    if (!response.ok) {
      throw new Error(`Duration estimation request failed: ${response.status}`);
    }

    const data = await response.json();

    return {
      estimatedMinutes: data.estimated_duration_minutes,
      confidenceLevel: data.confidence_level,
      confidenceIntervalLower: data.confidence_interval_lower,
      confidenceIntervalUpper: data.confidence_interval_upper,
      adjustmentFactors: data.adjustment_factors.map(factor => ({
        factorName: factor.name,
        impact: factor.impact_minutes,
        confidence: factor.confidence
      })),
      similarTasksCount: data.similar_tasks_count
    };
  } catch (error) {
    console.error('Failed to estimate task duration:', error);
    return generateFallbackEstimate(taskCategory);
  }
}

// Helper function for fallback estimates
function generateFallbackEstimate(taskCategory: string): DurationEstimate {
  // Default estimates based on category
  const categoryDefaults = {
    'meeting': 60,
    'coding': 120,
    'documentation': 90,
    'planning': 45,
    'email': 30,
    // other categories
  };

  const baseEstimate = categoryDefaults[taskCategory] || 60;

  return {
    estimatedMinutes: baseEstimate,
    confidenceLevel: 0.5, // Low confidence for fallback
    confidenceIntervalLower: Math.floor(baseEstimate * 0.7),
    confidenceIntervalUpper: Math.ceil(baseEstimate * 1.5),
    adjustmentFactors: [],
    similarTasksCount: 0
  };
}
```

### Task Complexity Analysis

```typescript
// Example: Analyzing complexity of a task description
async function analyzeTaskComplexity(
  taskDescription: string,
  taskType: string
): Promise<ComplexityAnalysis> {
  try {
    const response = await fetch(`${API_BASE_URL}/complexity/analyze`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        task_description: taskDescription,
        task_type: taskType,
        include_subtasks: true,
        subtask_threshold: 0.7
      })
    });

    if (!response.ok) {
      throw new Error(`Complexity analysis request failed: ${response.status}`);
    }

    const data = await response.json();

    return {
      overallComplexity: data.complexity_score,
      cognitiveLoad: data.cognitive_load,
      ambiguityIndex: data.ambiguity_index,
      technicalTerms: data.technical_terms,
      collaborationNeeded: data.collaboration_needed,
      detectedSubtasks: data.subtasks.map(subtask => ({
        description: subtask.description,
        estimatedMinutes: subtask.estimated_minutes,
        complexity: subtask.complexity
      })),
      recommendations: data.recommendations
    };
  } catch (error) {
    console.error('Failed to analyze task complexity:', error);
    // Return simple complexity estimate based on text length and keyword heuristics
    return performBasicComplexityAnalysis(taskDescription, taskType);
  }
}

// Simple fallback complexity analyzer
function performBasicComplexityAnalysis(
  taskDescription: string,
  taskType: string
): ComplexityAnalysis {
  // Very basic implementation
  const length = taskDescription.length;
  const sentenceCount = taskDescription.split(/[.!?]+/).length - 1;
  const technicalTerms = extractCommonTechnicalTerms(taskDescription);

  // Simple complexity score based on length and sentence count
  const complexity = Math.min(
    100,
    Math.round((length / 500) * 60 + (sentenceCount / 10) * 20 + (technicalTerms.length * 5))
  );

  return {
    overallComplexity: complexity,
    cognitiveLoad: calculateBasicCognitiveLoad(taskDescription, taskType),
    ambiguityIndex: calculateBasicAmbiguity(taskDescription),
    technicalTerms: technicalTerms,
    collaborationNeeded: taskDescription.includes('team') || taskDescription.includes('collaborate'),
    detectedSubtasks: [],
    recommendations: generateBasicRecommendations(complexity, taskType)
  };
}
```

### Stressor Detection

```typescript
// Example: Retrieving current stressor information
async function getCurrentStressors(userId: string): Promise<StressorData> {
  try {
    const response = await fetch(`${API_BASE_URL}/stressors/current`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json'
      },
      params: {
        user_id: userId,
        include_impact: true,
        include_recommendations: true
      }
    });

    if (!response.ok) {
      throw new Error(`Stressor detection request failed: ${response.status}`);
    }

    const data = await response.json();

    return {
      overallStressorLevel: data.overall_level,
      stressorCategories: data.categories.map(category => ({
        name: category.name,
        level: category.level,
        factors: category.factors
      })),
      performanceImpact: {
        focusReduction: data.impact.focus_reduction_percent,
        durationIncrease: data.impact.duration_increase_percent,
        contextSwitchCost: data.impact.context_switch_cost_minutes
      },
      recommendations: data.recommendations
    };
  } catch (error) {
    console.error('Failed to retrieve stressor data:', error);
    return {
      overallStressorLevel: 30, // Default moderate-low
      stressorCategories: [],
      performanceImpact: {
        focusReduction: 10,
        durationIncrease: 15,
        contextSwitchCost: 5
      },
      recommendations: []
    };
  }
}
```

## Integration Code Examples

### Calendar Integration with Time Buffers

```typescript
// Example: Calendar integration with buffer times
class BufferedCalendarIntegration {
  private userId: string;
  private bufferService: TimeBufferService;
  private calendarService: CalendarService;

  constructor(userId: string, bufferService: TimeBufferService, calendarService: CalendarService) {
    this.userId = userId;
    this.bufferService = bufferService;
    this.calendarService = calendarService;
  }

  // Apply buffer times to an existing calendar
  async applyBuffersToCalendar(dateRange: DateRange): Promise<BufferApplicationResult> {
    try {
      // 1. Get all calendar events in the date range
      const events = await this.calendarService.getEventsInRange(this.userId, dateRange);

      // 2. Sort events chronologically
      const sortedEvents = this.sortEventsByStartTime(events);

      // 3. Calculate optimal buffers between events
      const bufferedSchedule = await this.calculateEventBuffers(sortedEvents);

      // 4. Apply the buffers to the calendar
      const result = await this.insertBufferEvents(bufferedSchedule);

      return {
        originalEventCount: events.length,
        buffersAdded: result.buffersAdded,
        schedulingConflicts: result.conflicts,
        totalBufferMinutes: result.totalBufferMinutes
      };
    } catch (error) {
      console.error('Failed to apply buffers to calendar:', error);
      throw new Error(`Buffer application failed: ${error.message}`);
    }
  }

  // Calculate optimal buffer times between events
  private async calculateEventBuffers(events: CalendarEvent[]): Promise<BufferedSchedule> {
    const bufferedEvents: BufferedEvent[] = [];

    // Skip if there are no or just one event
    if (events.length <= 1) {
      return { events: events.map(e => ({ event: e })) };
    }

    // For each adjacent pair of events, calculate buffer
    for (let i = 0; i < events.length - 1; i++) {
      const currentEvent = events[i];
      const nextEvent = events[i + 1];

      // Add current event to the schedule
      bufferedEvents.push({ event: currentEvent });

      // Skip buffer calculation if events are adjacent or overlapping
      if (nextEvent.startTime <= currentEvent.endTime) {
        continue;
      }

      // Calculate available time between events
      const availableMinutes = Math.floor(
        (nextEvent.startTime.getTime() - currentEvent.endTime.getTime()) / (60 * 1000)
      );

      // Skip if there's virtually no time between events
      if (availableMinutes < 5) {
        continue;
      }

      // Request buffer calculation from the buffer service
      const buffer = await this.bufferService.calculateBuffer({
        userId: this.userId,
        prevTaskId: currentEvent.taskId,
        nextTaskId: nextEvent.taskId,
        availableMinutes: availableMinutes,
        timeOfDay: currentEvent.endTime,
        currentStressors: await this.getCurrentStressors()
      });

      // Add buffer to the schedule if one was recommended
      if (buffer && buffer.recommendedBufferMinutes > 0) {
        bufferedEvents.push({
          buffer: {
            startTime: new Date(currentEvent.endTime.getTime()),
            endTime: new Date(currentEvent.endTime.getTime() + buffer.recommendedBufferMinutes * 60 * 1000),
            bufferType: buffer.bufferType,
            bufferMinutes: buffer.recommendedBufferMinutes
          }
        });
      }
    }

    // Add the last event
    bufferedEvents.push({ event: events[events.length - 1] });

    return { events: bufferedEvents };
  }

  // Insert buffer events into the calendar
  private async insertBufferEvents(schedule: BufferedSchedule): Promise<BufferInsertionResult> {
    let buffersAdded = 0;
    let conflicts = 0;
    let totalBufferMinutes = 0;

    for (const item of schedule.events) {
      // Skip if this is a regular event (not a buffer)
      if (!item.buffer) {
        continue;
      }

      try {
        // Create a buffer event in the calendar
        await this.calendarService.createEvent({
          userId: this.userId,
          title: this.getBufferTitle(item.buffer.bufferType),
          startTime: item.buffer.startTime,
          endTime: item.buffer.endTime,
          isBuffer: true,
          bufferType: item.buffer.bufferType,
          color: this.getBufferColor(item.buffer.bufferType),
          visibility: 'private'
        });

        buffersAdded++;
        totalBufferMinutes += item.buffer.bufferMinutes;
      } catch (error) {
        console.warn('Failed to insert buffer event:', error);
        conflicts++;
      }
    }

    return { buffersAdded, conflicts, totalBufferMinutes };
  }

  // Get appropriate title for different buffer types
  private getBufferTitle(bufferType: string): string {
    const titles = {
      'transition': 'Transition Buffer',
      'recovery': 'Recovery Time',
      'context_switch': 'Context Switch',
      'preparation': 'Preparation Time',
      'default': 'Buffer Time'
    };

    return titles[bufferType] || titles.default;
  }

  // Get appropriate color for different buffer types
  private getBufferColor(bufferType: string): string {
    const colors = {
      'transition': '#E0F7FA', // Light blue
      'recovery': '#E8F5E9',   // Light green
      'context_switch': '#FFF3E0', // Light orange
      'preparation': '#F3E5F5',  // Light purple
      'default': '#ECEFF1'     // Light gray
    };

    return colors[bufferType] || colors.default;
  }

  // Helper methods
  private sortEventsByStartTime(events: CalendarEvent[]): CalendarEvent[] {
    return [...events].sort((a, b) => a.startTime.getTime() - b.startTime.getTime());
  }

  private async getCurrentStressors(): Promise<StressorInfo[]> {
    try {
      const stressorData = await fetch(`${API_BASE_URL}/stressors/current?user_id=${this.userId}`);
      const data = await stressorData.json();
      return data.stressors || [];
    } catch (error) {
      console.warn('Failed to get current stressors:', error);
      return [];
    }
  }
}
```

### Complexity Visualization

```typescript
// Example: Visualizing task complexity with D3.js
function renderComplexityRadarChart(containerId: string, complexityData: ComplexityAnalysis) {
  const width = 500;
  const height = 500;
  const margin = 60;
  const radius = Math.min(width, height) / 2 - margin;

  // Radar chart configuration
  const config = {
    w: width,
    h: height,
    margin,
    maxValue: 10,
    levels: 5,
    roundStrokes: true,
    color: d3.scaleOrdinal().range(["#EDC951", "#CC333F", "#00A0B0", "#8C4E03", "#5DA5DA"])
  };

  // Format data for radar chart
  const data = [
    {
      name: 'Task Complexity',
      axes: [
        { axis: "Cognitive Load", value: complexityData.cognitiveLoad },
        { axis: "Ambiguity", value: complexityData.ambiguityIndex },
        { axis: "Technical Content", value: complexityData.technicalTermsScore ||
                 Math.min(10, complexityData.technicalTerms.length * 2) },
        { axis: "Collaboration", value: complexityData.collaborationNeeded ? 8 : 3 },
        { axis: "Decision Points", value: complexityData.decisionPointsScore ||
                calculateDecisionPoints(complexityData) }
      ]
    }
  ];

  // Create SVG
  const svg = d3.select(`#${containerId}`)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${width/2},${height/2})`);

  // Draw the circular grid
  const levels = config.levels;
  const axisGrid = svg.append("g").attr("class", "axisWrapper");

  for (let j = 0; j < levels; j++) {
    const levelFactor = radius * ((j + 1) / levels);
    axisGrid.selectAll(".levels")
      .data(data[0].axes)
      .enter()
      .append("svg:line")
      .attr("x1", (d, i) => levelFactor * Math.cos(angleSlice * i - Math.PI / 2))
      .attr("y1", (d, i) => levelFactor * Math.sin(angleSlice * i - Math.PI / 2))
      .attr("x2", (d, i) => levelFactor * Math.cos(angleSlice * (i + 1) - Math.PI / 2))
      .attr("y2", (d, i) => levelFactor * Math.sin(angleSlice * (i + 1) - Math.PI / 2))
      .attr("class", "line")
      .style("stroke", "grey")
      .style("stroke-opacity", "0.75")
      .style("stroke-width", "0.3px");
  }

  // Draw the axes
  const angleSlice = Math.PI * 2 / data[0].axes.length;
  const axis = axisGrid.selectAll(".axis")
    .data(data[0].axes)
    .enter()
    .append("g")
    .attr("class", "axis");

  axis.append("line")
    .attr("x1", 0)
    .attr("y1", 0)
    .attr("x2", (d, i) => radius * Math.cos(angleSlice * i - Math.PI / 2))
    .attr("y2", (d, i) => radius * Math.sin(angleSlice * i - Math.PI / 2))
    .attr("class", "line")
    .style("stroke", "grey")
    .style("stroke-width", "1px");

  // Draw axis labels
  axis.append("text")
    .attr("class", "legend")
    .style("font-size", "11px")
    .attr("text-anchor", "middle")
    .attr("dy", "0.35em")
    .attr("x", (d, i) => radius * 1.1 * Math.cos(angleSlice * i - Math.PI / 2))
    .attr("y", (d, i) => radius * 1.1 * Math.sin(angleSlice * i - Math.PI / 2))
    .text(d => d.axis);

  // Draw the radar chart blobs
  const radarLine = d3.lineRadial()
    .radius(d => radius * (d.value / config.maxValue))
    .angle((d, i) => i * angleSlice);

  // Create the radar path and fill it
  const blobWrapper = svg.selectAll(".radarWrapper")
    .data(data)
    .enter()
    .append("g")
    .attr("class", "radarWrapper");

  blobWrapper.append("path")
    .attr("class", "radarArea")
    .attr("d", d => radarLine(d.axes))
    .style("fill", (d, i) => config.color(i))
    .style("fill-opacity", 0.35);

  // Add circles at each data point
  blobWrapper.selectAll(".radarCircle")
    .data(d => d.axes)
    .enter()
    .append("circle")
    .attr("class", "radarCircle")
    .attr("r", 4)
    .attr("cx", (d, i) => radius * (d.value / config.maxValue) * Math.cos(angleSlice * i - Math.PI / 2))
    .attr("cy", (d, i) => radius * (d.value / config.maxValue) * Math.sin(angleSlice * i - Math.PI / 2))
    .style("fill", "#ED174F")
    .style("fill-opacity", 0.9);

  // Add title in the center
  svg.append("text")
    .attr("x", 0)
    .attr("y", 0 - radius - 20)
    .attr("text-anchor", "middle")
    .style("font-weight", "bold")
    .text(`Complexity Score: ${complexityData.overallComplexity}/100`);

  // Helper function to calculate decision points
  function calculateDecisionPoints(complexity) {
    // Simple calculation based on ambiguity and cognitive load
    return Math.min(10, (complexity.ambiguityIndex + complexity.cognitiveLoad) / 2);
  }
}
```

### Stressor Integration

```typescript
// Example: Integrating stressor detection with a productivity dashboard
class StressorAwareProductivityDashboard {
  private userId: string;
  private stressorService: StressorDetectionService;
  private dashboardElement: HTMLElement;
  private updateInterval: number = 15 * 60 * 1000; // 15 minutes
  private intervalId: number;

  constructor(dashboardElement: HTMLElement, userId: string, stressorService: StressorDetectionService) {
    this.dashboardElement = dashboardElement;
    this.userId = userId;
    this.stressorService = stressorService;
  }

  // Initialize the dashboard with stressor awareness
  public initialize(): void {
    // Perform initial update
    this.updateDashboard();

    // Set up periodic updates
    this.intervalId = window.setInterval(() => this.updateDashboard(), this.updateInterval);

    // Add event listeners for real-time updates
    this.stressorService.on('stressor-change', () => this.updateDashboard());
    window.addEventListener('focus', () => this.updateDashboard());
  }

  // Clean up resources
  public dispose(): void {
    window.clearInterval(this.intervalId);
    this.stressorService.off('stressor-change');
    window.removeEventListener('focus', () => this.updateDashboard());
  }

  // Update the dashboard with current stressor information
  private async updateDashboard(): Promise<void> {
    try {
      // Get current stressor data
      const stressorData = await this.stressorService.getCurrentStressors(this.userId);

      // Update visual indicators
      this.updateStressorIndicators(stressorData);

      // Adjust task recommendations
      this.updateTaskRecommendations(stressorData);

      // Update productivity forecast
      this.updateProductivityForecast(stressorData);

      // Show interventions if necessary
      if (stressorData.overallStressorLevel > 70) {
        this.showStressInterventions(stressorData);
      }
    } catch (error) {
      console.error('Failed to update stressor-aware dashboard:', error);
      // Show offline indicator or fallback content
      this.showOfflineState();
    }
  }

  // Update visual stressor indicators
  private updateStressorIndicators(stressorData: StressorData): void {
    const indicatorElement = this.dashboardElement.querySelector('.stressor-indicator');
    if (!indicatorElement) return;

    // Clear existing indicators
    indicatorElement.innerHTML = '';

    // Overall stressor level indicator
    const overallLevel = document.createElement('div');
    overallLevel.className = 'overall-stressor-level';
    overallLevel.innerHTML = `
      <div class="level-label">Current Stressor Level</div>
      <div class="level-value ${this.getStressorLevelClass(stressorData.overallStressorLevel)}">
        ${stressorData.overallStressorLevel}/100
      </div>
      <div class="level-bar">
        <div class="level-fill" style="width: ${stressorData.overallStressorLevel}%"></div>
      </div>
    `;
    indicatorElement.appendChild(overallLevel);

    // Individual stressor category indicators
    const categoriesContainer = document.createElement('div');
    categoriesContainer.className = 'stressor-categories';

    stressorData.stressorCategories.forEach(category => {
      const categoryElement = document.createElement('div');
      categoryElement.className = 'stressor-category';
      categoryElement.innerHTML = `
        <div class="category-name">${category.name}</div>
        <div class="category-level ${this.getStressorLevelClass(category.level)}">
          ${category.level}/100
        </div>
      `;
      categoriesContainer.appendChild(categoryElement);
    });

    indicatorElement.appendChild(categoriesContainer);
  }

  // Other dashboard methods
  private updateTaskRecommendations(stressorData: StressorData): void {
    // Implementation details...
  }

  private updateProductivityForecast(stressorData: StressorData): void {
    // Implementation details...
  }

  private showStressInterventions(stressorData: StressorData): void {
    // Implementation details...
  }

  private showOfflineState(): void {
    // Implementation details...
  }

  // Helper methods
  private getStressorLevelClass(level: number): string {
    if (level < 30) return 'level-low';
    if (level < 60) return 'level-medium';
    if (level < 80) return 'level-high';
    return 'level-extreme';
  }
}
```

## Error Handling Patterns

### Graceful Degradation for Time Estimation

```typescript
// Example: Multi-level reliability for duration estimation
class ReliableDurationEstimator {
  private apiClient: ApiClient;
  private localStorage: LocalStorage;
  private modelCache: ModelCache;
  private telemetry: TelemetryService;

  constructor(
    apiClient: ApiClient,
    localStorage: LocalStorage,
    modelCache: ModelCache,
    telemetry: TelemetryService
  ) {
    this.apiClient = apiClient;
    this.localStorage = localStorage;
    this.modelCache = modelCache;
    this.telemetry = telemetry;
  }

  // Robust estimation with fallbacks
  async estimateTaskDuration(
    taskDescription: string,
    taskCategory: string,
    userId: string
  ): Promise<DurationEstimate> {
    let estimate: DurationEstimate | null = null;
    let source = '';
    let confidenceAdjustment = 0;

    try {
      // Step 1: Try to get from local cache first (fastest)
      const cacheKey = this.generateCacheKey(taskDescription, taskCategory, userId);
      estimate = await this.modelCache.get(cacheKey);

      if (estimate) {
        source = 'cache';
        this.telemetry.trackEvent('duration_estimate_source', { source });
        return estimate;
      }

      // Step 2: Try to get from API (most accurate)
      try {
        estimate = await this.apiClient.post('/time-estimation/predict', {
          user_id: userId,
          task_description: taskDescription,
          task_category: taskCategory,
          include_factors: true
        });

        // Cache successful result
        if (estimate) {
          await this.modelCache.set(cacheKey, estimate, { ttl: 3600 });
          source = 'api';
          this.telemetry.trackEvent('duration_estimate_source', { source });
          return estimate;
        }
      } catch (apiError) {
        // Log API error but continue to fallbacks
        this.telemetry.trackException('api_duration_estimation_failed', {
          error: apiError.message,
          taskCategory
        });

        // Adjust confidence for next fallbacks
        confidenceAdjustment -= 0.2;
      }

      // Step 3: Try to use locally cached model
      try {
        const localModel = await this.modelCache.getModel('duration_estimation');
        if (localModel) {
          estimate = await this.runLocalModel(localModel, taskDescription, taskCategory);
          source = 'local_model';

          // Adjust confidence downward
          if (estimate) {
            estimate.confidenceLevel = Math.max(0.1, estimate.confidenceLevel - 0.3);
            this.telemetry.trackEvent('duration_estimate_source', { source });
            return estimate;
          }
        }
      } catch (localModelError) {
        this.telemetry.trackException('local_model_estimation_failed', {
          error: localModelError.message,
          taskCategory
        });

        // Further adjust confidence for next fallback
        confidenceAdjustment -= 0.1;
      }

      // Step 4: Use local storage historical data
      try {
        const historicalData = await this.localStorage.getTasksByCategory(taskCategory, userId);
        if (historicalData && historicalData.length > 0) {
          estimate = this.calculateFromHistoricalData(historicalData, taskDescription);
          source = 'historical_data';

          // Adjust confidence based on data quality
          if (estimate) {
            estimate.confidenceLevel = Math.max(0.1,
              Math.min(0.6, 0.3 + (historicalData.length / 20)) + confidenceAdjustment);
            this.telemetry.trackEvent('duration_estimate_source', { source });
            return estimate;
          }
        }
      } catch (storageError) {
        this.telemetry.trackException('local_storage_access_failed', {
          error: storageError.message,
          taskCategory
        });
      }

      // Step 5: Final fallback to category defaults
      estimate = this.getCategoryDefaults(taskCategory);
      source = 'defaults';
      estimate.confidenceLevel = 0.3 + confidenceAdjustment;
      this.telemetry.trackEvent('duration_estimate_source', { source });
      return estimate;

    } catch (error) {
      // Catch-all for unexpected errors
      this.telemetry.trackException('duration_estimation_failed', {
        error: error.message,
        taskCategory
      });

      // Emergency fallback
      return {
        estimatedMinutes: 60, // 1 hour default
        confidenceLevel: 0.1, // Very low confidence
        confidenceIntervalLower: 30,
        confidenceIntervalUpper: 120,
        adjustmentFactors: [],
        similarTasksCount: 0,
        source: 'emergency_fallback'
      };
    }
  }

  // Helper methods
  private generateCacheKey(taskDescription: string, taskCategory: string, userId: string): string {
    // Implementation details...
    return `duration:${userId}:${taskCategory}:${this.hashString(taskDescription)}`;
  }

  private async runLocalModel(model: any, taskDescription: string, taskCategory: string): Promise<DurationEstimate> {
    // Implementation details...
    return null;
  }

  private calculateFromHistoricalData(historicalData: any[], taskDescription: string): DurationEstimate {
    // Implementation details...
    return null;
  }

  private getCategoryDefaults(taskCategory: string): DurationEstimate {
    const categoryDefaults = {
      'meeting': 60,
      'coding': 120,
      'writing': 90,
      'email': 30,
      'planning': 45,
      'design': 120,
      'research': 90,
      'default': 60
    };

    const baseEstimate = categoryDefaults[taskCategory] || categoryDefaults.default;

    return {
      estimatedMinutes: baseEstimate,
      confidenceLevel: 0.3,
      confidenceIntervalLower: Math.floor(baseEstimate * 0.6),
      confidenceIntervalUpper: Math.ceil(baseEstimate * 1.6),
      adjustmentFactors: [],
      similarTasksCount: 0,
      source: 'category_defaults'
    };
  }

  private hashString(str: string): string {
    // Implementation details...
    return str.length.toString();
  }
}
```

### Centralized Error Handler

```typescript
// Example: Centralized error handling for stochastic time estimation components
class TimeEstimationErrorHandler {
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

  // Handle errors from various components consistently
  handleError(error: any, context: ErrorContext): ErrorResult {
    // Log the error with context
    this.telemetry.logError({
      message: error.message,
      code: error.code || 'unknown',
      component: context.component,
      operation: context.operation,
      userId: context.userId,
      taskId: context.taskId,
      timestamp: new Date().toISOString()
    });

    // Determine error type and appropriate response
    if (this.isNetworkError(error)) {
      return this.handleNetworkError(error, context);
    } else if (this.isAuthError(error)) {
      return this.handleAuthError(error, context);
    } else if (this.isValidationError(error)) {
      return this.handleValidationError(error, context);
    } else if (this.isServiceError(error)) {
      return this.handleServiceError(error, context);
    } else {
      return this.handleUnknownError(error, context);
    }
  }

  // Handle network connectivity errors
  private handleNetworkError(error: any, context: ErrorContext): ErrorResult {
    // Check if we should retry
    if (this.retryPolicy.shouldRetry(context.operation, context.attempts)) {
      const nextRetryDelay = this.retryPolicy.getNextRetryDelay(context.operation, context.attempts);

      return {
        type: 'retry',
        message: 'Connection issue. Retrying...',
        retryDelay: nextRetryDelay,
        userVisible: context.attempts > 1
      };
    }

    // If retries exhausted, suggest offline mode
    return {
      type: 'connectivity',
      message: 'Unable to connect to estimation service. Using offline mode.',
      fallbackStrategy: 'local_model',
      userVisible: true
    };
  }

  // Handle authentication/authorization errors
  private handleAuthError(error: any, context: ErrorContext): ErrorResult {
    return {
      type: 'auth_error',
      message: 'Session expired or invalid. Please log in again.',
      action: 'redirect_login',
      userVisible: true
    };
  }

  // Handle validation errors
  private handleValidationError(error: any, context: ErrorContext): ErrorResult {
    // Extract field-specific errors if available
    const fieldErrors = error.details?.fieldErrors || {};

    // Show field-specific error messages
    if (Object.keys(fieldErrors).length > 0) {
      return {
        type: 'validation',
        message: 'Please correct the following issues:',
        fieldErrors: fieldErrors,
        userVisible: true
      };
    }

    // Generic validation error
    return {
      type: 'validation',
      message: 'Invalid input. Please check your task description and try again.',
      userVisible: true
    };
  }

  // Handle service errors (backend issues)
  private handleServiceError(error: any, context: ErrorContext): ErrorResult {
    // Notify operations team for critical service errors
    if (error.code === 'critical_service_failure') {
      this.notifyOperationsTeam(error, context);
    }

    return {
      type: 'service_error',
      message: 'Estimation service is currently unavailable. Using best available estimates.',
      fallbackStrategy: 'historical_data',
      userVisible: true
    };
  }

  // Handle unknown/unexpected errors
  private handleUnknownError(error: any, context: ErrorContext): ErrorResult {
    // Always notify about unknown errors
    this.notifyOperationsTeam(error, context);

    return {
      type: 'unknown_error',
      message: 'Something went wrong. Using simplified estimation.',
      fallbackStrategy: 'category_defaults',
      userVisible: true
    };
  }

  // Helper methods for error detection
  private isNetworkError(error: any): boolean {
    return error.name === 'NetworkError' ||
           error.code === 'network_error' ||
           error.message.includes('network') ||
           error.message.includes('connection');
  }

  private isAuthError(error: any): boolean {
    return error.status === 401 ||
           error.status === 403 ||
           error.code === 'unauthorized' ||
           error.code === 'forbidden';
  }

  private isValidationError(error: any): boolean {
    return error.status === 400 ||
           error.code === 'validation_error' ||
           error.hasOwnProperty('details');
  }

  private isServiceError(error: any): boolean {
    return error.status === 500 ||
           error.status === 503 ||
           error.code === 'service_unavailable';
  }

  private notifyOperationsTeam(error: any, context: ErrorContext): void {
    // Implementation details...
  }
}
```

## Testing Code Examples

### Unit Testing for Duration Estimation

```typescript
// Example: Unit tests for the Bayesian Duration Predictor
describe('BayesianDurationPredictor', () => {
  let predictor: BayesianDurationPredictor;
  let mockDataService: any;
  let mockModelService: any;

  beforeEach(() => {
    // Mock dependencies
    mockDataService = {
      getHistoricalTasks: jest.fn().mockResolvedValue([
        {
          id: 'task-1',
          description: 'Write unit tests for authentication module',
          category: 'coding',
          estimatedDuration: 120,
          actualDuration: 150,
          complexity: 7
        },
        {
          id: 'task-2',
          description: 'Update API documentation',
          category: 'documentation',
          estimatedDuration: 90,
          actualDuration: 75,
          complexity: 4
        }
      ])
    };

    mockModelService = {
      getPriors: jest.fn().mockResolvedValue({
        coding: { mean: 120, variance: 900 },
        documentation: { mean: 90, variance: 400 },
        meeting: { mean: 60, variance: 225 }
      }),
      updateModel: jest.fn().mockResolvedValue(true)
    };

    // Create predictor with mocked dependencies
    predictor = new BayesianDurationPredictor(mockDataService, mockModelService);
  });

  describe('predictDuration', () => {
    it('should return a duration estimate with confidence intervals', async () => {
      // Arrange
      const taskDescription = 'Write unit tests for authentication module';
      const taskCategory = 'coding';
      const userId = 'user-123';

      // Act
      const result = await predictor.predictDuration(taskDescription, taskCategory, userId);

      // Assert
      expect(result).toBeDefined();
      expect(result.estimatedMinutes).toBeGreaterThan(0);
      expect(result.confidenceIntervalLower).toBeLessThan(result.estimatedMinutes);
      expect(result.confidenceIntervalUpper).toBeGreaterThan(result.estimatedMinutes);
      expect(result.confidenceLevel).toBeGreaterThan(0);
      expect(result.confidenceLevel).toBeLessThanOrEqual(1);
      expect(mockDataService.getHistoricalTasks).toHaveBeenCalledWith(userId, {
        categories: [taskCategory],
        limit: 50
      });
    });

    it('should adjust estimate based on complexity', async () => {
      // Arrange
      const taskDescription = 'Write complex authentication system with 2FA and biometrics';
      const taskCategory = 'coding';
      const userId = 'user-123';

      // Mock complexity analyzer
      predictor.getTaskComplexity = jest.fn().mockResolvedValue({
        overallComplexity: 85, // High complexity
        cognitiveLoad: 8,
        ambiguityIndex: 3
      });

      // Act
      const result = await predictor.predictDuration(taskDescription, taskCategory, userId);
      const baseResult = await predictor.predictDuration('Write simple authentication system', taskCategory, userId);

      // Assert
      expect(result.estimatedMinutes).toBeGreaterThan(baseResult.estimatedMinutes);
      expect(result.adjustmentFactors).toContainEqual(
        expect.objectContaining({
          factorName: 'complexity',
          impact: expect.any(Number),
          confidence: expect.any(Number)
        })
      );
    });

    it('should handle cases with no historical data', async () => {
      // Arrange
      mockDataService.getHistoricalTasks.mockResolvedValue([]);
      const taskDescription = 'New task type with no history';
      const taskCategory = 'unknown';
      const userId = 'user-123';

      // Act
      const result = await predictor.predictDuration(taskDescription, taskCategory, userId);

      // Assert
      expect(result).toBeDefined();
      expect(result.estimatedMinutes).toBeGreaterThan(0);
      expect(result.confidenceLevel).toBeLessThan(0.5); // Low confidence due to no data
      expect(result.source).toBe('category_priors');
    });
  });

  describe('recordActualDuration', () => {
    it('should update model with actual completion data', async () => {
      // Arrange
      const taskId = 'task-123';
      const estimatedMinutes = 120;
      const actualMinutes = 150;
      const userId = 'user-123';
      const category = 'coding';

      // Act
      await predictor.recordActualDuration(taskId, estimatedMinutes, actualMinutes, category, userId);

      // Assert
      expect(mockModelService.updateModel).toHaveBeenCalledWith(
        expect.objectContaining({
          taskId,
          estimatedDuration: estimatedMinutes,
          actualDuration: actualMinutes,
          category,
          userId
        })
      );
    });

    it('should handle extremely short or long durations', async () => {
      // Arrange
      const taskId = 'task-123';
      const estimatedMinutes = 120;
      const actualMinutes = 600; // 10 hours, unusually long
      const userId = 'user-123';
      const category = 'coding';

      // Spy on outlier detection method
      jest.spyOn(predictor as any, 'isOutlier').mockReturnValue(true);

      // Act
      await predictor.recordActualDuration(taskId, estimatedMinutes, actualMinutes, category, userId);

      // Assert
      expect(mockModelService.updateModel).toHaveBeenCalledWith(
        expect.objectContaining({
          taskId,
          estimatedDuration: estimatedMinutes,
          actualDuration: actualMinutes,
          category,
          userId,
          isOutlier: true,
          outlierReason: 'duration_anomaly'
        })
      );
    });
  });
});
```

### Integration Testing for Buffer Calculation

```typescript
// Example: Integration tests for the Time Buffer Calculator
describe('TimeBufferCalculator Integration', () => {
  // Use test database or repositories
  let bufferCalculator: TimeBufferCalculator;
  let mockTaskRepository: TaskRepository;
  let mockUserProfileRepository: UserProfileRepository;
  let mockStressorService: StressorDetectionService;

  beforeAll(async () => {
    // Set up test database
    const testDb = new TestDatabase();
    await testDb.connect();

    // Seed with test data
    await testDb.seed('./test/fixtures/buffer_calculator_test_data.json');

    // Initialize repositories with test database
    mockTaskRepository = new TaskRepository(testDb);
    mockUserProfileRepository = new UserProfileRepository(testDb);

    // Mock stressor service
    mockStressorService = {
      getCurrentStressors: jest.fn().mockResolvedValue({
        overallStressorLevel: 40, // Moderate level
        stressorCategories: [
          { name: 'Environmental', level: 30 },
          { name: 'Physiological', level: 50 },
          { name: 'Deadline', level: 40 }
        ]
      })
    };

    // Create calculator with real repositories and mocked services
    bufferCalculator = new TimeBufferCalculator(
      mockTaskRepository,
      mockUserProfileRepository,
      mockStressorService
    );
  });

  afterAll(async () => {
    // Clean up test database
    await testDb.disconnect();
  });

  it('should calculate appropriate buffers between different task types', async () => {
    // Arrange
    const userId = 'test-user-1';
    const prevTaskId = 'task-meeting-1';
    const nextTaskId = 'task-coding-1';

    // Act
    const buffer = await bufferCalculator.calculateBuffer({
      userId,
      prevTaskId,
      nextTaskId,
      availableMinutes: 60,
      timeOfDay: new Date('2023-06-15T14:00:00') // 2 PM
    });

    // Assert
    expect(buffer).toBeDefined();
    expect(buffer.recommendedBufferMinutes).toBeGreaterThan(0);
    expect(buffer.bufferComponents).toContainEqual(
      expect.objectContaining({
        componentType: 'context_switch',
        minutes: expect.any(Number)
      })
    );
    expect(buffer.bufferComponents).toContainEqual(
      expect.objectContaining({
        componentType: 'preparation',
        minutes: expect.any(Number)
      })
    );
  });

  it('should adjust buffers based on current stressors', async () => {
    // Arrange
    const userId = 'test-user-1';
    const prevTaskId = 'task-meeting-1';
    const nextTaskId = 'task-coding-1';

    // First test with moderate stressors (default)
    const moderateBuffer = await bufferCalculator.calculateBuffer({
      userId,
      prevTaskId,
      nextTaskId,
      availableMinutes: 60,
      timeOfDay: new Date('2023-06-15T14:00:00')
    });

    // Then test with high stressors
    mockStressorService.getCurrentStressors.mockResolvedValue({
      overallStressorLevel: 75, // High level
      stressorCategories: [
        { name: 'Environmental', level: 80 },
        { name: 'Physiological', level: 70 },
        { name: 'Deadline', level: 75 }
      ]
    });

    const highStressBuffer = await bufferCalculator.calculateBuffer({
      userId,
      prevTaskId,
      nextTaskId,
      availableMinutes: 60,
      timeOfDay: new Date('2023-06-15T14:00:00')
    });

    // Assert
    expect(highStressBuffer.recommendedBufferMinutes).toBeGreaterThan(
      moderateBuffer.recommendedBufferMinutes
    );
    expect(highStressBuffer.bufferComponents).toContainEqual(
      expect.objectContaining({
        componentType: 'recovery',
        minutes: expect.any(Number)
      })
    );
  });

  it('should respect maximum available time', async () => {
    // Arrange
    const userId = 'test-user-1';
    const prevTaskId = 'task-meeting-1';
    const nextTaskId = 'task-coding-1';
    const limitedAvailableTime = 10; // Only 10 minutes available

    // Act
    const buffer = await bufferCalculator.calculateBuffer({
      userId,
      prevTaskId,
      nextTaskId,
      availableMinutes: limitedAvailableTime,
      timeOfDay: new Date('2023-06-15T14:00:00')
    });

    // Assert
    expect(buffer.recommendedBufferMinutes).toBeLessThanOrEqual(limitedAvailableTime);
    expect(buffer.bufferComponents.reduce((sum, component) => sum + component.minutes, 0))
      .toBeLessThanOrEqual(limitedAvailableTime);
    expect(buffer.isConstrainedByAvailableTime).toBe(true);
  });

  it('should learn from user feedback', async () => {
    // Arrange
    const userId = 'test-user-1';
    const prevTaskId = 'task-meeting-1';
    const nextTaskId = 'task-coding-1';

    // Get initial buffer recommendation
    const initialBuffer = await bufferCalculator.calculateBuffer({
      userId,
      prevTaskId,
      nextTaskId,
      availableMinutes: 60,
      timeOfDay: new Date('2023-06-15T14:00:00')
    });

    // Submit feedback that buffer was too short
    await bufferCalculator.recordBufferFeedback({
      userId,
      bufferId: initialBuffer.id,
      feedbackType: 'too_short',
      actualRequiredMinutes: initialBuffer.recommendedBufferMinutes + 10
    });

    // Act - get new buffer recommendation for similar situation
    const updatedBuffer = await bufferCalculator.calculateBuffer({
      userId,
      prevTaskId: 'task-meeting-2', // Different but similar task
      nextTaskId: 'task-coding-2',  // Different but similar task
      availableMinutes: 60,
      timeOfDay: new Date('2023-06-15T14:00:00')
    });

    // Assert - buffer should be longer after feedback
    expect(updatedBuffer.recommendedBufferMinutes).toBeGreaterThan(
      initialBuffer.recommendedBufferMinutes
    );
  });
});
```
