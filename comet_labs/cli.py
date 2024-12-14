import sys
from .utils import get_staged_diff, get_unstaged_changes, add_files_to_stage
from .ai_helpers import generate_commit_message, validate_commit_info
from .jira import update_jira_issue, create_jira_issue
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def main():
    print("Checking for staged changes...")
    git_diff = get_staged_diff()
    if not git_diff:
        unstaged = get_unstaged_changes()
        if not unstaged:
            print("No unstaged changes found. Nothing to commit.")
            sys.exit(0)
        else:
            add_files_to_stage(unstaged)
            git_diff = get_staged_diff()
            if not git_diff:
                print("Still no staged changes. Exiting.")
                sys.exit(0)

    print("Generating commit information from AI...")
    commit_info = generate_commit_message(git_diff)

    if commit_info:
        if not validate_commit_info(commit_info):
            print("Commit information is invalid. Exiting.")
            sys.exit(1)

        print("\nAI-Generated Commit Information:")
        print(f"Message: {commit_info['message']}")
        print(f"\nBrief Description:\n{commit_info['small_description']}")
        print(f"\nDetailed Description:\n{commit_info['large_description']}")
        print(f"\nImpact: {commit_info['impact']}/5")
        print(f"Priority: {commit_info['priority']}/5")
        print(f"\nFile Changes:\n{commit_info['file_changes']}")
        print(f"\nIssue:\n{commit_info['issue']}")
        print(f"\nSolution:\n{commit_info['solution']}")

        print("\nDo you have an existing Jira ticket number to associate with this commit?")
        print("(leave blank if no, or enter 'q' to quit):")
        jira_ticket = input().strip()

        if jira_ticket.lower() == 'q':
            print("Exiting script...")
            sys.exit(0)

        if jira_ticket:
            commit_info['message'] = f"{commit_info['message']} [{jira_ticket}]"
            update_jira_issue(jira_ticket, commit_info)
        else:
            print("No Jira ticket provided. Do you want to create a new ticket? (yes/no/quit)")
            choice = input().strip().lower()
            if choice in ['quit', 'q']:
                print("Exiting script...")
                sys.exit(0)
            if choice == 'yes':
                new_issue_key = create_jira_issue(commit_info)
                if new_issue_key:
                    commit_info['message'] = f"{commit_info['message']} [{new_issue_key}]"

        print("\nDo you want to commit now? (yes/no/quit):")
        choice = input().strip().lower()
        if choice in ['quit', 'q']:
            print("Exiting script...")
            sys.exit(0)
        if choice == 'yes':
            print("Committing changes...")
            # Commit logic here
    else:
        print("Failed to generate commit information.")
