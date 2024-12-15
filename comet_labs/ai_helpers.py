import dotenv
import openai
import json
import requests
import re
from .prompts import generate_prompt_xml
from pathlib import Path
from dotenv import load_dotenv, get_key
from textblob import TextBlob
import nltk
import sys
import os

def download_nltk_data_quietly(package):
    """
    Downloads NLTK data without showing logs.
    """
    original_stdout = sys.stdout  # Save original stdout
    original_stderr = sys.stderr  # Save original stderr
    sys.stdout = open(os.devnull, 'w')  # Redirect stdout to null
    sys.stderr = open(os.devnull, 'w')  # Redirect stderr to null
    try:
        nltk.download(package, quiet=True)
    finally:
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = original_stdout  # Restore original stdout
        sys.stderr = original_stderr  # Restore original stderr

download_nltk_data_quietly("punkt")

# Define the path to your .env file
ENV_FILE = str(Path(__file__).parent.parent / ".env")

# Load environment variables from .env
load_dotenv(ENV_FILE)

def extract_json_from_response(content):
    match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
    return match.group(1).strip() if match else content.strip()

def extract_key_diff_info(diff):
    """
    Extracts key information from a git diff, including file names and meaningful changes.
    """
    import re

    # Extract file names
    changed_files = re.findall(r'diff --git a/(.+?) b/', diff)

    # Extract meaningful added/removed lines
    meaningful_changes = []
    for line in diff.splitlines():
        if line.startswith('+') and not line.startswith('+++'):
            meaningful_changes.append(line.strip())
        elif line.startswith('-') and not line.startswith('---'):
            meaningful_changes.append(line.strip())

    # Combine extracted information into a single text
    summary = []
    if changed_files:
        summary.append(f"Changed files: {', '.join(changed_files)}")
    if meaningful_changes:
        summary.append("Key changes:")
        summary.extend(meaningful_changes[:50])  # Limit to 50 lines

    return "\n".join(summary)

def summarize_diff_with_textblob(diff):
    """
    Summarizes the extracted diff information using TextBlob.
    """
    # Extract key diff information
    key_diff_info = extract_key_diff_info(diff)

    # Use TextBlob to summarize
    blob = TextBlob(key_diff_info)
    sentences = blob.sentences

    # Select first few sentences as the summary
    summarized_text = " ".join(str(sentence) for sentence in sentences[:5])  # Limit to 5 sentences
    return summarized_text

def extract_key_diff_info(diff):
    """
    Extracts key information from a git diff, including file names and meaningful changes.
    
    Args:
        diff (str): The full git diff.
    
    Returns:
        str: A summarized version of the git diff.
    """
    # Extract file names
    changed_files = re.findall(r'diff --git a/(.+?) b/', diff)

    # Extract meaningful added/removed lines
    meaningful_changes = []
    for line in diff.splitlines():
        if line.startswith('+') and not line.startswith('+++'):  # Added lines
            meaningful_changes.append(line.strip())
        elif line.startswith('-') and not line.startswith('---'):  # Removed lines
            meaningful_changes.append(line.strip())

    # Combine extracted information into a summary
    summary = []
    if changed_files:
        summary.append(f"Changed files: {', '.join(changed_files)}")
    if meaningful_changes:
        summary.append("Key changes:")
        summary.extend(meaningful_changes[:50])  # Limit to first 50 changes to stay concise

    # Return the summarized diff
    return "\n".join(summary)


def truncate_diff(diff, max_tokens=1024):
    """
    Truncates the diff to fit within the token limit.
    
    Args:
        diff (str): The original git diff.
        max_tokens (int): Maximum number of tokens allowed.

    Returns:
        str: Truncated diff.
    """
    # Split the diff into lines and truncate to fit within max tokens
    truncated_diff = "\n".join(diff.splitlines()[:max_tokens // 10])  # Approx. 10 tokens per line
    return truncated_diff


def wrapper_generate_commit_message(diff):
    """
    Wrapper to choose between OpenAI GPT and Free AI for generating commit messages.
    """
    openai_key = get_key(ENV_FILE, "OPENAI_API_KEY")

    if openai_key:
        print("Using OpenAI GPT for generating commit message...")
        return generate_commit_message(diff)
    else:
        print("OpenAI API key not provided. Falling back to free AI.")
        return free_ai_generate_commit_message(diff)
    

def free_ai_generate_commit_message(diff):
    """
    Generates a commit message using a free AI model (GPT-2 via Hugging Face).
    Returns a JSON object with message, descriptions, impact, and priority.
    """
    print("Using free AI version to generate commit message...")
    
    # Truncate the diff
    truncated_diff = truncate_diff(diff)
    
    key_diff_info = extract_key_diff_info(diff)
    summarized_diff = summarize_diff_with_textblob(key_diff_info)

    hugging_face_api_key = get_key(ENV_FILE, "HUGGING_FACE_API_KEY")

    # Hugging Face Inference API URL
    api_url = "https://api-inference.huggingface.co/models/gpt2"

    # You need to use your own Hugging Face token
    headers = {"Authorization": f"Bearer {hugging_face_api_key}"}

    # Prepare the prompt for GPT-2
    prompt = generate_prompt_xml(diff)

    # Attempt to extract the JSON object from the response
    try:
        # Send request to Hugging Face API
        response = requests.post(
            api_url,
            headers=headers,
            json={"inputs": prompt, "parameters": {"max_length": 300, "temperature": 0.7}}
        )

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return fallback_generate_commit_message(diff)

        # Parse response text
        generated_text = response.json()["generated_text"]

        # Extract JSON from the response
        json_start = generated_text.find("{")
        json_end = generated_text.rfind("}")
        if json_start == -1 or json_end == -1:
            raise ValueError("No valid JSON found in the response.")

        json_str = generated_text[json_start:json_end + 1]
        commit_info = json.loads(json_str)

        # Validate the structure
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

        return commit_info

    except Exception as e:
        print(f"Error in free AI function: {e}")
        print("Falling back to TextBlob-based heuristic generation...")
        return fallback_generate_commit_message(diff)

def fallback_generate_commit_message(diff):
    """
    Fallback function to generate commit message JSON using TextBlob NLP.
    """
    try:
        # Extract key information from the diff
        key_diff_info = extract_key_diff_info(diff)
        summarized_diff = summarize_diff_with_textblob(key_diff_info)

        # Analyze the summarized diff with TextBlob
        blob = TextBlob(summarized_diff)

        # Generate the commit message based on sentiment or key phrases
        commit_message = blob.noun_phrases[:1]  # Use the first noun phrase as a base
        commit_message = "Update " + " ".join(commit_message) if commit_message else "Code changes"

        # Generate small and large descriptions
        small_description = [str(sentence) for sentence in blob.sentences[:2]]  # First 2 sentences
        large_description = [str(sentence) for sentence in blob.sentences[:5]]  # First 5 sentences

        # Generate issues and solutions based on text sentiment analysis
        issues = [
            f"Potential issue detected: {str(sentence)}"
            for sentence in blob.sentences if sentence.sentiment.polarity < 0
        ]
        solutions = [
            f"Suggested improvement: {str(sentence)}"
            for sentence in blob.sentences if sentence.sentiment.polarity >= 0
        ]

        # Create a structured JSON response
        commit_info = {
            "message": commit_message,
            "small_description": small_description,
            "large_description": large_description,
            "file_changes": re.findall(r'diff --git a/(.+?) b/', diff),
            "issue": issues[:3],  # Limit to 3 issues
            "solution": solutions[:3],  # Limit to 3 solutions
            "impact": 1,
            "priority": 3
        }
        return commit_info
    except Exception as e:
        print(f"Error in fallback function: {e}")
        # Return a minimal response in case of further errors
        return heuristic_fallback_generate_commit_message(diff)

def heuristic_fallback_generate_commit_message(diff):
    """
    Fallback function to heuristically generate commit message JSON.
    """
    try:
        # Extract filenames from the diff
        file_changes = re.findall(r'diff --git a/(.+?) b/', diff)

        # Extract meaningful changes (added and removed lines)
        meaningful_changes = []
        for line in diff.splitlines():
            if line.startswith('+') and not line.startswith('+++'):  # Added lines
                meaningful_changes.append(f"Added: {line[1:].strip()}")
            elif line.startswith('-') and not line.startswith('---'):  # Removed lines
                meaningful_changes.append(f"Removed: {line[1:].strip()}")

        # Generate a heuristic commit message
        if file_changes:
            commit_message = f"Updated {len(file_changes)} file(s): {', '.join(file_changes[:3])}"
        else:
            commit_message = "Code changes made"

        # Generate small and large descriptions
        small_description = [
            f"Modified files: {', '.join(file_changes[:3])}" if file_changes else "General code updates",
            f"{len(meaningful_changes)} changes detected in the diff"
        ]
        large_description = (
            [f"Modified files: {', '.join(file_changes)}"] +
            meaningful_changes[:10]  # Limit detailed descriptions to the first 10 changes
        )

        # Generate issues and solutions heuristically
        issues = [
            f"Potential issue in: {change}"
            for change in meaningful_changes if "Removed:" in change
        ]
        solutions = [
            f"Implemented change: {change}"
            for change in meaningful_changes if "Added:" in change
        ]

        # Create the final commit_info JSON
        commit_info = {
            "message": commit_message,
            "small_description": small_description[:2],  # Limit to 2 points
            "large_description": large_description[:5],  # Limit to 5 points
            "file_changes": file_changes,
            "issue": issues[:3],  # Limit to 3 issues
            "solution": solutions[:3],  # Limit to 3 solutions
            "impact": 1,
            "priority": 3
        }

        return commit_info

    except Exception as e:
        print(f"Error in heuristic fallback: {e}")
        return None

def generate_commit_message(diff):
    """
    Uses OpenAI GPT to generate a structured commit message based on the git diff.
    Returns a JSON object with message, descriptions, impact, and priority.
    """
    if not diff:
        return None

    # Enhanced prompt for better output
    prompt = generate_prompt_xml(diff)

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

def validate_commit_info(commit_info):
    required_fields = {"message": str, "small_description": list, "large_description": list, "file_changes": list}
    return all(isinstance(commit_info.get(key), expected) for key, expected in required_fields.items())
