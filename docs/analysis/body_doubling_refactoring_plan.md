# Body Doubling Service Refactoring Plan

Based on the technical debt analysis, `body_doubling_service.py` requires significant refactoring. This document outlines a plan to address the issues identified.

## Current Issues

- **Large Class**: `BodyDoublingService` has 12 methods (too many for a single class)
- **High Complexity**: Several functions have high cyclomatic complexity
- **Deep Nesting**: 83 nesting hotspots with depths of up to 5 levels
- **Poor Structure**: Scored 1.00 (maximum) on structure metrics

## Refactoring Strategy

### 1. Apply Service Layer Pattern

Separate the service into multiple specialized classes:

```
BodyDoublingService (orchestration layer)
├── SessionManager (session operations)
├── MatchingEngine (user matching logic)
├── AnalyticsService (statistics and analysis)
└── NotificationService (user notifications)
```

### 2. Code Extraction Examples

#### Original Complex Method
```python
def _calculate_match_score(self, user1, user2):
    score = 0
    if user1.preferences and user2.preferences:
        if user1.preferences.work_style == user2.preferences.work_style:
            score += 10
        if user1.preferences.focus_level == user2.preferences.focus_level:
            score += 8
        # More nested conditions...
        if user1.session_history and user2.session_history:
            for session1 in user1.session_history:
                for session2 in user2.session_history:
                    if session1.productivity_rating > 3 and session2.productivity_rating > 3:
                        score += 5
                        break
    return score
```

#### Refactored Approach
```python
def _calculate_match_score(self, user1, user2):
    if not (user1.preferences and user2.preferences):
        return 0
        
    score = self._score_preferences_match(user1.preferences, user2.preferences)
    score += self._score_history_compatibility(user1.session_history, user2.session_history)
    return score
    
def _score_preferences_match(self, preferences1, preferences2):
    score = 0
    score += 10 if preferences1.work_style == preferences2.work_style else 0
    score += 8 if preferences1.focus_level == preferences2.focus_level else 0
    # More flat scoring logic...
    return score
    
def _score_history_compatibility(self, history1, history2):
    if not (history1 and history2):
        return 0
        
    for session1 in history1:
        if any(s.productivity_rating > 3 for s in history2):
            return 5
    return 0
```

### 3. Breaking Down BodyDoublingService

#### Move to SessionManager
- `create_session`
- `join_session`
- `leave_session` 
- `find_available_sessions`

#### Move to MatchingEngine
- `find_matching_users`
- `_calculate_match_score`
- `suggest_partners`

#### Move to AnalyticsService
- `calculate_trend`
- `calculate_completion_rate`
- `calculate_most_productive_time`
- `calculate_session_type_stats`

### 4. Address Nesting Issues

For all deeply nested code:
1. Extract conditionals to descriptive methods
2. Use early returns to avoid deep nesting
3. Create helper functions for repetitive checks

## Implementation Plan

### Phase 1: Preparation (Week 1)
- Create test cases to ensure behavior doesn't change
- Document current interfaces and behaviors
- Create new files for each service component

### Phase 2: Extraction (Weeks 2-3)
- Move related methods to their new classes
- Update references and dependencies
- Keep facade methods in main service for backward compatibility

### Phase 3: Interface Improvements (Week 4)
- Clean up interfaces between components
- Implement proper error handling
- Reduce parameter lists, use data objects

### Phase 4: Verification (Week 5)
- Run comprehensive tests
- Check performance metrics
- Verify technical debt metrics improve

## Expected Improvements

- **Complexity**: From 0.72 → ~0.30 (58% improvement)
- **Structure**: From 1.00 → ~0.60 (40% improvement)
- **Nesting**: From 1.00 → ~0.40 (60% improvement)

## Future Considerations

- Consider implementing Observer pattern for session notifications
- Add a caching layer for frequently accessed user preferences
- Implement a strategy pattern for different matching algorithms 