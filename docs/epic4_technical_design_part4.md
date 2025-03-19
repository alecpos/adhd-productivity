# Epic 4: Technical Design Document - Part 4
# Dynamic Schedule Rebalancing with Circadian Rhythm Optimization

## Deployment Architecture

### Service Deployment

The Dynamic Schedule Rebalancing system is deployed using containerized microservices with Kubernetes orchestration:

1. **API Gateway Service**: Route requests and handle authentication
2. **Scheduling Service**: Core scheduling logic and optimization
3. **Circadian Model Service**: Energy predictions and model management
4. **Task Profiling Service**: Task analysis and cognitive profiling
5. **Model Training Service**: Asynchronous model training and updates

```yaml
# API Gateway Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  labels:
    app: adhd-calendar
    component: api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: adhd-calendar
      component: api-gateway
  template:
    metadata:
      labels:
        app: adhd-calendar
        component: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: adhd-calendar/api-gateway:v2.3.1
        ports:
        - containerPort: 8080
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
          requests:
            cpu: "0.5"
            memory: "512Mi"
        env:
        - name: SERVICE_DISCOVERY_URL
          value: "http://service-registry:8761/eureka/"
        - name: AUTH_SERVICE_URL
          value: "http://auth-service:8090/auth"
        - name: LOG_LEVEL
          value: "INFO"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Scaling Strategy

The system employs a multi-tiered scaling strategy:

1. **Horizontal Pod Autoscaling**: Based on CPU and memory utilization
2. **Custom Metrics Scaling**: Based on request queue length and processing time
3. **Predictive Scaling**: Based on usage patterns (e.g., increased morning activity)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: scheduling-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: scheduling-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: scheduling_queue_length
      target:
        type: AverageValue
        averageValue: 10
  - type: Object
    object:
      metric:
        name: optimization_request_duration_seconds
      describedObject:
        apiVersion: v1
        kind: Service
        name: scheduling-service
      target:
        type: Value
        value: 5
```

### Database Deployment

The database architecture ensures high availability and performance:

1. **PostgreSQL**: Deployed as a StatefulSet with replicas
2. **MongoDB**: Deployed as a replica set with sharding
3. **Redis**: Deployed as a cluster with sentinel for high availability

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: "postgres"
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secrets
              key: password
        - name: POSTGRES_USER
          value: "adhd_app"
        - name: POSTGRES_DB
          value: "adhd_calendar"
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "standard"
      resources:
        requests:
          storage: 100Gi
```

## Testing Strategy

### Unit Testing

Unit tests cover key algorithmic components:

1. **Energy Pattern Detection**: Test pattern detection algorithms
2. **Task Cognitive Profiling**: Test task analysis and categorization
3. **Schedule Optimization**: Test optimization algorithms
4. **Reward Functions**: Test reward calculation for different scenarios

```typescript
describe('CircadianRhythmModel', () => {
  let model;
  
  beforeEach(() => {
    model = new CircadianRhythmModel(TEST_USER_ID);
    jest.spyOn(model, '_load_base_parameters').mockReturnValue(TEST_BASE_PARAMS);
    jest.spyOn(model, '_load_user_parameters').mockReturnValue(TEST_USER_PARAMS);
  });
  
  describe('predict_energy_levels', () => {
    it('should predict energy levels correctly for morning time', () => {
      const morning = new Date('2023-09-01T09:00:00Z');
      const predictions = model.predict_energy_levels(morning);
      
      expect(predictions.energy_level).toBeCloseTo(7.2, 1);
      expect(predictions.focus_capacity).toBeCloseTo(8.1, 1);
      expect(predictions.creative_capacity).toBeCloseTo(6.5, 1);
      expect(predictions.executive_function_capacity).toBeCloseTo(7.8, 1);
    });
    
    it('should predict energy levels correctly for afternoon slump', () => {
      const afternoon = new Date('2023-09-01T14:30:00Z');
      const predictions = model.predict_energy_levels(afternoon);
      
      expect(predictions.energy_level).toBeCloseTo(5.1, 1);
      expect(predictions.focus_capacity).toBeCloseTo(4.2, 1);
      expect(predictions.creative_capacity).toBeCloseTo(6.8, 1);
      expect(predictions.executive_function_capacity).toBeCloseTo(4.5, 1);
    });
  });
  
  describe('detect_optimal_windows', () => {
    it('should identify optimal focus windows correctly', () => {
      const date = new Date('2023-09-01');
      const windows = model.detect_optimal_windows(date, 'focus_capacity', 0.7);
      
      expect(windows).toHaveLength(2);
      expect(windows[0].start.getHours()).toBe(9);
      expect(windows[0].end.getHours()).toBe(12);
      expect(windows[1].start.getHours()).toBe(16);
      expect(windows[1].end.getHours()).toBe(18);
    });
  });
});
```

### Integration Testing

Integration tests verify service interactions:

1. **API Gateway-to-Service**: Test request routing and authentication
2. **Service-to-Service**: Test inter-service communication
3. **Service-to-Database**: Test data persistence and retrieval
4. **External API Integration**: Test calendar and productivity integrations

```typescript
describe('Schedule Optimization Integration', () => {
  let schedulingService;
  let circadianService;
  let taskService;
  
  beforeEach(async () => {
    // Set up services with test data
    schedulingService = new SchedulingService();
    circadianService = new CircadianModelService();
    taskService = new TaskProfileService();
    
    // Initialize test database
    await setupTestDatabase();
    
    // Mock external dependencies
    jest.spyOn(circadianService, 'predictUserEnergy').mockImplementation(mockPredictUserEnergy);
    jest.spyOn(taskService, 'analyzeTaskCognitiveProfile').mockImplementation(mockAnalyzeTaskProfile);
  });
  
  afterEach(async () => {
    await cleanupTestDatabase();
  });
  
  it('should optimize a schedule using circadian patterns', async () => {
    const userId = 'test-user-123';
    const request = createTestOptimizationRequest();
    
    const result = await schedulingService.optimizeSchedule(userId, request);
    
    expect(result.schedule).toHaveLength(request.tasks.length);
    expect(result.quality_metrics.overall_score).toBeGreaterThan(0.7);
    
    // Check that high-focus tasks are scheduled during peak focus periods
    const highFocusTasks = request.tasks.filter(t => t.focus_required >= 7);
    const highFocusScheduled = result.schedule.filter(s => 
      highFocusTasks.some(t => t.id === s.task_id)
    );
    
    for (const item of highFocusScheduled) {
      const startHour = new Date(item.start_time).getHours();
      expect(startHour).toBeWithin([9, 10, 11, 16, 17]);
    }
  });
});
```

### Load Testing

Load tests validate system performance under stress:

1. **Concurrent User Testing**: Test system with simulated concurrent users
2. **Peak Load Testing**: Test performance during high-demand periods
3. **Endurance Testing**: Test system stability over extended periods
4. **Stress Testing**: Test system behavior beyond expected capacity

```javascript
// k6 load test script
import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  stages: [
    { duration: '5m', target: 100 }, // Ramp up to 100 users over 5 minutes
    { duration: '10m', target: 100 }, // Stay at 100 users for 10 minutes
    { duration: '5m', target: 500 }, // Ramp up to 500 users over 5 minutes
    { duration: '20m', target: 500 }, // Stay at 500 users for 20 minutes
    { duration: '5m', target: 0 }, // Ramp down to 0 users over 5 minutes
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.01'], // Less than 1% of requests should fail
  },
};

export default function() {
  const BASE_URL = 'https://api-test.adhd-calendar.com/v1';
  const AUTH_TOKEN = `Bearer ${__ENV.AUTH_TOKEN}`;
  
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': AUTH_TOKEN,
    },
  };
  
  // Generate a random date range for the next week
  const startDate = new Date();
  const endDate = new Date();
  endDate.setDate(endDate.getDate() + 7);
  
  // Create optimization request
  const optimizationRequest = {
    start_date: startDate.toISOString(),
    end_date: endDate.toISOString(),
    tasks: generateRandomTasks(10),
    preferences: {
      optimization_strength: 0.8,
      respect_existing_events: true,
    }
  };
  
  // Request optimization
  let response = http.post(
    `${BASE_URL}/scheduling/circadian-optimize`,
    JSON.stringify(optimizationRequest),
    params
  );
  
  check(response, {
    'optimization request successful': (r) => r.status === 200,
    'optimization response contains schedule': (r) => {
      const body = JSON.parse(r.body);
      return body.schedule && body.schedule.length > 0;
    },
    'response time under 2s': (r) => r.timings.duration < 2000,
  });
  
  // Wait between requests
  sleep(Math.random() * 5 + 5);
}
```

### User Acceptance Testing

UAT validates system functionality from a user perspective:

1. **Scenario-Based Testing**: Test complete user workflows
2. **A/B Testing**: Compare algorithm variants with real users
3. **Feedback Collection**: Gather user feedback on optimization quality
4. **Longitudinal Testing**: Track completion rates and satisfaction over time

## Rollout Plan

### Feature Flagging

The system uses feature flags for controlled rollout:

1. **Circadian Optimization**: Enable/disable circadian-based optimization
2. **Advanced Task Profiling**: Enable/disable NLP-based task analysis
3. **Energy Reporting**: Enable/disable energy level reporting
4. **Sleep Integration**: Enable/disable sleep data integration

```typescript
const featureFlags = {
  CIRCADIAN_OPTIMIZATION: {
    enabled: true,
    rolloutPercentage: 50, // Percentage of users who get this feature
    enabledFor: ['beta_testers', 'premium_users'], // User groups
    disabledFor: [], // Excluded user groups
  },
  ADVANCED_TASK_PROFILING: {
    enabled: true,
    rolloutPercentage: 25,
    enabledFor: ['beta_testers'],
    disabledFor: [],
  },
  ENERGY_REPORTING: {
    enabled: true,
    rolloutPercentage: 100, // Available to all users
    enabledFor: [],
    disabledFor: [],
  },
  SLEEP_INTEGRATION: {
    enabled: false, // Not yet enabled
    rolloutPercentage: 0,
    enabledFor: ['internal_testers'],
    disabledFor: [],
  },
};

function isFeatureEnabledForUser(featureName, user) {
  const flag = featureFlags[featureName];
  if (!flag || !flag.enabled) return false;
  
  // Check if user is explicitly enabled
  if (flag.enabledFor.some(group => user.groups.includes(group))) return true;
  
  // Check if user is explicitly disabled
  if (flag.disabledFor.some(group => user.groups.includes(group))) return false;
  
  // Apply percentage rollout
  const userHash = hashUserId(user.id);
  const userPercentile = userHash % 100;
  return userPercentile < flag.rolloutPercentage;
}
```

### Phased Rollout

The rollout follows a phased approach:

1. **Phase 1**: Internal testing with employees (2 weeks)
2. **Phase 2**: Beta testers and power users (4 weeks)
3. **Phase 3**: 25% of users (2 weeks)
4. **Phase 4**: 50% of users (2 weeks)
5. **Phase 5**: 100% of users

```typescript
const rolloutSchedule = [
  {
    phase: 1,
    startDate: '2023-08-15',
    endDate: '2023-08-29',
    userPercentage: 0,
    targetGroups: ['internal_testers'],
    features: ['CIRCADIAN_OPTIMIZATION', 'ADVANCED_TASK_PROFILING', 'ENERGY_REPORTING'],
    successCriteria: {
      errorRate: 0.05, // Less than 5% error rate
      userSatisfaction: 3.5, // Greater than 3.5/5 average satisfaction
    }
  },
  {
    phase: 2,
    startDate: '2023-08-30',
    endDate: '2023-09-27',
    userPercentage: 0,
    targetGroups: ['internal_testers', 'beta_testers', 'power_users'],
    features: ['CIRCADIAN_OPTIMIZATION', 'ADVANCED_TASK_PROFILING', 'ENERGY_REPORTING'],
    successCriteria: {
      errorRate: 0.03,
      userSatisfaction: 3.8,
      scheduleCompletionImprovement: 0.1, // 10% improvement in task completion
    }
  },
  // Additional phases...
];
```

### Monitoring and Rollback Plan

The rollout includes continuous monitoring and rollback capabilities:

1. **Health Metrics**: API latency, error rates, resource utilization
2. **User Metrics**: Satisfaction ratings, feature usage, completion rates
3. **Automated Alerts**: Triggered when metrics exceed thresholds
4. **Rollback Procedures**: Automated and manual rollback capabilities

```typescript
function evaluateRolloutHealth(phase) {
  const metrics = getMetricsForPhase(phase);
  const criteria = rolloutSchedule.find(p => p.phase === phase).successCriteria;
  
  const healthStatus = {
    pass: true,
    metrics: {},
    recommendations: []
  };
  
  // Check each criterion
  if (metrics.errorRate > criteria.errorRate) {
    healthStatus.pass = false;
    healthStatus.metrics.errorRate = {
      actual: metrics.errorRate,
      threshold: criteria.errorRate,
      status: 'FAIL'
    };
    healthStatus.recommendations.push('Investigate high error rates');
  }
  
  if (metrics.userSatisfaction < criteria.userSatisfaction) {
    healthStatus.pass = false;
    healthStatus.metrics.userSatisfaction = {
      actual: metrics.userSatisfaction,
      threshold: criteria.userSatisfaction,
      status: 'FAIL'
    };
    healthStatus.recommendations.push('Review user feedback');
  }
  
  // Additional checks...
  
  return healthStatus;
}

function shouldRollback(phase) {
  const health = evaluateRolloutHealth(phase);
  
  // Automatic rollback criteria
  if (!health.pass) {
    const metrics = health.metrics;
    
    // Critical failure conditions
    if (metrics.errorRate && metrics.errorRate.actual > 0.1) return true; // > 10% error rate
    if (metrics.userSatisfaction && metrics.userSatisfaction.actual < 2.5) return true; // < 2.5/5 satisfaction
    
    // Allow for manual review for non-critical failures
    return false;
  }
  
  return false;
}
```

## Future Enhancements

### Planned Enhancements

The following enhancements are planned for future releases:

1. **Advanced Sleep Integration**:
   - Direct integration with sleep tracking devices
   - Sleep phase-based scheduling recommendations
   - Sleep quality predictions based on schedule

2. **Medication Timing Optimization**:
   - Track medication effects on energy and focus
   - Optimize medication timing for peak performance
   - Account for medication half-life in energy predictions

3. **Environmental Factors Integration**:
   - Weather impact on energy and mood
   - Seasonal affective disorder adjustments
   - Location-based energy predictions

4. **Social Coordination**:
   - Team productivity optimization
   - Meeting scheduling based on group energy patterns
   - Collaborative task scheduling

### Research Areas

The following research areas are being explored:

1. **Multi-Modal Emotion Detection**:
   - Voice analysis for energy and focus detection
   - Facial expression analysis for engagement
   - Typing pattern analysis for cognitive state

2. **Neurological Research Integration**:
   - Research-based ADHD-specific circadian patterns
   - Executive function fluctuation models
   - Hyperfocus prediction and utilization

3. **Advanced Personalization Algorithms**:
   - Transfer learning between similar users
   - Few-shot learning for faster personalization
   - Continual learning with knowledge preservation

## Conclusion

The Dynamic Schedule Rebalancing system with Circadian Rhythm Optimization represents a significant advancement in personalized productivity tools. By aligning tasks with individual energy patterns, the system helps users with ADHD manage their unique cognitive patterns more effectively. 

The technical design outlined in this document provides a robust foundation for implementing, deploying, and evolving this capability. Through a combination of machine learning, reinforcement learning, and user-centered design, the system offers an innovative approach to schedule optimization that adapts to each user's unique patterns.

As the system collects more data and continues to evolve, it will provide increasingly personalized and effective scheduling assistance, helping users achieve their productivity goals while working in harmony with their natural energy patterns. 