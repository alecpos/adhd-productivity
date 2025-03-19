# ADHD Calendar Frontend Components

This directory contains the React Native components for the ADHD Calendar application. The components are organized according to the six epics of the project.

## Main Components

### `ADHDCalendarDashboard`

The main dashboard that provides access to all features from the six epics. It offers:
- Filtering by epic number
- A visually appealing card-based interface
- Clear categorization of features

## Epic 1: Temporal Pattern Recognition

### `ProductivityPatternViewer`

Shows productivity patterns over time using the LSTM-based models. Features:
- Visualization of daily, weekly, and monthly patterns
- Insights generated from the productivity data
- Interactive charts for data exploration

### `CircadianRhythmView`

Displays the user's energy patterns throughout the day. Features:
- Energy level visualization
- Task type selection based on energy requirements
- Optimal time block recommendations based on energy patterns

## Epic 2: Stochastic Time Estimation

### `DurationEstimator`

Helps users get more accurate time estimates for tasks. Features:
- Task description analysis
- Complexity factor breakdown
- Bayesian prediction of minimum, maximum, and most likely durations
- Visualization of duration distribution

## Epic 3: Proactive Forgetfulness and Distraction Mitigation

### `CommitmentTracker`

Helps users track and manage commitments detected from various sources. Features:
- Commitment filtering by status
- Priority visualization
- Related commitment detection
- Add/complete/delete commitment actions

## Epic 4: Dynamic Schedule Rebalancing

### `ScheduleOptimizer`

Dynamically rebalances the user's schedule based on energy levels and priorities. Features:
- Schedule optimization with clear before/after comparison
- Energy-aware scheduling visualization
- Configurable optimization settings
- Break insertion and schedule rebalancing

## Epic 5: Fairness, Bias Mitigation, and Ethical Implementation

### `ExplainableAI`

Provides transparent explanations for AI recommendations. Features:
- Feature importance visualization
- Simplified and detailed explanation modes
- Counterfactual explanations
- Dataset information for transparency

## Epic 6: User Experience and Interface Optimization

### `AdaptiveUI`

Provides a neurodiverse-optimized UI with customization options. Features:
- Adaptive UI preferences
- Energy level-based UI adjustments
- Motivation profile visualization
- Achievement tracking and gamification

## Installation

Make sure you have Expo installed:

```
npm install -g expo-cli
```

Install the dependencies:

```
npm install
```

## Running the App

```
npm start
```

## Running the App Without Problematic Dependencies

We've created a simplified version of the app that doesn't rely on `expo-notifications` or other problematic dependencies that were causing the `LegacyEventEmitter` error.

### How to Run the Simplified App

```
cd frontend
npm run start:simple
```

This uses our custom SimpleTestApp component that provides a navigation interface to all the ADHD Calendar components without relying on Expo Router.

### Changes Made to Fix the Error

1. **Removed problematic dependencies**:
   ```
   npm uninstall expo-notifications expo-linear-gradient
   ```

2. **Created a standalone app**: `SimpleTestApp.tsx` provides a simple navigation interface to all our components without using Expo Router.

3. **Updated configuration**:
   - Modified `package.json` to use App.tsx as the main entry point
   - Added a `start:simple` script that disables Expo Router
   - Updated app.config.js to use our custom entry point

4. **Fixed import paths**: Updated component imports to use relative paths instead of alias paths.

5. **Removed Expo Router references**: Our simplified app doesn't rely on the router functionality that was causing errors.

### Component Organization

All components are organized by Epic:

1. **Epic 1: Temporal Pattern Recognition**
   - ProductivityPatternViewer
   - CircadianRhythmView

2. **Epic 2: Stochastic Time Estimation**
   - DurationEstimator

3. **Epic 3: Proactive Forgetfulness and Distraction Mitigation**
   - CommitmentTracker

4. **Epic 4: Dynamic Schedule Rebalancing**
   - ScheduleOptimizer

5. **Epic 5: Fairness, Bias Mitigation, and Ethical Implementation**
   - ExplainableAI

6. **Epic 6: User Experience and Interface Optimization**
   - AdaptiveUI

### Main Dashboard

- ADHDCalendarDashboard provides access to all components

## Dependencies

- React Native
- Expo
- React Navigation
- React Native Elements
- React Native Chart Kit

## Notes

- All components are responsive and work on both mobile and tablet devices
- Accessibility features are built into the UI components
- The app is designed with ADHD-specific needs in mind
- Error handling is implemented throughout the components

## Running the Web Version

We've created multiple options for running the web version of the app:

### 1. Standard Web Version

```
npm run web
```

This uses Expo's web bundler to create a web version of the app using Expo Router.

> Note: This may have issues with module compatibility in web environments.

### 2. Simple Web Version

```
npm run web:basic
```

This serves a pre-built static HTML/CSS/JS version of the app that doesn't rely on problematic native modules. This is the most reliable way to view the app on web.

The basic web version provides:
- A simple navigation interface to view key components
- Working charts and visualizations
- Sample data to demonstrate functionality

### Web Compatibility Issues

The ADHD Calendar app relies on several native modules that don't have proper web implementations. We've implemented workarounds:

1. **expo-notifications**: Created a mock implementation that simulates notification behavior on web
2. **expo-file-system**: Created a mock implementation for web
3. **Font loading**: Simplified to use system fonts on web

For the best experience, we recommend using the mobile version of the app, but the web version provides a good way to view and interact with the components. 