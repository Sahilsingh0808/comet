import openai
import os
import subprocess
import json
from dotenv import load_dotenv
import requests
import re

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "DGA")

def get_unstaged_changes():
    """
    Get list of files that have changes but are not staged.
    """
    try:
        diff_output = subprocess.check_output(["git", "ls-files", "--others", "--modified", "--exclude-standard"], text=True)
        files = diff_output.strip().split('\n') if diff_output.strip() else []
        return files
    except subprocess.CalledProcessError:
        return []

def get_staged_diff():
    """
    Gets the current staged git diff.
    """
    try:
        diff_output = subprocess.check_output(["git", "diff", "--staged"], text=True)
        return diff_output
    except subprocess.CalledProcessError as e:
        print("Error getting git diff:", e)
        return None
    
def validate_commit_info(commit_info):
    """
    Validates the structure and content of the commit_info dictionary.

    Args:
        commit_info (dict): The dictionary containing AI-generated commit information.

    Returns:
        bool: True if the commit_info is valid, False otherwise.
    """
    required_fields = {
        "message": str,
        "small_description": list,
        "large_description": list,
        "file_changes": list,
        "issue": list,
        "solution": list,
        "impact": int,
        "priority": int,
    }

    # Check for missing fields and correct types
    for field, expected_type in required_fields.items():
        if field not in commit_info:
            print(f"Missing field: {field}")
            return False
        if not isinstance(commit_info[field], expected_type):
            print(f"Incorrect type for field '{field}'. Expected {expected_type.__name__}, got {type(commit_info[field]).__name__}.")
            return False

    # Validate ranges for impact and priority
    if not (1 <= commit_info["impact"] <= 5):
        print(f"Invalid value for 'impact': {commit_info['impact']}. It should be between 1 and 5.")
        return False
    if not (1 <= commit_info["priority"] <= 5):
        print(f"Invalid value for 'priority': {commit_info['priority']}. It should be between 1 and 5.")
        return False

    # All checks passed
    return True
    
def extract_json_from_response(response_content):
    """
    Extracts JSON content from a string that may be wrapped in Markdown code blocks.
    
    Args:
        response_content (str): The raw response from the AI.
        
    Returns:
        str: The extracted JSON string.
        
    Raises:
        ValueError: If no JSON content is found in the expected format.
    """
    # Regular expression to match ```json ... ```
    json_block_pattern = r"```json\s*(\{.*?\})\s*```"
    match = re.search(json_block_pattern, response_content, re.DOTALL)
    
    if match:
        json_str = match.group(1).strip()
        return json_str
    else:
        # If not wrapped in code block, assume the entire content is JSON
        # Optionally, you can add more sophisticated checks here
        return response_content.strip()

def add_files_to_stage(files):
    """
    Allows user to select which files to stage, then runs git add on them.
    If Enter is pressed, stages all files. If 'q' is entered, exits the script.
    """
    if not files:
        return
    
    print("\nThese files have changes but are not staged:")
    for i, f in enumerate(files, start=1):
        print(f"[{i}] {f}")
    print("\nEnter the numbers of the files you want to stage separated by spaces")
    print("(press Enter to stage all, or 'q' to quit):")
    choice = input().strip()
    
    if choice.lower() == 'q':
        print("Exiting script...")
        exit(0)
    
    if not choice:
        # Stage all files using 'git add .'
        try:
            subprocess.run(["git", "add", "."], check=True)
            print("All files have been staged.")
            return
        except subprocess.CalledProcessError as e:
            print(f"Error staging files: {e}")
            return
    
    try:
        indices = [int(x) for x in choice.split()]
        to_add = [files[i-1] for i in indices if 0 < i <= len(files)]
        if to_add:
            for f in to_add:
                subprocess.run(["git", "add", f], check=True)
            print("Selected files have been staged.")
        else:
            print("No valid files selected. No files were staged.")
    except ValueError:
        print("Invalid input. No files were staged.")

def generate_commit_message(diff):
    """
    Uses OpenAI GPT to generate a structured commit message based on the git diff.
    Returns a JSON object with message, descriptions, impact, and priority.
    """
    if not diff:
        return None

    # Enhanced prompt for better output
    prompt = f"""
You are an assistant tasked with analyzing the provided git diff and generating a JSON-only output.
Analyze the code changes in detail and produce a JSON structure that includes:

- A short, meaningful commit "message" (2-10 words) referencing a component or part of the code changed.
- A "small_description": A brief summary of 1-3 key changes without any markdown or bullet points.
- A "large_description": A detailed explanation of 1-5 changes without any markdown or bullet points.
- "file_changes": A list of changed files with brief notes on what was changed, without markdown or bullet points.
- "issue": A list of issues fixed, including issue numbers and simple explanations, without markdown or bullet points.
- "solution": A list of solutions implemented, including solution numbers and plain language explanations, without markdown or bullet points.
- "impact": A number between 1-5 indicating the impact of the commit.
- "priority": A number between 1-5 indicating the priority of the commit.

**Important Instructions:**

- **Return ONLY valid JSON**, with no additional text, markdown, or formatting outside of the JSON structure.
- **All string fields should be plain text** without any markdown syntax (e.g., no `- ` bullet points, no `**bold**`).
- **Use arrays** for fields that represent lists (e.g., "small_description", "file_changes", "issue", "solution") instead of single strings with bullet points.

**JSON Structure:**
{{
    "message": "...",
    "small_description": ["...", "..."],
    "large_description": ["...", "..."],
    "file_changes": ["...", "..."],
    "issue": ["...", "..."],
    "solution": ["...", "..."],
    "impact": ...,
    "priority": ...
}}

Git Diff:
{diff}
"""

    # Using ChatCompletion API with more explicit instructions
    try:
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a JSON-only response bot. Return valid JSON with no additional text or formatting."},
                {"role": "user", "content": prompt}
            ]
        )
        print(response.choices[0].message.content.strip())
        # Access the message content correctly
        content = response.choices[0].message.content.strip()
        
        # Extract JSON from the response
        json_str = extract_json_from_response(content)

        # Parse the JSON string
        commit_info = json.loads(json_str)

        # Validation Checks
        required_fields = {
            "message": str,
            "small_description": list,
            "large_description": list,
            "file_changes": list,
            "issue": list,
            "solution": list,
            "impact": int,
            "priority": int
        }

        for field, field_type in required_fields.items():
            if field not in commit_info:
                print(f"Missing field in response: {field}")
                return None
            if not isinstance(commit_info[field], field_type):
                print(f"Incorrect type for field '{field}'. Expected {field_type.__name__}.")
                return None

        # Further validation for 'impact' and 'priority' ranges
        if not (1 <= commit_info["impact"] <= 5):
            print("Invalid value for 'impact'. It should be between 1 and 5.")
            return None
        if not (1 <= commit_info["priority"] <= 5):
            print("Invalid value for 'priority'. It should be between 1 and 5.")
            return None

        return commit_info

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return None
    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

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

def main():
    print("Checking for staged changes...")
    git_diff = get_staged_diff()
    if not git_diff:
        # No staged changes, let user add them
        unstaged = get_unstaged_changes()
        if not unstaged:
            print("No unstaged changes found. Nothing to commit.")
            return
        else:
            print("No staged changes found.")
            add_files_to_stage(unstaged)
            # Check again after adding
            git_diff = get_staged_diff()
            if not git_diff:
                print("Still no staged changes. Exiting.")
                return
    
    print("Generating commit information from AI...")
    commit_info = generate_commit_message(git_diff)
    
    if commit_info:
        # Validate the commit_info structure
        if not validate_commit_info(commit_info):
            print("Commit information is invalid. Exiting.")
            return
        
        print("\nAI-Generated Commit Information:")
        print(f"Message: {commit_info['message']}")
        print(f"\nBrief Description:\n{commit_info['small_description']}")
        print(f"\nDetailed Description:\n{commit_info['large_description']}")
        print(f"\nImpact: {commit_info['impact']}/5")
        print(f"Priority: {commit_info['priority']}/5")
        print(f"\nFile Changes:\n{commit_info['file_changes']}")
        print(f"\nIssue:\n{commit_info['issue']}")
        print(f"\nSolution:\n{commit_info['solution']}")

        # Ask user for Jira ticket number
        print("\nDo you have an existing Jira ticket number to associate with this commit?")
        print("(leave blank if no, or enter 'q' to quit):")
        jira_ticket = input().strip()

        if jira_ticket.lower() == 'q':
            print("Exiting script...")
            exit(0)

        if jira_ticket:
            # Append ticket to commit message
            commit_info['message'] = f"{commit_info['message']} [{jira_ticket}]"
            print(f"Appending Jira ticket {jira_ticket} to commit message.")
            update_jira_issue(jira_ticket, commit_info)
        else:
            # No ticket provided
            print("No Jira ticket provided. Do you want to create a new ticket? (yes/no/quit)")
            choice = input().strip().lower()
            if choice == 'quit' or choice == 'q':
                print("Exiting script...")
                exit(0)
            if choice == 'yes':
                print(f"Creating new Jira ticket in project {JIRA_PROJECT_KEY}...")
                new_issue_key = create_jira_issue(commit_info, JIRA_PROJECT_KEY)
                if new_issue_key:
                    commit_info['message'] = f"{commit_info['message']} [{new_issue_key}]"
                    print(f"Appended newly created Jira issue {new_issue_key} to commit message.")

        # Ask user if they want to commit
        print("\nDo you want to use this commit message and commit now? (yes/no/quit):")
        user_choice = input().strip().lower()
        if user_choice in ['quit', 'q']:
            print("Exiting script...")
            exit(0)
        if user_choice == "yes":
            try:
                # Include a short summary line referencing impact & priority at start of message
                full_commit_message = f"{commit_info['message']}\n\n" \
                                      f"{commit_info['small_description']}\n\n" \
                                      f"{commit_info['large_description']}\n\n" \
                                      f"Impact: {commit_info['impact']}/5\n" \
                                      f"Priority: {commit_info['priority']}/5\n\n" \
                                      f"Files changed:\n{commit_info['file_changes']}\n\n" \
                                      f"Issue:\n{commit_info['issue']}\n\n" \
                                      f"Solution:\n{commit_info['solution']}"

                subprocess.run(["git", "commit", "-m", full_commit_message], check=True)
                print("Changes committed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error committing changes: {e}")
        else:
            print("Commit message discarded.")
    else:
        print("Failed to generate commit information.")

if __name__ == "__main__":
    main()