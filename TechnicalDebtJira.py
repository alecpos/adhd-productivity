import csv
import os

def create_jira_csv():
    # Your email for assignments
    your_email = "alec@apintegrations.com"
    
    # -------------------------------------------------------------------------
    # Technical Debt Sprint Plan: Organized by priority based on analysis results
    # -------------------------------------------------------------------------
    sprint_plan = {
        "Epic 1: Code Structure Improvements": [
            {
                "summary": "Reduce excessive nesting depth in database.py",
                "description": (
                    "The current database.py file has a nested depth of 10 (recommended max is 4). "
                    "Refactor the code by extracting functions and simplifying nested conditionals.\n\n"
                    "Acceptance Criteria:\n"
                    "- Reduce nesting depth to maximum of 4 levels\n"
                    "- Extract helper functions for error handling\n"
                    "- Maintain all existing functionality\n"
                    "- Add comprehensive tests for the refactored code\n\n"
                    "References: IEEE Software Engineering Standards, Code Quality Metrics"
                )
            },
            {
                "summary": "Refactor main.py to reduce complexity and nesting",
                "description": (
                    "The main.py file has a nested depth of 11 and a dependency score of 1.0 (worst possible). "
                    "Refactor to improve structure and reduce coupling.\n\n"
                    "Acceptance Criteria:\n"
                    "- Reduce nesting depth to maximum of 4 levels\n"
                    "- Decrease dependency score to below 0.5\n"
                    "- Maintain all existing functionality\n"
                    "- Document the refactoring approach\n\n"
                    "References: IEEE Software Engineering Standards"
                )
            },
            {
                "summary": "Improve UI component structure in app/ui directory",
                "description": (
                    "UI components in the app/ui directory have nested depths of 12-14, making them "
                    "difficult to maintain and test. Refactor to improve structure.\n\n"
                    "Acceptance Criteria:\n"
                    "- Reduce nesting depth to maximum of 5 levels\n"
                    "- Break complex components into smaller, more focused ones\n"
                    "- Create unit tests for refactored components\n"
                    "- Document the new component architecture\n\n"
                    "References: Code Quality Metrics (nesting depth < 4 levels)"
                )
            },
            {
                "summary": "Simplify recursive functions in ML models",
                "description": (
                    "Several ML models have high nesting depths and complex recursive functions. "
                    "Refactor to improve readability and maintainability.\n\n"
                    "Acceptance Criteria:\n"
                    "- Reduce function complexity in ML models\n"
                    "- Apply functional programming principles where appropriate\n"
                    "- Document the algorithm changes\n"
                    "- Maintain or improve model performance\n\n"
                    "References: IEEE Software Engineering Standards, Cognitive Complexity < 15"
                )
            }
        ],
        "Epic 2: Task State Machine Improvements": [
            {
                "summary": "Complete TaskModel state transition improvements",
                "description": (
                    "Building on recent updates to the TaskState enum and TaskModel, complete the state "
                    "machine implementation with comprehensive validation and documentation.\n\n"
                    "Acceptance Criteria:\n"
                    "- Implement and test all valid state transitions\n"
                    "- Add proper validation for each transition\n"
                    "- Update timestamp handling for state changes\n"
                    "- Create comprehensive documentation\n"
                    "- Add unit tests for all transition scenarios\n\n"
                    "References: TaskModel is listed as high priority (🟠) in the debt tracker"
                )
            },
            {
                "summary": "Implement TaskState visualization for documentation",
                "description": (
                    "Create a visual representation of the TaskState state machine to improve "
                    "understanding and documentation of valid transitions.\n\n"
                    "Acceptance Criteria:\n"
                    "- Generate state diagram showing all states and transitions\n"
                    "- Include the diagram in project documentation\n"
                    "- Document any potential future states\n"
                    "- Ensure alignment with implementation\n\n"
                    "References: Documentation Standards (80% coverage target)"
                )
            },
            {
                "summary": "Refactor task-related services to use new state machine",
                "description": (
                    "Update all services that interact with TaskModel to properly use the new state "
                    "machine and transition validation.\n\n"
                    "Acceptance Criteria:\n"
                    "- Update TaskService to use TaskState enum\n"
                    "- Ensure SchedulingService handles task states correctly\n"
                    "- Add appropriate error handling for invalid transitions\n"
                    "- Write integration tests for task state transitions\n\n"
                    "References: 'TaskModel' in Technical Debt Tracker"
                )
            }
        ],
        "Epic 3: ML Model Performance Optimization": [
            {
                "summary": "Optimize BayesianDurationPredictor prediction algorithm",
                "description": (
                    "The BayesianDurationPredictor has slow prediction times according to technical debt tracker. "
                    "Optimize the algorithm to improve performance.\n\n"
                    "Acceptance Criteria:\n"
                    "- Reduce prediction time by at least 50%\n"
                    "- Implement caching for similar predictions\n"
                    "- Optimize feature engineering steps\n"
                    "- Maintain prediction accuracy within 5% of original\n"
                    "- Document optimization approach\n\n"
                    "References: ML Models section in Technical Debt Tracker"
                )
            },
            {
                "summary": "Reduce memory consumption in ContextualStressorDetector",
                "description": (
                    "The ContextualStressorDetector has high memory usage according to the technical debt tracker. "
                    "Optimize to reduce memory footprint.\n\n"
                    "Acceptance Criteria:\n"
                    "- Reduce memory usage by at least 40%\n"
                    "- Implement more efficient data structures\n"
                    "- Optimize model architecture\n"
                    "- Maintain or improve detection accuracy\n"
                    "- Document memory optimization approach\n\n"
                    "References: ML Models section in Technical Debt Tracker"
                )
            },
            {
                "summary": "Simplify TimeBufferCalculator logic",
                "description": (
                    "The TimeBufferCalculator has complex buffer logic according to technical debt tracker. "
                    "Simplify to improve maintainability and performance.\n\n"
                    "Acceptance Criteria:\n"
                    "- Reduce function complexity metrics\n"
                    "- Document algorithm improvements\n"
                    "- Create comprehensive tests\n"
                    "- Maintain buffer calculation accuracy\n\n"
                    "References: ML Models section in Technical Debt Tracker"
                )
            }
        ],
        "Epic 4: Test Improvements": [
            {
                "summary": "Refactor test_models.py to reduce complexity",
                "description": (
                    "The test_models.py file has a cyclomatic complexity of 15.4 and very low maintainability (0.11). "
                    "Refactor to improve readability and maintainability.\n\n"
                    "Acceptance Criteria:\n"
                    "- Break down into smaller, focused test files\n"
                    "- Reduce cyclomatic complexity to < 5.0\n"
                    "- Improve maintainability index to > 60\n"
                    "- Maintain or improve test coverage\n"
                    "- Document test organization\n\n"
                    "References: Testing section in Technical Debt Tracker"
                )
            },
            {
                "summary": "Refactor test_schemas.py to reduce complexity",
                "description": (
                    "The test_schemas.py file has a complexity of 6.07 and low maintainability (0.14). "
                    "Refactor to improve readability and maintainability.\n\n"
                    "Acceptance Criteria:\n"
                    "- Break down into smaller, focused test files\n"
                    "- Reduce cyclomatic complexity to < 4.0\n"
                    "- Improve maintainability index to > 60\n"
                    "- Use test fixtures to reduce duplication\n"
                    "- Document test organization\n\n"
                    "References: Testing section in Technical Debt Tracker"
                )
            },
            {
                "summary": "Fix flaky API tests",
                "description": (
                    "Integration tests for APIs are flaky according to technical debt tracker. "
                    "Identify and fix race conditions or other issues.\n\n"
                    "Acceptance Criteria:\n"
                    "- Identify sources of test flakiness\n"
                    "- Implement more robust test assertions\n"
                    "- Add appropriate test timeouts and retries\n"
                    "- Document testing best practices\n"
                    "- Achieve 95% consistent test runs\n\n"
                    "References: Testing section in Technical Debt Tracker"
                )
            },
            {
                "summary": "Implement load testing for critical endpoints",
                "description": (
                    "Missing load testing is listed as a high priority issue in the technical debt tracker. "
                    "Implement comprehensive load tests for critical API endpoints.\n\n"
                    "Acceptance Criteria:\n"
                    "- Set up load testing infrastructure\n"
                    "- Develop test scenarios for critical endpoints\n"
                    "- Establish performance baselines\n"
                    "- Document performance requirements\n"
                    "- Integrate load tests into CI pipeline\n\n"
                    "References: Testing section in Technical Debt Tracker"
                )
            }
        ],
        "Epic 5: API Performance and Security": [
            {
                "summary": "Optimize API response times",
                "description": (
                    "Current API response time is 350ms (target: <200ms) according to technical debt metrics. "
                    "Optimize to improve performance.\n\n"
                    "Acceptance Criteria:\n"
                    "- Identify slow endpoints through profiling\n"
                    "- Optimize database queries\n"
                    "- Implement caching for frequent queries\n"
                    "- Reduce response time to < 200ms\n"
                    "- Document optimization approach\n\n"
                    "References: Performance Debt section in Technical Debt Tracker"
                )
            },
            {
                "summary": "Add missing security headers",
                "description": (
                    "Missing security headers is listed as a high priority issue in the Infrastructure section. "
                    "Implement appropriate headers to improve security.\n\n"
                    "Acceptance Criteria:\n"
                    "- Add Content-Security-Policy headers\n"
                    "- Add X-XSS-Protection headers\n"
                    "- Add X-Content-Type-Options headers\n"
                    "- Add Strict-Transport-Security headers\n"
                    "- Document security header implementation\n\n"
                    "References: Infrastructure section in Technical Debt Tracker, OWASP Guidelines"
                )
            },
            {
                "summary": "Implement rate limiting for API endpoints",
                "description": (
                    "Missing rate limiting is listed as a medium priority issue for calendar events. "
                    "Implement rate limiting for all API endpoints.\n\n"
                    "Acceptance Criteria:\n"
                    "- Add rate limiting middleware\n"
                    "- Configure appropriate limits per endpoint\n"
                    "- Add proper rate limit headers\n"
                    "- Document rate limiting policy\n"
                    "- Test with high-volume requests\n\n"
                    "References: API Routes section in Technical Debt Tracker, OWASP Guidelines"
                )
            }
        ],
        "Epic 6: Model Evolution and Documentation": [
            {
                "summary": "Document ML model architectures",
                "description": (
                    "Missing model architecture docs is listed as a high priority issue. "
                    "Create comprehensive documentation for all ML models.\n\n"
                    "Acceptance Criteria:\n"
                    "- Document architecture of BayesianDurationPredictor\n"
                    "- Document architecture of NLPComplexityAnalyzer\n"
                    "- Document architecture of ContextualStressorDetector\n"
                    "- Document architecture of TimeBufferCalculator\n"
                    "- Include diagrams and implementation details\n\n"
                    "References: Documentation section in Technical Debt Tracker"
                )
            },
            {
                "summary": "Address model purpose drift in TaskModel",
                "description": (
                    "The TaskModel has drifted from its original purpose according to the Model Evolution section. "
                    "Evaluate and refactor to align with core needs.\n\n"
                    "Acceptance Criteria:\n"
                    "- Analyze current TaskModel usage\n"
                    "- Identify core vs. extended functionality\n"
                    "- Propose refactoring to split responsibilities\n"
                    "- Document model purpose and evolution\n"
                    "- Create migration plan if needed\n\n"
                    "References: Model Evolution section in Technical Debt Tracker"
                )
            },
            {
                "summary": "Address redundancy between TaskModel and CalendarEventModel",
                "description": (
                    "CalendarEventModel has redundant fields with TaskModel according to technical debt tracker. "
                    "Refactor to reduce duplication.\n\n"
                    "Acceptance Criteria:\n"
                    "- Identify shared fields and functionality\n"
                    "- Create a common base model or abstraction\n"
                    "- Update data access patterns\n"
                    "- Write migration scripts if needed\n"
                    "- Document the new model relationship\n\n"
                    "References: Database Models section in Technical Debt Tracker"
                )
            },
            {
                "summary": "Update API documentation",
                "description": (
                    "Outdated endpoint documentation is listed as a medium priority issue. "
                    "Update all API documentation to reflect current functionality.\n\n"
                    "Acceptance Criteria:\n"
                    "- Update docs for task-related endpoints\n"
                    "- Update docs for calendar-related endpoints\n"
                    "- Update docs for ML-related endpoints\n"
                    "- Include examples and response formats\n"
                    "- Implement automatic API documentation generation\n\n"
                    "References: Documentation section in Technical Debt Tracker"
                )
            }
        ],
        "Epic 7: Monitoring and Logging": [
            {
                "summary": "Implement comprehensive logging",
                "description": (
                    "Insufficient logging is listed as a high priority issue in the Infrastructure section. "
                    "Implement robust logging across the application.\n\n"
                    "Acceptance Criteria:\n"
                    "- Define logging standards and levels\n"
                    "- Implement structured logging\n"
                    "- Add context to all log messages\n"
                    "- Ensure proper error logging\n"
                    "- Document logging approach\n\n"
                    "References: Infrastructure section in Technical Debt Tracker"
                )
            },
            {
                "summary": "Set up performance monitoring",
                "description": (
                    "Implement monitoring for API response times, database query times, and overall system health.\n\n"
                    "Acceptance Criteria:\n"
                    "- Set up monitoring for API endpoints\n"
                    "- Set up monitoring for database queries\n"
                    "- Set up monitoring for ML model performance\n"
                    "- Create dashboards for key metrics\n"
                    "- Configure alerts for performance degradation\n\n"
                    "References: Performance Debt section in Technical Debt Tracker"
                )
            },
            {
                "summary": "Implement automated technical debt tracking",
                "description": (
                    "Set up tools to automatically track technical debt metrics and update the tracker.\n\n"
                    "Acceptance Criteria:\n"
                    "- Integrate code quality tools into CI pipeline\n"
                    "- Generate reports for technical debt metrics\n"
                    "- Automate updates to technical debt tracker\n"
                    "- Create dashboards for technical debt trends\n"
                    "- Document the technical debt tracking process\n\n"
                    "References: Automation & Tools section in Technical Debt Tracker"
                )
            }
        ]
    }

    # Create CSV file
    csv_file = "technical_debt_jira.csv"
    
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        
        # Write header row
        writer.writerow([
            'Summary', 'Issue Type', 'Description', 'Priority',
            'Labels', 'Epic Link', 'Issue ID', 'Parent', 'Assignee', 'Reporter'
        ])
        
        epic_count = 0
        story_count = 0
        
        for epic, stories in sprint_plan.items():
            epic_count += 1
            epic_id = f"TECHDEBT-{epic_count}"
            
            # Add the epic
            writer.writerow([
                epic,  # Summary
                'Epic',  
                (f"Technical debt reduction focused on improving code quality, performance, "
                 f"and maintainability based on analysis results.\n\n{epic}"),  # Epic description
                'High',
                'TechnicalDebt,Refactoring,CodeQuality',
                '',  # Epic Link
                epic_id,
                '',  # Parent
                your_email,
                your_email
            ])
            
            # Add the stories for this epic
            for story in stories:
                story_count += 1
                story_id = f"TECHDEBT-TASK-{story_count}"
                
                writer.writerow([
                    story["summary"],
                    'Story',
                    story["description"],
                    'Medium',
                    'TechnicalDebt,Refactoring',  
                    epic,
                    story_id,
                    epic_id,
                    your_email,
                    your_email
                ])
    
    print(f"CSV file created: {os.path.abspath(csv_file)}")
    print(f"All tasks assigned to: {your_email}")
    print("\nInstructions for importing into Jira:")
    print("1. Log into your Jira instance")
    print("2. Go to Project settings > Import & Export")
    print("3. Select 'Import from CSV'")
    print("4. Upload your CSV file and follow the wizard")
    print("5. Map the Assignee and Reporter fields during the import")
    print("\nImplementation Strategy:")
    print("- Begin with Epic 1 (Code Structure Improvements) to establish a solid foundation")
    print("- Continue with Epic 2 (Task State Machine Improvements) to address high-priority model debt")
    print("- Then tackle Epic 3 (ML Model Performance) to improve user experience")
    print("- Follow with remaining epics based on resource availability and priority")
    print("- Re-run technical debt analysis after each epic to measure progress")


if __name__ == "__main__":
    create_jira_csv() 