import base64
import json
import logging
import os

import requests


def create_jira_tasks():
    # ---------------------------------------------------------------------
    # Setup Python logging for both console and file output
    # ---------------------------------------------------------------------
    # If you want a different log file name or path, change 'jira_script.log' below.
    # The log file will contain DEBUG-level messages, while console is at INFO level.
    log_file_name = "jira_script.log"
    logging.basicConfig(
        level=logging.DEBUG,  # File log level
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.FileHandler(log_file_name, mode="a"), logging.StreamHandler()],  # console
    )
    logger = logging.getLogger(__name__)

    logger.info("----- Starting Jira Task Creation Script -----")

    # --------------------------
    # Jira connection info
    # --------------------------
    JIRA_URL = "https://apintegrations-team.atlassian.net"
    JIRA_EMAIL = "alec@apintegrations.com"
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")  # Get from environment variable
    PROJECT_KEY = "SCRUM"

    logger.debug(f"JIRA_URL: {JIRA_URL}")
    logger.debug(f"JIRA_EMAIL: {JIRA_EMAIL}")
    logger.debug(f"PROJECT_KEY: {PROJECT_KEY}")
    logger.debug("JIRA_API_TOKEN: [REDACTED]")

    # If you *know* your Sprint ID and want to add issues to that sprint, uncomment:
    # SPRINT_ID = 12345

    basic_token = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode()).decode()
    headers = {"Content-Type": "application/json", "Authorization": f"Basic {basic_token}"}

    # -----------------------------------------------------------
    # 1) Define the structure of your parent and child tasks
    # -----------------------------------------------------------
    sprint_plan = {
        "Parent Task 1: Set Up Project Environment": [
            "Install Required Libraries",
            "Configure TypeScript",
            "Set Up ThemeProvider",
        ],
        "Parent Task 2: Define Theme Structure": [
            "Define Theme Interface",
            "Implement Light/Dark Themes",
            "Extend Theme Properties",
        ],
        "Parent Task 3: Implement Theme Toggle Functionality": [
            "Create Theme Context",
            "Integrate Context with ThemeProvider",
            "Add Toggle Button",
        ],
        "Parent Task 4: Apply Theming to Components": [
            "Refactor Core Components",
            "Update Screens for Theming",
            "Handle Edge Cases",
        ],
        "Parent Task 5: Testing and QA": [
            "Write Unit Tests for Theme Context",
            "Test Components with Themes",
            "Perform Manual Testing on Devices",
        ],
    }

    logger.info("Sprint plan defined with 5 parent tasks.")

    # -----------------------------------------------------------
    # 2) Create parent tasks in Jira (issuetype = "Task")
    # -----------------------------------------------------------
    parent_keys = {}  # Store the Jira issue keys for each parent task

    for parent_summary, child_summaries in sprint_plan.items():
        parent_payload = {
            "fields": {
                "summary": parent_summary,
                "description": f"{parent_summary}\n\n(Refer to the sprint plan for details.)",
                "project": {"key": PROJECT_KEY},
                "issuetype": {"name": "Task"},
                # If you want to add to a specific sprint:
                # "customfield_10007": SPRINT_ID
            }
        }

        logger.info(f"Creating parent task: '{parent_summary}'")
        logger.debug(f"Parent payload: {json.dumps(parent_payload, indent=2)}")

        response = requests.post(
            f"{JIRA_URL}/rest/api/3/issue", headers=headers, data=json.dumps(parent_payload)
        )

        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Content: {response.text}")

        if response.status_code == 201:
            parent_key = response.json()["key"]
            parent_keys[parent_summary] = parent_key
            logger.info(f"Created parent task: {parent_summary} -> {parent_key}")
        else:
            logger.error(
                f"Failed to create parent task: {parent_summary}. " f"Response: {response.text}"
            )
            # Move to next parent task instead of trying to create sub-tasks

        # -----------------------------------------------------------
        # 3) For each parent task, create its child sub-tasks
        # -----------------------------------------------------------
        for child_summary in child_summaries:
            child_payload = {
                "fields": {
                    "summary": child_summary,
                    "description": f"Sub-task of {parent_summary}.\n\nDetail: {child_summary}",
                    "project": {"key": PROJECT_KEY},
                    # In many Jira instances, subtask type is "Subtask" (no hyphen)
                    "issuetype": {"name": "Subtask"},
                    "parent": {"key": parent_key},
                    # "customfield_10007": SPRINT_ID
                }
            }

            logger.info(
                f"  Creating sub-task '{child_summary}' under parent '{parent_summary}' ({parent_key})"
            )
            logger.debug(f"  Sub-task payload: {json.dumps(child_payload, indent=2)}")

            child_response = requests.post(
                f"{JIRA_URL}/rest/api/3/issue", headers=headers, data=json.dumps(child_payload)
            )

            logger.debug(f"  Response Status Code: {child_response.status_code}")
            logger.debug(f"  Response Content: {child_response.text}")

            if child_response.status_code == 201:
                child_key = child_response.json()["key"]
                logger.info(f"    Created sub-task: {child_summary} -> {child_key}")
            else:
                logger.error(
                    f"    Failed to create sub-task: {child_summary}. "
                    f"Response: {child_response.text}"
                )

    logger.info("----- Finished creating Jira tasks -----")


if __name__ == "__main__":
    create_jira_tasks()
