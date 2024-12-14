import requests

def update_jira_issue(issue_key, commit_info):
    """
    Update the Jira issue with the details from the commit_info.
    Add the issue/solution details as a comment, and update the description.
    """
    if not JIRA_BASE_URL or not JIRA_USERNAME or not JIRA_API_TOKEN:
        print("Jira configuration not found. Skipping Jira updates.")
        return

    # Update the description by appending the large_description
    # Add a comment with the issue and solution

    # Get current issue details
    issue_url = f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Get current description
    response = requests.get(issue_url, auth=auth, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve Jira issue {issue_key}, status code: {response.status_code}")
        return

    issue_data = response.json()
    current_description = issue_data['fields'].get('description', '')

    # Convert large_description list to string
    large_description_str = "\n".join(commit_info['large_description'])
    new_description = (current_description or '') + "\n\n" + large_description_str

    # Update issue description
    update_payload = {
        "fields": {
            "description": new_description
        }
    }

    r = requests.put(issue_url, json=update_payload, headers=headers, auth=auth)
    if r.status_code not in [200, 204]:
        print(f"Failed to update Jira issue {issue_key} description. Status code: {r.status_code}")

    # Add issue/solution as a comment
    comment_url = issue_url + "/comment"
    # Convert issue and solution lists to strings
    issue_str = "\n".join(commit_info['issue'])
    solution_str = "\n".join(commit_info['solution'])
    comment_text = f"Issue Details:\n{issue_str}\n\nSolution Details:\n{solution_str}"
    comment_payload = {"body": comment_text}
    c = requests.post(comment_url, json=comment_payload, headers=headers, auth=auth)
    if c.status_code not in [200, 201]:
        print(f"Failed to add comment to Jira issue {issue_key}. Status code: {c.status_code}")
    else:
        print(f"Jira issue {issue_key} successfully updated.")

def create_jira_issue(commit_info, project_key):
    """
    Create a new Jira issue with the details from commit_info and return the new issue key.
    """
    if not JIRA_BASE_URL or not JIRA_USERNAME or not JIRA_API_TOKEN:
        print("Jira configuration not found. Skipping Jira issue creation.")
        return None

    issue_url = f"{JIRA_BASE_URL}/rest/api/2/issue"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    summary = commit_info['message']
    description = commit_info['large_description']

    payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": "Task"
            }
        }
    }

    r = requests.post(issue_url, json=payload, auth=auth)
    if r.status_code not in [200, 201]:
        print(f"Failed to create Jira issue. Status code: {r.status_code}")
        return None
    data = r.json()
    issue_key = data['key']

    # Add issue/solution as comment
    comment_url = f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}/comment"
    comment_text = f"**Issue Details:**\n{commit_info['issue']}\n\n**Solution Details:**\n{commit_info['solution']}"
    c = requests.post(comment_url, json={"body": comment_text}, auth=auth)
    if c.status_code not in [200, 201]:
        print(f"Failed to add comment to new Jira issue {issue_key}. Status code: {c.status_code}")

    print(f"New Jira issue {issue_key} created successfully.")
    return issue_key