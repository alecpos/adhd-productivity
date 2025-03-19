# Epic 4: Technical Design Document - Part 2
# Dynamic Schedule Rebalancing with Circadian Rhythm Optimization

## Algorithms and Machine Learning Models

### Task Cognitive Profiling

The Task Cognitive Profiling system analyzes tasks to determine their cognitive demand profiles, which are critical for matching tasks to appropriate energy states.

#### Cognitive Demand Classification

Tasks are classified across multiple cognitive dimensions:

1. **Focus Intensity**: Required level of sustained attention (1-10)
2. **Executive Function Load**: Required planning and decision making (1-10)
3. **Creative Thinking**: Required creative or divergent thinking (1-10)
4. **Complexity**: Overall task complexity (1-10)

The classification is performed using a multi-output regression model:

```python
class TaskCognitiveProfiler:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.model = MultiOutputRegressor(RandomForestRegressor(n_estimators=100))
        self.label_columns = ['focus_required', 'executive_function_load', 
                            'creative_required', 'complexity']
        
    def train(self, training_data):
        """Train the model on labeled task data"""
        X_text = [task['title'] + ' ' + (task['description'] or '') for task in training_data]
        X_features = self._extract_metadata_features(training_data)
        
        # Transform text to TF-IDF features
        X_text_tfidf = self.vectorizer.fit_transform(X_text)
        
        # Combine text features with metadata features
        X = hstack([X_text_tfidf, X_features])
        
        # Extract labels
        y = np.array([[task[label] for label in self.label_columns] for task in training_data])
        
        # Train model
        self.model.fit(X, y)
        
    def predict_cognitive_demands(self, task):
        """Predict cognitive demands for a new task"""
        X_text = [task['title'] + ' ' + (task['description'] or '')]
        X_features = self._extract_metadata_features([task])
        
        X_text_tfidf = self.vectorizer.transform(X_text)
        X = hstack([X_text_tfidf, X_features])
        
        predictions = self.model.predict(X)[0]
        
        return {
            label: prediction for label, prediction in zip(self.label_columns, predictions)
        }
        
    def _extract_metadata_features(self, tasks):
        """Extract numerical and categorical features from task metadata"""
        features = []
        
        for task in tasks:
            task_features = [
                task.get('duration_minutes', 0) / 60.0,  # Normalize to hours
                self._priority_to_numeric(task.get('priority', 'MEDIUM')),
                1 if task.get('is_flexible', True) else 0,
                self._calculate_deadline_pressure(task.get('deadline'))
            ]
            
            # Add task type one-hot encoding if available
            if 'task_type' in task:
                task_type_features = self._one_hot_encode_task_type(task['task_type'])
                task_features.extend(task_type_features)
                
            features.append(task_features)
            
        return np.array(features)
```

#### NLP-Based Task Analysis

For tasks with detailed descriptions, we employ NLP techniques to extract additional insights:

```python
class TaskNLPAnalyzer:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_md')
        self.cognitive_keywords = self._load_cognitive_keywords()
        
    def analyze_description(self, description):
        """Extract cognitive indicators from task description"""
        if not description:
            return {}
            
        doc = self.nlp(description)
        
        analysis = {
            'cognitive_indicators': self._extract_cognitive_indicators(doc),
            'complexity_indicators': self._extract_complexity_indicators(doc),
            'key_verbs': self._extract_key_action_verbs(doc),
            'time_expressions': self._extract_time_expressions(doc)
        }
        
        return analysis
        
    def _extract_cognitive_indicators(self, doc):
        """Identify words and phrases suggesting cognitive demands"""
        indicators = {
            'focus': 0,
            'executive_function': 0,
            'creative': 0,
            'memory': 0
        }
        
        # Simplified logic - actual implementation would be more sophisticated
        for token in doc:
            if token.text.lower() in self.cognitive_keywords['focus']:
                indicators['focus'] += 1
            # Similar for other cognitive categories
                
        return indicators
```

### Reinforcement Learning for Schedule Optimization

The schedule optimization process uses a modified Deep Q-Network approach with circadian-specific adaptations.

#### State Representation

The state space includes:

1. **Task Features**: Properties of each task (priority, deadline, cognitive demands)
2. **Time Features**: Properties of each time slot (hour, day of week, date)
3. **Energy Predictions**: Predicted energy levels for each time slot
4. **Schedule Context**: Currently scheduled tasks and their properties
5. **User Preferences**: Task type weightings and scheduling constraints

```python
def create_state_representation(tasks, time_slots, energy_levels, current_schedule, user_preferences):
    # Task encoding
    task_encodings = []
    for task in tasks:
        task_encoding = [
            normalize_priority(task.priority),
            normalize_deadline_pressure(task.deadline),
            task.duration_minutes / 60.0,  # Normalize to hours
            task.focus_required / 10.0,    # Normalize to 0-1
            task.executive_function_load / 10.0,
            task.creative_required / 10.0,
            task.complexity / 10.0,
            1.0 if task.is_flexible else 0.0
        ]
        task_encodings.append(task_encoding)
    
    # Time slot encoding
    time_slot_encodings = []
    for slot in time_slots:
        hour_sin = math.sin(2 * math.pi * slot.hour / 24)
        hour_cos = math.cos(2 * math.pi * slot.hour / 24)
        
        day_of_week_sin = math.sin(2 * math.pi * slot.day_of_week / 7)
        day_of_week_cos = math.cos(2 * math.pi * slot.day_of_week / 7)
        
        time_encoding = [
            hour_sin,
            hour_cos,
            day_of_week_sin,
            day_of_week_cos,
            1.0 if is_weekend(slot.day_of_week) else 0.0,
            normalize_date(slot.date)
        ]
        time_slot_encodings.append(time_encoding)
    
    # Energy level encoding
    energy_encodings = []
    for energy in energy_levels:
        energy_encoding = [
            energy.energy_level / 10.0,
            energy.focus_capacity / 10.0,
            energy.creative_capacity / 10.0,
            energy.executive_function_capacity / 10.0
        ]
        energy_encodings.append(energy_encoding)
    
    # Schedule context encoding
    schedule_encoding = encode_current_schedule(current_schedule)
    
    # User preferences encoding
    preferences_encoding = [
        user_preferences.priority_weight,
        user_preferences.deadline_weight,
        user_preferences.cognitive_matching_weight,
        user_preferences.optimization_strength
    ]
    
    # Combine all encodings
    state = {
        'tasks': task_encodings,
        'time_slots': time_slot_encodings,
        'energy_levels': energy_encodings,
        'schedule': schedule_encoding,
        'preferences': preferences_encoding
    }
    
    return state
```

#### Action Space

The action space consists of all possible assignments of tasks to time slots, with special actions for scheduling breaks and creating buffer time.

#### Reward Function

The reward function combines multiple components:

1. **Energy-Task Alignment**: How well the task's cognitive demands match energy levels
2. **Priority Satisfaction**: Reward for scheduling high-priority tasks
3. **Deadline Compliance**: Reward for scheduling tasks well before deadlines
4. **Workload Balance**: Penalty for overloading certain time periods
5. **Context Switching**: Penalty for excessive task type switching

```python
def calculate_reward(task, time_slot, energy_level, schedule_context, user_preferences):
    # Energy-task alignment reward
    alignment_reward = calculate_energy_task_alignment(
        task.cognitive_demands,
        energy_level
    )
    
    # Priority reward
    priority_reward = calculate_priority_reward(task.priority)
    
    # Deadline reward
    deadline_reward = calculate_deadline_reward(
        task.deadline,
        time_slot.timestamp
    )
    
    # Workload balance penalty
    workload_penalty = calculate_workload_penalty(
        schedule_context,
        time_slot
    )
    
    # Context switching penalty
    switching_penalty = calculate_context_switching_penalty(
        task.type,
        schedule_context,
        time_slot
    )
    
    # Combine rewards with user preference weights
    total_reward = (
        user_preferences.alignment_weight * alignment_reward +
        user_preferences.priority_weight * priority_reward +
        user_preferences.deadline_weight * deadline_reward -
        user_preferences.workload_weight * workload_penalty -
        user_preferences.switching_weight * switching_penalty
    )
    
    return total_reward
```

#### Training Process

The DQN model is trained using a combination of:

1. **Offline Training**: Initial training on historical data from similar users
2. **Online Fine-tuning**: Continuous personalization based on user feedback
3. **Transfer Learning**: Adapting general patterns to individual users

### Harmonic Modeling for Circadian Rhythms

The core of the energy prediction system is a harmonic model that captures the natural oscillations in human energy levels.

#### Mathematical Foundations

We model energy levels as a combination of harmonic components:

```python
def predict_energy(time, params):
    """Predict energy using harmonic components"""
    # Convert time to fractional hours since midnight
    hours = time.hour + time.minute / 60.0
    
    # Base level
    energy = params['base_level']
    
    # Primary circadian rhythm (approximately 24 hours)
    energy += params['primary_amplitude'] * math.sin(
        2 * math.pi * (hours - params['primary_phase']) / 24.0
    )
    
    # Secondary rhythm (approximately 12 hours - post-lunch dip)
    energy += params['secondary_amplitude'] * math.sin(
        2 * math.pi * (hours - params['secondary_phase']) / 12.0
    )
    
    # Tertiary rhythm (ultradian rhythm ~4 hours)
    energy += params['tertiary_amplitude'] * math.sin(
        2 * math.pi * (hours - params['tertiary_phase']) / 4.0
    )
    
    # Apply day of week adjustment
    day_of_week = time.weekday()
    energy += params['day_adjustment'][day_of_week]
    
    # Apply contextual adjustments (time since waking, meals, etc.)
    energy += calculate_contextual_adjustments(time, params)
    
    return max(1.0, min(10.0, energy))  # Clamp to 1-10 scale
```

#### Parameter Estimation

The model parameters are estimated using Bayesian methods to handle sparse and noisy data:

```python
class CircadianParameterEstimator:
    def __init__(self, prior_params=None):
        self.prior_params = prior_params or self._default_prior_params()
        
    def estimate_parameters(self, user_id, energy_reports):
        """Estimate circadian parameters from user-reported energy levels"""
        if len(energy_reports) < 10:
            # Not enough data, return population defaults with slight adjustments
            return self._estimate_with_limited_data(user_id, energy_reports)
            
        # Extract times and reported energy levels
        times = [report['timestamp'] for report in energy_reports]
        energy_levels = [report['energy_level'] for report in energy_reports]
        
        # Initial parameter guess (from prior or previous estimate)
        initial_params = self._get_initial_params(user_id)
        
        # Define objective function for optimization
        def objective(params_vector):
            params = self._vector_to_params(params_vector)
            predictions = [predict_energy(t, params) for t in times]
            return sum((pred - actual) ** 2 for pred, actual in zip(predictions, energy_levels))
        
        # Run optimization
        result = minimize(
            objective,
            self._params_to_vector(initial_params),
            method='L-BFGS-B',
            bounds=self._parameter_bounds()
        )
        
        # Convert optimized vector back to parameter dictionary
        optimized_params = self._vector_to_params(result.x)
        
        # Apply Bayesian update to combine with prior
        posterior_params = self._bayesian_update(optimized_params, len(energy_reports))
        
        return posterior_params
```

#### Multi-dimensional Energy Modeling

We track multiple energy dimensions to capture different aspects of cognitive capacity:

```python
class MultiDimensionalEnergyModel:
    def __init__(self, user_id):
        self.user_id = user_id
        self.dimensions = {
            'general_energy': CircadianRhythmModel(user_id, 'general_energy'),
            'focus': CircadianRhythmModel(user_id, 'focus'),
            'creativity': CircadianRhythmModel(user_id, 'creativity'),
            'executive_function': CircadianRhythmModel(user_id, 'executive_function')
        }
        
    def predict_multidimensional_energy(self, timestamp):
        """Predict energy levels across all dimensions"""
        return {
            dim_name: model.predict_energy(timestamp)
            for dim_name, model in self.dimensions.items()
        }
        
    def update_with_report(self, timestamp, energy_report):
        """Update models with a new energy report"""
        for dim_name, model in self.dimensions.items():
            if dim_name in energy_report:
                model.update_with_reported_level(timestamp, energy_report[dim_name])
```

## Optimization Techniques

### Dynamic Schedule Rebalancing

The system continually rebalances schedules in response to changes using several approaches:

#### Incremental Optimization

When minor changes occur, we use incremental optimization to avoid completely rebuilding the schedule:

```python
def incremental_rebalance(original_schedule, changes, energy_predictions):
    """Rebalance a schedule when small changes occur"""
    # Identify affected time slots
    affected_slots = identify_affected_slots(original_schedule, changes)
    
    # Extract tasks that need to be rescheduled
    tasks_to_reschedule = extract_affected_tasks(original_schedule, affected_slots)
    
    # Remove affected tasks from schedule
    partial_schedule = remove_tasks_from_schedule(original_schedule, tasks_to_reschedule)
    
    # Find available time slots in the partial schedule
    available_slots = find_available_slots(partial_schedule)
    
    # Optimize placement of tasks into available slots
    optimized_placement = optimize_task_placement(
        tasks_to_reschedule,
        available_slots,
        energy_predictions
    )
    
    # Merge optimized placement back into the schedule
    new_schedule = merge_schedules(partial_schedule, optimized_placement)
    
    return new_schedule
```

#### Priority-Based Rescheduling

When major disruptions occur, we use priority-based rescheduling:

```python
def priority_based_rebalance(tasks, constraints, energy_predictions):
    """Rebuild a schedule based on task priorities when major changes occur"""
    # Sort tasks by priority
    sorted_tasks = sorted(tasks, key=lambda t: priority_score(t), reverse=True)
    
    # Initialize empty schedule
    schedule = initialize_empty_schedule(constraints)
    
    # Schedule high-priority tasks first
    for task in sorted_tasks:
        # Find optimal time slot for this task
        best_slot = find_optimal_slot(task, schedule, energy_predictions)
        
        if best_slot:
            # Add task to schedule
            schedule = add_task_to_schedule(schedule, task, best_slot)
        else:
            # Handle unable to schedule
            handle_unschedulable_task(task)
    
    return schedule
```

### Optimization Constraints

The system respects several types of constraints:

1. **Hard Constraints**: Must be satisfied (fixed appointments, unavailable time)
2. **Soft Constraints**: Preferences that can be violated if necessary
3. **User-Defined Constraints**: Custom rules set by the user

```python
class ConstraintProcessor:
    def __init__(self):
        self.constraint_handlers = {
            'fixed_appointment': self._handle_fixed_appointment,
            'unavailable_time': self._handle_unavailable_time,
            'preferred_time': self._handle_preferred_time,
            'task_sequence': self._handle_task_sequence,
            'max_tasks_per_day': self._handle_max_tasks_per_day,
            'buffer_time': self._handle_buffer_time,
            'break_time': self._handle_break_time
        }
        
    def apply_constraints(self, schedule, constraints):
        """Apply all constraints to a schedule"""
        for constraint in constraints:
            handler = self.constraint_handlers.get(constraint['type'])
            if handler:
                schedule = handler(schedule, constraint)
                
        return schedule
        
    def check_constraint_violations(self, schedule, constraints):
        """Check for constraint violations in a schedule"""
        violations = []
        
        for constraint in constraints:
            if constraint.get('hard', False):  # Only check hard constraints
                handler = self._get_violation_checker(constraint['type'])
                if handler:
                    constraint_violations = handler(schedule, constraint)
                    violations.extend(constraint_violations)
                    
        return violations
```

## Performance Optimization

### Computational Efficiency

The system uses several techniques to ensure computational efficiency:

1. **Batch Processing**: Grouping operations for efficient processing
2. **Caching**: Caching energy predictions and intermediate results
3. **Progressive Optimization**: Starting with coarse optimization and refining

```python
class OptimizationService:
    def __init__(self):
        self.prediction_cache = {}
        self.recently_optimized = LRUCache(100)
        
    def optimize_schedule(self, user_id, tasks, timeframe, preferences):
        """Optimize a user's schedule with performance optimizations"""
        cache_key = self._generate_cache_key(user_id, tasks, timeframe)
        
        # Check if we've recently computed this or something similar
        if cache_key in self.recently_optimized:
            cached_result = self.recently_optimized[cache_key]
            if self._is_still_valid(cached_result, tasks, timeframe):
                return cached_result
        
        # Get energy predictions (cached when possible)
        energy_predictions = self._get_energy_predictions(user_id, timeframe)
        
        # Start with coarse optimization (1-hour blocks)
        coarse_schedule = self._coarse_optimization(
            tasks, timeframe, energy_predictions, preferences
        )
        
        # Refine with fine-grained optimization (15-minute blocks)
        fine_schedule = self._fine_optimization(
            coarse_schedule, energy_predictions, preferences
        )
        
        # Cache the result
        self.recently_optimized[cache_key] = fine_schedule
        
        return fine_schedule
```

### Parallel Processing

For complex optimizations, we use parallel processing to improve performance:

```python
def parallel_schedule_optimization(tasks, timeframe, energy_predictions, num_workers=4):
    """Optimize schedule using parallel processing"""
    # Split tasks into chunks
    task_chunks = split_tasks_into_chunks(tasks, num_workers)
    
    # Create a process pool
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Submit optimization jobs
        future_to_chunk = {
            executor.submit(
                optimize_task_chunk, 
                chunk, 
                timeframe, 
                energy_predictions
            ): i for i, chunk in enumerate(task_chunks)
        }
        
        # Collect results
        chunk_results = []
        for future in as_completed(future_to_chunk):
            chunk_idx = future_to_chunk[future]
            try:
                result = future.result()
                chunk_results.append((chunk_idx, result))
            except Exception as e:
                print(f"Chunk {chunk_idx} generated an exception: {e}")
                
        # Sort results by chunk index
        chunk_results.sort(key=lambda x: x[0])
        
        # Merge optimized chunks
        merged_schedule = merge_optimized_chunks([r[1] for r in chunk_results])
        
        # Final conflict resolution pass
        final_schedule = resolve_conflicts(merged_schedule)
        
        return final_schedule
``` 