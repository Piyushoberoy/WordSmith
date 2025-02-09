import google.generativeai as genai
import json
import os
import re
from .models import Word  # Import the Django model

# Use an environment variable for API key
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("ERROR: API key is missing. Set GOOGLE_API_KEY in environment variables.")
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
    print("Cleaning JSON response...")
    cleaned_text = re.sub(r"```json\n(.*?)\n```", r"\1", response_text, flags=re.DOTALL).strip()
    return cleaned_text


def get_word_details_from_db(word):
    """
    Fetches word details from the database and converts synonyms/antonyms into lists.

    Args:
        word (str): The word to look up.

    Returns:
        tuple: (meaning, synonyms, antonyms, example)
    """
    print(f"Fetching details for word: {word}")
    try:
        word_entry = Word.objects.get(word=word)
        print("Word found in database.")

        meaning = word_entry.meaning or "No meaning found."
        synonyms = word_entry.synonyms.split(",") if word_entry.synonyms else []
        antonyms = word_entry.antonyms.split(",") if word_entry.antonyms else []
        example = word_entry.example or "No example available."

        # Strip whitespace from each synonym and antonym
        synonyms = [s.strip() for s in synonyms]
        antonyms = [a.strip() for a in antonyms]

        print(f"Meaning: {meaning}")
        print(f"Synonyms: {synonyms}")
        print(f"Antonyms: {antonyms}")
        print(f"Example: {example}")

        return meaning, synonyms, antonyms, example

    except Word.DoesNotExist:
        print("WARNING: Word not found in the database.")
        return None, [], [], ""


def generate_mcq(word):
    """
    Generates a multiple-choice question (MCQ) based on the given word.

    Args:
        word (str): The word for which the MCQ should be generated.

    Returns:
        tuple: MCQ containing question, options, and the correct answer.
    """
    print(f"Generating MCQ for word: {word}")
    meaning, synonyms, antonyms, example = get_word_details_from_db(word)

    if not synonyms:
        print("ERROR: Insufficient data to generate MCQ.")
        return {"error": "Insufficient data to generate MCQ."}

    prompt = f"""
    Generate 10 unique MCQs for word "{word}" with details "{synonyms, antonyms, example}", with three incorrect and one correct option, in valid JSON format (without any markdown formatting), where "i" represents mcq number e.g., mcq_1, mcq_2 and so on:
    {{
    "mcq_1": {{
        "question": "What is the meaning of {word}?",
        "option1": "Correct Answer",
        "option2": "Incorrect Answer",
        "option3": "Incorrect Answer",
        "option4": "Incorrect Answer"
    }},
    "mcq_2": {{
        "question": "...",
        "option1": "...",
        "option2": "...",
        "option3": "...",
        "option4": "..."
    }},
    ...
    "mcq_10": {{
        "question": "...",
        "option1": "...",
        "option2": "...",
        "option3": "...",
        "option4": "..."
    }}
    }}
    """
    try:
        print("Sending request to Gemini AI model...")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        print(f"Raw response from model: {response_text}")

        # Clean the response
        cleaned_response = clean_json_response(response_text)

        # Parse JSON response
        mcqs = json.loads(cleaned_response)
        print("List of mcqs--------------->")
        print(mcqs)
        
        mcq_list = []
        # Extract details into variables
        for key, question_details in mcqs.items():
            question = question_details.get("question", "No question found.")
            option1 = question_details.get("option1", "No option")
            option2 = question_details.get("option2", "No option")
            option3 = question_details.get("option3", "No option")
            option4 = question_details.get("option4", "No option")

            mcq = {
                "question": question,
                "options": [option1, option2, option3, option4]  # Storing options as a list
            }

            mcq_list.append(mcq)
            print("MCQ Generated Successfully:")
            print(f"Question: {question}")
            print(f"Option 1 (Correct): {option1}")
            print(f"Option 2: {option2}")
            print(f"Option 3: {option3}")
            print(f"Option 4: {option4}")
        # question = question_details.get("question", "No question found.")
        # option1 = question_details.get("option1", "No option")
        # option2 = question_details.get("option2", "No option")
        # option3 = question_details.get("option3", "No option")
        # option4 = question_details.get("option4", "No option")
        return mcq_list

    except json.JSONDecodeError:
        print("ERROR: Response is not in valid JSON format.")
        print(f"Response received: {response_text}")
        return "Error retrieving details.", [], [], ""

    except Exception as e:
        print(f"ERROR: {e}")
        return "Error retrieving details.", [], [], ""

