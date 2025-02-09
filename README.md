# WordSmith

## Overview

**WordSmith** is an intelligent dictionary and vocabulary-building application that helps users enhance their language skills. Users can enter words along with their meanings, synonyms, antonyms, and example sentences. If any of these details are missing, WordSmith automatically generates them using AI-powered tools.

The application also creates interactive exercises to reinforce learning, including:

- **Multiple Choice Questions (MCQs)**
- **Multiple Select Questions (MSQs)**
- **Fill-in-the-Blanks**

## Features

- **User Input:** Add new words with optional details.
- **AI Assistance:** Automatically generates missing word details.
- **Quiz Generation:** Creates MCQs, MSQs, and fill-in-the-blank exercises.
- **Search & Filter:** Find words easily with search functionality.
- **User Authentication:** Register and log in to save progress.
- **Admin Panel:** Manage words and quizzes.

## Tech Stack

- **Backend:** Django, Django REST Framework (optional for API integration)
- **Database:** PostgreSQL / MySQL / SQLite
- **Frontend:** Django Templates / React (optional)
- **AI Features:** OpenAI API / WordNet for word generation

## Installation & Setup

### Prerequisites

- Python 3.8+
- Django 4+
- Virtual Environment (Recommended)

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Piyushoberoy/WordSmith.git
   ```
   ```bash
   cd WordSmith
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   ```
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations**

   ```bash
   python manage.py makemigrations
   ```
   ```bash
   python manage.py migrate
   ```

5. **Run Development Server**

   ```bash
   python manage.py runserver
   ```

6. **Access the App** Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Usage

- Navigate to `/dictionary/add/` to add a new word.
- The system will generate missing details automatically.
- Visit `/admin/` for backend management.
- Quizzes are automatically generated for added words.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push to your fork and submit a Pull Request.

## License

This project is licensed under the MIT License.

