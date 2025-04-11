# Integration Components Refactoring Plan - Part 3: Jira Integration

## Current Issues in `app/ui/integrations/jira_integration.py`

- High nested depth (14)
- Complex mapping logic
- Many responsibilities in a single class
- Overly complex methods
- Unclear separation of concerns

## Refactoring Goals

1. Reduce cyclomatic complexity by at least 40%
2. Limit maximum nesting depth to 3-4 levels
3. Improve separation of concerns
4. Make code more testable
5. Enhance error handling

## Phase 1: Preparation (2 days)

### 1.1 Create Test Suite
- Develop unit tests for all public methods
- Create mocks for Jira API responses
- Document edge cases

### 1.2 Document Current Behavior
- Create sequence diagrams for key operations
- Document Jira-specific mapping rules

## Phase 2: Component Extraction (3 days)

### 2.1 Create `JiraAuthenticator` Class

```python
class JiraAuthenticator:
    """Handles authentication with Jira APIs."""

    def __init__(self, config: ProjectToolConfig):
        self.config = config

    async def authenticate(self) -> bool:
        """Authenticate with Jira using the provided credentials."""
        try:
            headers = self.get_auth_headers()
            # Make test API call
            # await self._make_api_call(f"{self.config.api_url}/rest/api/3/myself", headers=headers)
            return True
        except Exception as e:
            logging.error(f"Failed to authenticate with Jira: {str(e)}")
            return False

    def get_auth_headers(self) -> Dict[str, str]:
        """Create authentication headers for Jira API requests."""
        headers = {"Content-Type": "application/json"}

        if self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"
        elif self.config.auth_user and self.config.auth_password:
            # Basic authentication
            import base64
            auth_str = f"{self.config.auth_user}:{self.config.auth_password}"
            encoded = base64.b64encode(auth_str.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"

        return headers

    async def _make_api_call(self, url, method="GET", headers=None, json=None):
        """Make API call to Jira."""
        # Implementation would use aiohttp or similar
        pass
```

### 2.2 Create `JiraTaskMapper` Class

```python
class JiraTaskMapper:
    """Maps between Jira issues and ADHD Calendar tasks."""

    def jira_to_external_task(self, issue: Dict[str, Any]) -> ExternalTask:
        """Convert a Jira issue to an ExternalTask."""
        fields = issue["fields"]

        return ExternalTask(
            external_id=issue["key"],
            title=fields["summary"],
            description=fields.get("description", ""),
            status=self.map_jira_status_to_internal(fields["status"]["name"]),
            due_date=self._parse_date(fields.get("duedate")),
            created_date=self._parse_date(fields.get("created")),
            updated_date=self._parse_date(fields.get("updated")),
            priority=self.map_jira_priority_to_internal(fields.get("priority", {}).get("name")),
            assignee=fields.get("assignee", {}).get("displayName"),
            labels=fields.get("labels", []),
            project_id=fields["project"]["id"],
            url=f"{issue.get('self', '').split('/rest/')[0]}/browse/{issue['key']}",
            tool_type=ProjectToolType.JIRA,
            additional_data={"key": issue["key"]}
        )

    def internal_to_jira_issue(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Convert an internal task to Jira issue format."""
        issue_data = {
            "fields": {
                "project": {"key": task.get("project_key", "")},
                "summary": task["title"],
                "description": task.get("description", ""),
                "issuetype": {"name": "Task"},
            }
        }

        self._add_optional_fields(issue_data, task)

        return issue_data

    def map_jira_status_to_internal(self, jira_status: str) -> str:
        """Map Jira status to internal status format."""
        status_map = {
            "to do": "not_started",
            "in progress": "in_progress",
            "done": "completed",
            "blocked": "blocked"
        }
        return status_map.get(jira_status.lower(), "not_started")

    def map_internal_status_to_jira(self, internal_status: str) -> str:
        """Map internal status to Jira status format."""
        status_map = {
            "not_started": "To Do",
            "in_progress": "In Progress",
            "completed": "Done",
            "blocked": "Blocked"
        }
        return status_map.get(internal_status, "To Do")

    def map_jira_priority_to_internal(self, jira_priority: Optional[str]) -> str:
        """Map Jira priority to internal priority format."""
        if not jira_priority:
            return "medium"

        priority_map = {
            "highest": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "lowest": "trivial"
        }
        return priority_map.get(jira_priority.lower(), "medium")

    def map_internal_priority_to_jira(self, internal_priority: str) -> str:
        """Map internal priority to Jira priority format."""
        priority_map = {
            "critical": "Highest",
            "high": "High",
            "medium": "Medium",
            "low": "Low",
            "trivial": "Lowest"
        }
        return priority_map.get(internal_priority, "Medium")

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string from Jira."""
        if not date_str:
            return None

        try:
            if 'T' in date_str:
                # ISO format with timezone
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # Simple date format
                return datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            logging.warning(f"Could not parse date: {date_str}")
            return None

    def _add_optional_fields(self, issue_data: Dict[str, Any], task: Dict[str, Any]) -> None:
        """Add optional fields to the Jira issue data."""
        fields = issue_data["fields"]

        if task.get("due_date"):
            fields["duedate"] = task["due_date"].strftime("%Y-%m-%d")

        if task.get("priority"):
            fields["priority"] = {
                "name": self.map_internal_priority_to_jira(task["priority"])
            }

        if task.get("labels"):
            fields["labels"] = task["labels"]
```

### 2.3 Create `JiraQueryBuilder` Class

```python
class JiraQueryBuilder:
    """Builds JQL (Jira Query Language) queries."""

    def build_jql_query(self, config: ProjectToolConfig) -> str:
        """Build a JQL query based on the configuration."""
        jql_parts = []

        # Filter by project if specified
        if config.project_ids:
            project_clause = self._build_project_clause(config.project_ids)
            jql_parts.append(project_clause)

        # Filter by labels if specified
        if config.labels_to_sync:
            label_clause = self._build_label_clause(config.labels_to_sync)
            jql_parts.append(label_clause)

        # Limit to recent updates if not initial sync
        if config.last_sync:
            updated_clause = self._build_updated_clause(config.last_sync)
            jql_parts.append(updated_clause)

        # Combine all parts with AND operator
        jql = " AND ".join(jql_parts) if jql_parts else ""

        # Add default ordering
        jql = self._add_ordering(jql)

        return jql

    def _build_project_clause(self, project_ids: List[str]) -> str:
        """Build a JQL clause to filter by projects."""
        project_clause = " OR ".join([f"project = {pid}" for pid in project_ids])
        return f"({project_clause})"

    def _build_label_clause(self, labels: List[str]) -> str:
        """Build a JQL clause to filter by labels."""
        label_clause = " OR ".join([f"labels = {label}" for label in labels])
        return f"({label_clause})"

    def _build_updated_clause(self, last_sync: datetime) -> str:
        """Build a JQL clause to filter by update date."""
        last_sync_str = last_sync.strftime("%Y-%m-%d %H:%M")
        return f"updated >= '{last_sync_str}'"

    def _add_ordering(self, jql: str) -> str:
        """Add ordering to the JQL query."""
        if jql:
            return f"{jql} ORDER BY updated DESC"
        else:
            return "ORDER BY updated DESC"
```

### 2.4 Create `JiraApiClient` Class

```python
class JiraApiClient:
    """Client for making requests to the Jira API."""

    def __init__(self, config: ProjectToolConfig, authenticator: JiraAuthenticator):
        self.config = config
        self.authenticator = authenticator

    async def get_issues(self, jql: str) -> List[Dict[str, Any]]:
        """Fetch issues from Jira using JQL."""
        url = f"{self.config.api_url}/rest/api/3/search"
        params = {"jql": jql}

        try:
            headers = self.authenticator.get_auth_headers()
            # In real implementation:
            # response = await self._make_request(url, method="GET", params=params, headers=headers)
            # return response.get("issues", [])

            # Mock response for this example
            return self._get_mock_issues()
        except Exception as e:
            logging.error(f"Error fetching Jira issues: {str(e)}")
            raise

    async def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new issue in Jira."""
        url = f"{self.config.api_url}/rest/api/3/issue"

        try:
            headers = self.authenticator.get_auth_headers()
            # In real implementation:
            # return await self._make_request(url, method="POST", json=issue_data, headers=headers)

            # Mock response for this example
            return {"id": "10001", "key": "JRA-124"}
        except Exception as e:
            logging.error(f"Error creating Jira issue: {str(e)}")
            raise

    async def update_issue(self, issue_key: str, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing issue in Jira."""
        url = f"{self.config.api_url}/rest/api/3/issue/{issue_key}"

        try:
            headers = self.authenticator.get_auth_headers()
            # In real implementation:
            # return await self._make_request(url, method="PUT", json=issue_data, headers=headers)

            # Mock response for this example
            return {"id": "10001", "key": issue_key}
        except Exception as e:
            logging.error(f"Error updating Jira issue: {str(e)}")
            raise

    async def delete_issue(self, issue_key: str) -> bool:
        """Delete an issue in Jira."""
        url = f"{self.config.api_url}/rest/api/3/issue/{issue_key}"

        try:
            headers = self.authenticator.get_auth_headers()
            # In real implementation:
            # await self._make_request(url, method="DELETE", headers=headers)
            return True
        except Exception as e:
            logging.error(f"Error deleting Jira issue: {str(e)}")
            raise

    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get available projects from Jira."""
        url = f"{self.config.api_url}/rest/api/3/project"

        try:
            headers = self.authenticator.get_auth_headers()
            # In real implementation:
            # return await self._make_request(url, method="GET", headers=headers)

            # Mock response for this example
            return [{"id": "10000", "key": "JRA", "name": "Jira Project"}]
        except Exception as e:
            logging.error(f"Error fetching Jira projects: {str(e)}")
            raise

    async def _make_request(self, url, method="GET", params=None, headers=None, json=None):
        """Make HTTP request to Jira API."""
        # Implementation would use aiohttp or similar
        pass

    def _get_mock_issues(self):
        """Return mock issues for testing."""
        return [
            {
                "id": "JRA-123",
                "key": "JRA-123",
                "fields": {
                    "summary": "Implement project sync",
                    "description": "Create bidirectional sync with project tools",
                    "status": {"name": "In Progress"},
                    "duedate": "2023-06-30",
                    "created": "2023-05-01T10:00:00.000Z",
                    "updated": "2023-05-15T14:30:00.000Z",
                    "priority": {"name": "High"},
                    "assignee": {"displayName": "John Doe"},
                    "labels": ["adhd-calendar", "integration"],
                    "project": {"id": "10000", "key": "JRA"}
                }
            }
        ]
```
