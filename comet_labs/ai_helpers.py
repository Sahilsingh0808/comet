import openai
import json
import re


def extract_json_from_response(content):
    match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
    return match.group(1).strip() if match else content.strip()


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

def validate_commit_info(commit_info):
    required_fields = {"message": str, "small_description": list, "large_description": list, "file_changes": list}
    return all(isinstance(commit_info.get(key), expected) for key, expected in required_fields.items())
