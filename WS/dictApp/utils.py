import google.generativeai as genai
import json
import os
import re

# Use an environment variable for API key (Replace with os.getenv if needed)
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("API key is missing. Set GOOGLE_API_KEY in environment variables.")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-pro")

def clean_json_response(response_text):
    """
    Cleans JSON response by removing markdown-style triple backticks.
    """
    cleaned_text = re.sub(r"```json\n(.*?)\n```", r"\1", response_text, flags=re.DOTALL).strip()
    return cleaned_text

def generate_word_details(word):
    """
    Generate meaning, synonyms, antonyms, and an example sentence for a given word.

    Args:
        word (str): The word to analyze.

    Returns:
        tuple: (meaning, synonyms, antonyms, example)
    """
    prompt = f"""
    Provide the following details for the word "{word}" in valid JSON format (without any markdown formatting):
    {{
        "meaning": "A concise definition of the word.",
        "synonyms": ["synonym1", "synonym2", "synonym3", "synonym4", "synonym5"],
        "antonyms": ["antonym1", "antonym2", "antonym3", "antonym4", "antonym5"],
        "example": "A sentence using the word correctly."
    }}
    """

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Clean the response
        cleaned_response = clean_json_response(response_text)

        # Parse JSON response
        word_details = json.loads(cleaned_response)

        # Extract details into variables
        meaning = word_details.get("meaning", "No meaning found.")
        synonyms = word_details.get("synonyms", [])
        antonyms = word_details.get("antonyms", [])
        print(antonyms)
        example = word_details.get("example", "No example available.")

        return meaning, synonyms, antonyms, example

    except json.JSONDecodeError:
        print("Error: Response is not in valid JSON format.")
        print("Response received:", response_text)
        return "Error retrieving details.", [], [], ""

    except Exception as e:
        print("Error:", e)
        return "Error retrieving details.", [], [], ""

