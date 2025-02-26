import os
import re
import json
import google.generativeai as genai

# Use an environment variable for API key (Replace with os.getenv if needed)
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("API key is missing. Set GOOGLE_API_KEY in environment variables.")

genai.configure(api_key=API_KEY)

# AVAILABLE_MODELS = [
#     "gemini-pro",
#     "gemini-pro-vision",
#     "gemini-1.5-pro-latest",
#     "gemini-1.5-flash-latest"
# ]
model = genai.GenerativeModel("gemini-1.5-flash-latest")

def clean_json_response(response_text):
    """
    Cleans JSON response by removing markdown-style triple backticks.
    """
    return re.sub(r"```json\n(.*?)\n```", r"\1", response_text, flags=re.DOTALL).strip()

def generate_word_details(word):
    """
    Generates meaning, synonyms, antonyms, and an example sentence for a given word.

    Args:
        word (str): The word to analyze.

    Returns:
        tuple: (meaning, synonyms, antonyms, example)
    """
    prompt = f"""
        You are an educational assistant helping users understand words. Please provide information for the word "{word}" in a safe, educational format, for competetive exams.

        - Meaning: A short, neutral definition.
        - Synonyms: Up to 5 synonyms (if available).
        - Antonyms: Up to 5 antonyms (if available).
        - Example Sentence: A neutral sentence using the word.

        Respond in **pure JSON** format (without markdown or additional text):
        {{
            "meaning": "Definition here",
            "synonyms": ["synonym1", "synonym2", "synonym3"],
            "antonyms": ["antonym1", "antonym2", "antonym3"],
            "example": "A correct usage example."
        }}
    """

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Clean and parse the JSON response
        cleaned_response = clean_json_response(response_text)
        word_details = json.loads(cleaned_response)

        # Extract word details with safe fallbacks
        meaning = word_details.get("meaning", "No meaning found.")
        synonyms = word_details.get("synonyms", [])
        antonyms = word_details.get("antonyms", [])
        example = word_details.get("example", "No example available.")

        print("[INFO] Successfully generated idiom details.")
        return meaning, synonyms, antonyms, example

    except json.JSONDecodeError:
        print("[ERROR] JSON parsing failed. Raw response:", response_text)
        return "Error retrieving details.", [], [], ""

    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        return "Error retrieving details.", [], [], ""

def generate_idiom_details(phrase):
    """
    Generates detailed information for a given idiom.

    Args:
        phrase (str): The idiom to analyze.

    Returns:
        tuple: (meaning, example, insights, category, related_idioms, origin, difficulty_level, tags)
    """
    
    print(f"[INFO] Generating details for idiom: {phrase}")

    prompt = f"""
        You are an advanced language assistant specializing in idioms. Given the idiom "{phrase}", generate detailed information in a structured educational format.

        ### **Requirements:**
        - Provide an accurate **meaning** of the idiom.
        - Generate a **contextually correct example sentence** demonstrating its proper usage.
        - Offer **AI-generated insights** that explain the idiom’s origin, common usage, or interesting facts.
        - Assign **category** (e.g., Business, Everyday Life, Sports, Weather, etc.).
        - Suggest **related idioms** (if applicable).
        - Assign a **difficulty level** based on how commonly the idiom is used:
        - "Beginner" (very common and easy to understand)
        - "Intermediate" (moderate complexity or less common)
        - "Advanced" (rare or complex usage)
        - Generate **tags** that describe the idiom, making it easier to search (e.g., "motivation", "success", "teamwork").

        ### **Response Format:**  
        Respond in **pure JSON format** (no extra text or markdown), like this:

        {{
            "meaning": "A clear and concise definition.",
            "example": "A well-structured sentence using the idiom.",
            "insights": "Historical background or interesting facts about the idiom.",
            "category": "Relevant category of the idiom",
            "related_idioms": ["Similar idiom 1", "Similar idiom 2"],
            "origin": "A brief historical background if available.",
            "difficulty_level": "Beginner/Intermediate/Advanced",
            "tags": ["keyword1", "keyword2", "keyword3"]
        }}
    """

    try:
        print("[INFO] Sending prompt to AI model...")
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        print("[DEBUG] Raw response:", response_text)

        # Clean and parse the JSON response
        cleaned_response = clean_json_response(response_text)
        idiom_details = json.loads(cleaned_response)

        # Extract details with safe fallbacks
        meaning = idiom_details.get("meaning", "No meaning found.")
        example = idiom_details.get("example", "No example available.")
        insights = idiom_details.get("insights", "")
        category = idiom_details.get("category", "General")
        related_idioms = idiom_details.get("related_idioms", [])
        origin = idiom_details.get("origin", "")
        difficulty_level = idiom_details.get("difficulty_level", "Beginner")
        tags = idiom_details.get("tags", [])

        print("[INFO] Successfully generated idiom details.")
        return meaning, example, insights, category, related_idioms, origin, difficulty_level, tags

    except json.JSONDecodeError:
        print("[ERROR] JSON parsing failed. Raw response:", response_text)
        return "Error retrieving details.", "", "", "General", [], "", "Beginner", []

    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        return "Error retrieving details.", "", "", "General", [], "", "Beginner", []