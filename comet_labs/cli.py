import sys
from .utils import get_staged_diff, get_unstaged_changes, add_files_to_stage
from .ai_helpers import (generate_commit_message, validate_commit_info,
    wrapper_generate_commit_message)
from .jira import update_jira_issue, create_jira_issue
from dotenv import load_dotenv, set_key
import argparse
import subprocess
import time
from datetime import datetime


# Load environment variables from .env
load_dotenv()

# Constants
ENV_FILE = ".env"
DEFAULT_AI_KEY = "free-ai-key"  # Placeholder for free AI usage


def print_comet():
    """
    Animates a beautiful ASCII comet flying across the screen.
    """
    comet_frames = [
        "                       ☄️                     ",
        "                    ☄️                        ",
        "                 ☄️                           ",
        "              ☄️                              ",
        "           ☄️                                 ",
        "        ☄️                                    ",
        "     ☄️                                       ",
        "  ☄️                                          ",
        "☄️                                             ",
        "  ☄️                                          ",
        "     ☄️                                       ",
        "        ☄️                                    ",
        "           ☄️                                 ",
        "              ☄️                              ",
        "                 ☄️                           ",
        "                    ☄️                        ",
        "                       ☄️                     ",
        "                          ✨                  ",
        "                             🌟               ",
        "🌌 Welcome to Comet-Labs CLI! 🌌"
    ]

    # Loop through frames
    for frame in comet_frames[:-1]:
        print(f"\r{frame}", end="", flush=True)
        time.sleep(0.15)  # Control animation speed

    # Final welcome frame
    print(f"\r{comet_frames[-1]}\n", flush=True)

def print_banner():
    """
    Prints the welcome banner with a timestamp and project details.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=" * 60)
    # print("🌌  Welcome to **Comet-Labs CLI**  🌌")
    time.sleep(0.3)  # Short pause after welcome
    print("🚀 Smarter commits, powered by AI and designed for you.")
    time.sleep(0.3)  # Pause after tagline
    print(f"✨ Current Time: {now}")
    time.sleep(0.2)  # Brief pause after time
    print("\n📢 **Open-Source Project**: Your contributions make us better!")
    time.sleep(0.3)  # Pause after project info
    print("💖 Star us on GitHub and join the community.")
    time.sleep(1.5)  # Final pause
    print("=" * 60)


def show_credits():
    """
    Displays a heartfelt dedication and project credits.
    """
    print("\n✨🌌 **Comet-Labs CLI Credits** 🌌✨")
    time.sleep(1)
    print("=" * 60)
    print("This project was built with love, code, and a little stardust. 💫")
    print("💖 Dedicated to Drishty, the brightest star in my universe. 💖")
    print("=" * 60)
    time.sleep(2)
    print("\nSpecial thanks to:")
    print("- 🧑‍💻 Open-source contributors who made this project possible.")
    print("- 📚 The amazing developer community for their invaluable resources.")
    print("- 🌍 Users like you who believe in smarter commits and better code!")
    print("\n✨ Keep shining, keep coding! ✨")
    print("\n🌟 Happy committing with Comet-Labs! 🌟\n")

def initialize():
    """
    Initializes the package by configuring OpenAI API key, Jira credentials, and setting up required resources.
    """

    # Animation and Welcome Sequence
    print("\nInitializing...")
    print_comet()
    print_banner()

    print("\n🔑 **Why Use Comet-Labs?**")
    print("- 🚀 Automate your commit messages with AI-powered insights.")
    print("- 📘 Link your Jira tickets effortlessly for better tracking.")
    print("- 🧠 Offline NLP fallback for lightweight usage.")
    print("\n💡 Let's get you set up in just a few steps!")
    time.sleep(1)

    # OpenAI API Key Configuration
    print("\n--- OpenAI API Key Configuration ---")
    print("🔐 To unlock the **full potential** of Comet-Labs, provide your OpenAI API key.")
    print("   Don’t worry—we value your privacy and do not store your key.")
    print("   No key? No problem! We’ll use the free AI fallback (but it’s limited).")
    time.sleep(1)
    openai_key = input("\nEnter your OpenAI API key (or press Enter to use the free version): ").strip()

    if not openai_key:
        openai_key = "free-ai-key"  # Fallback to free version
        print("\n⚠️  No API key provided. Using free AI version. Note: Results may be limited.")
    else:
        print("\n✅ Awesome! Your OpenAI API key is set. Let’s create smarter commits together!")

    # Save the OpenAI API key
    set_key(".env", "OPENAI_API_KEY", openai_key)
    time.sleep(0.5)
    # Jira Integration
    print("\n--- Jira Integration Configuration ---")
    print("🔗 **Optional:** Connect your Jira account to link commit messages with tickets.")
    print("   (This helps you track work better and saves you time!)")
    time.sleep(0.5)
    use_jira = input("\nWould you like to enable Jira integration? (yes/no): ").strip().lower()

    if use_jira in ["yes", "y"]:
        jira_url = input("Enter your Jira base URL (e.g., https://yourdomain.atlassian.net): ").strip()
        jira_username = input("Enter your Jira username or email: ").strip()
        jira_token = input("Enter your Jira API token: ").strip()

        if jira_url and jira_username and jira_token:
            set_key(".env", "JIRA_BASE_URL", jira_url)
            set_key(".env", "JIRA_USERNAME", jira_username)
            set_key(".env", "JIRA_API_TOKEN", jira_token)
            print("\n✅ Jira integration is live! 🎉 You’re all set to link commits with tickets.")
        else:
            print("\n⚠️  Looks like some Jira details are missing. Jira integration is disabled for now.")
    else:
        print("❌ Jira integration skipped. You can enable it later by re-running the initialization.")

    # TextBlob Corpora Setup
    print("\n--- Setting up NLP resources ---")
    print("🧠 Ensuring required NLP libraries are ready for offline commit message generation...")
    try:
        subprocess.run(["python", "-m", "textblob.download_corpora"], check=True)
        print("✅ TextBlob corpora downloaded successfully.")
    except Exception as e:
        print(f"⚠️  Failed to download TextBlob corpora. You can manually run:\npython -m textblob.download_corpora\nError: {e}")

    # Final Message
    print("\n🎉 **Initialization Complete!** 🎉")
    print("✨ What’s next?")
    print("- Run `comet-labs run` to generate AI-powered commit messages.")
    print("- Use `comet-labs --help` for more commands.")
    print("\n🌟 Thank you for choosing Comet-Labs! Happy coding and smarter commits ahead! 🌟\n")


def run():
    """
    Runs the main package functionality for generating commit messages and handling Jira integration.
    """
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
    
    commit_info = wrapper_generate_commit_message(git_diff)

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
        print("Failed to generate commit information.")


def main():
    parser = argparse.ArgumentParser(description="Comet-Labs CLI for AI-driven commit messages and Jira integration.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Initialize command
    subparsers.add_parser("initialize", help="Initialize the package configuration")

    # Run command
    subparsers.add_parser("run", help="Run the main functionality")

    # Credits command
    subparsers.add_parser("credits", help="Show project credits")

    args = parser.parse_args()

    if args.command == "initialize":
        initialize()
    elif args.command == "run":
        run()
    elif args.command == "credits":
        show_credits()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()