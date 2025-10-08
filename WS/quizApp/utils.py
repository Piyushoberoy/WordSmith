import os
import re
import json
from .models import Word, Idiom
import google.generativeai as genai
from django.http import JsonResponse

# Use an environment variable for API key
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("[ERROR] API key is missing. Set GOOGLE_API_KEY in environment variables.")
    raise ValueError("API key is missing. Set GOOGLE_API_KEY in environment variables.")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash-lite")

def clean_json_response(response_text):
    """Removes markdown-style triple backticks from JSON response."""
    print("[INFO] Cleaning JSON response...")
    return re.sub(r"```json\n(.*?)\n```", r"\1", response_text, flags=re.DOTALL).strip()

def get_word_details_from_db(word):
    """
    Fetches word details from the database, ensuring synonyms/antonyms are processed correctly.

    Args:
        word (str): The word to look up.

    Returns:
        tuple: (meaning, synonyms, antonyms, example)
    """
    print(f"[INFO] Fetching details for word: '{word}'...")

    try:
        # Fetch only required fields to optimize query
        word_entry = Word.objects.only("meaning", "synonyms", "antonyms", "example").get(word=word)
        print("[INFO] Word found in database.")

        # Extract details with safe defaults
        meaning = word_entry.meaning or "No meaning found."
        synonyms = word_entry.synonyms.split(",") if word_entry.synonyms else []
        antonyms = word_entry.antonyms.split(",") if word_entry.antonyms else []
        example = word_entry.example or "No example available."

        # Clean and filter out empty strings
        synonyms = [s.strip() for s in synonyms if s.strip()]
        antonyms = [a.strip() for a in antonyms if a.strip()]

        print(f"[DEBUG] Meaning: {meaning}")
        print(f"[DEBUG] Synonyms: {synonyms}")
        print(f"[DEBUG] Antonyms: {antonyms}")
        print(f"[DEBUG] Example: {example}")

        return meaning, synonyms, antonyms, example

    except Word.DoesNotExist:
        print("[WARNING] Word not found in the database.")
        return None, [], [], ""

    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        return None, [], [], ""

def generate_mcq(word):
    """
    Generates multiple-choice questions (MCQs) for a given word.

    Args:
        word (str): The word for which MCQs should be generated.

    Returns:
        dict: A dictionary of MCQs following the structure:
        {
            "mcq_1": {
                "question": "...",
                "option1": "...",  # Correct answer
                "option2": "...",  # Incorrect answer
                "option3": "...",  # Incorrect answer
                "option4": "...",  # Incorrect answer
            },
            ...
        }
    """
    print(f"[INFO] Generating MCQs for word: '{word}'...")

    # Fetch word details from the database
    meaning, synonyms, antonyms, example = get_word_details_from_db(word)

    if not synonyms:
        print("[ERROR] Insufficient data to generate MCQs.")
        return {"error": "Insufficient data to generate MCQs."}

    # Format prompt for AI
    prompt = f"""
    You are an expert MCQ generator. Create **10 unique multiple-choice questions** (MCQs) for the word "{word}" using:

    - **Synonyms**: {synonyms}
    - **Antonyms**: {antonyms}
    - **Example Sentence**: {example}

    ### **MCQ Structure:**
    - Each MCQ must have **one correct answer** (option1).
    - The other three options (option2, option3, option4) must be **incorrect but reasonable**.
    - The response must be **valid JSON** (no markdown or extra text).

    ### **Response Format:**
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
        print("[INFO] Sending request to AI model...")
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        print(f"[DEBUG] Raw AI response: {response_text}")

        # Clean JSON response (removing markdown-style formatting)
        cleaned_response = clean_json_response(response_text)

        # Parse JSON response
        mcqs = json.loads(cleaned_response)
        print("[INFO] Successfully parsed AI response.")

        # Validate MCQs
        valid_mcqs = []
        for key, question_details in mcqs.items():
            question = question_details.get("question", "No question available.")
            option1 = question_details.get("option1", "No option")
            option2 = question_details.get("option2", "No option")
            option3 = question_details.get("option3", "No option")
            option4 = question_details.get("option4", "No option")

            # Ensure all four options exist
            if not all([option1, option2, option3, option4]):
                print(f"[WARNING] Invalid MCQ format in {key}. Skipping...")
                continue
            
            mcq = {
                "question": question,
                "options": [option1, option2, option3, option4]
            }
            
            valid_mcqs.append(mcq)

            print(f"[INFO] ✅ MCQ {key} Generated Successfully:")
            print(f"  🔹 Question: {question}")
            print(f"  🔹 Option 1 (Correct): {option1}")
            print(f"  🔹 Option 2: {option2}")
            print(f"  🔹 Option 3: {option3}")
            print(f"  🔹 Option 4: {option4}")

        return valid_mcqs

    except json.JSONDecodeError:
        print("[ERROR] AI response is not in valid JSON format.")
        print(f"[DEBUG] Response received: {response_text}")
        # return {"error": "Invalid AI response format."}
        return []

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return []
        # return {"error": str(e)}

def get_idiom_details_from_db(phrase):
    """
    Fetches idiom details from the database and processes related idioms and tags into lists.

    Args:
        phrase (str): The idiom to look up.

    Returns:
        tuple: (meaning, example, insights, category, related_idioms, origin, difficulty_level, tags)
    """
    print(f"[INFO] Fetching details for idiom: '{phrase}'")

    try:
        idiom_entry = Idiom.objects.get(phrase=phrase)
        print(f"[SUCCESS] Idiom found in database: {idiom_entry}")

        meaning = idiom_entry.meaning or "No meaning found."
        example = idiom_entry.example or "No example available."
        insights = idiom_entry.insights or ""
        category = idiom_entry.category or "General"
        
        related_idioms = idiom_entry.related_idioms.split(",") if idiom_entry.related_idioms else []
        related_idioms = [idiom.strip() for idiom in related_idioms]  # Remove whitespace
        
        origin = idiom_entry.origin or ""
        difficulty_level = idiom_entry.difficulty_level or "Beginner"
        tags = idiom_entry.tags.split(",") if idiom_entry.tags else []
        tags = [tag.strip() for tag in tags]  # Remove whitespace

        # Logging details
        print(f"[DEBUG] Meaning: {meaning}")
        print(f"[DEBUG] Example: {example}")
        print(f"[DEBUG] Insights: {insights}")
        print(f"[DEBUG] Category: {category}")
        print(f"[DEBUG] Related Idioms: {related_idioms}")
        print(f"[DEBUG] Origin: {origin}")
        print(f"[DEBUG] Difficulty Level: {difficulty_level}")
        print(f"[DEBUG] Tags: {tags}")

        return meaning, example, insights, category, related_idioms, origin, difficulty_level, tags

    except Idiom.DoesNotExist:
        print(f"[WARNING] Idiom '{phrase}' not found in the database.")
        return None, "", "", "General", [], "", "Beginner", []

def generate_idiom_mcq(phrase):
    """
    Generates multiple-choice questions (MCQs) for a given idiom.

    Args:
        phrase (str): The idiom for which the MCQs should be generated.

    Returns:
        list: A list of MCQs containing question, options, and correct answers.
    """
    print(f"[INFO] Generating MCQs for idiom: '{phrase}'")

    # Fetch idiom details
    meaning, example, insights, category, related_idioms, origin, difficulty_level, tags = get_idiom_details_from_db(phrase)

    if meaning is None:
        print("[ERROR] Insufficient data to generate MCQs.")
        return {"error": "Insufficient data to generate MCQs."}

    # Prompt for AI model
    prompt = f"""
    Generate 10 unique MCQs for the idiom "{phrase}" with details:
    - Meaning: "{meaning}"
    - Example: "{example}"
    - Insights: "{insights}"
    - Origin: "{origin}"
    - Difficulty Level: "{difficulty_level}"
    - Tags: "{tags}"
    - Related Idioms: "{related_idioms}"

    Each MCQ should have:
    - A well-structured question
    - Three incorrect options
    - One correct option
    - Ensure JSON format is valid and does not contain markdown.

    Respond in JSON format like this:
    {{
        "mcq_1": {{
            "question": "What does the idiom '{phrase}' mean?",
            "option1": "Correct Answer",
            "option2": "Incorrect Answer",
            "option3": "Incorrect Answer",
            "option4": "Incorrect Answer"
        }},
        "mcq_2": {{ ... }},
        "mcq_10": {{ ... }}
    }}
    """

    try:
        print("[INFO] Sending request to AI model...")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        print(f"[SUCCESS] Raw response received: {response_text}")

        # Clean and parse JSON response
        cleaned_response = clean_json_response(response_text)
        mcqs = json.loads(cleaned_response)

        mcq_list = []
        for i, (key, question_details) in enumerate(mcqs.items(), start=1):
            mcq = {
                "question": question_details.get("question", "No question found."),
                "options": [
                    question_details.get("option1", "No option"),
                    question_details.get("option2", "No option"),
                    question_details.get("option3", "No option"),
                    question_details.get("option4", "No option")
                ]
            }
            mcq_list.append(mcq)

            # Debugging output
            print(f"[DEBUG] MCQ-{i} Generated Successfully")

        return mcq_list

    except json.JSONDecodeError:
        print("[ERROR] Response is not in valid JSON format.")
        print(f"[DEBUG] Response received: {response_text}")
        return {"error": "Invalid response format."}

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return {"error": str(e)}
