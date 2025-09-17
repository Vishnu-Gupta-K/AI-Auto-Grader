# AI AUTO GRADER

A Python application where teachers can create questions, students can submit answers, and a large language model (LLM) evaluates and provides feedback on those answers.

## Features

- **Teacher Mode**:
  - Create new questions with optional expected answers and grading criteria
  - View all created questions
  - Review student submissions and LLM evaluations

- **Student Mode**:
  - View available questions
  - Submit answers to questions
  - Receive immediate LLM-based evaluation and feedback
  - Review past submissions

- **LLM Evaluation**:
  - Automatic evaluation of student answers
  - Detailed feedback on strengths and areas for improvement
  - Scoring on a 0-100 scale

## Setup

1. Clone this repository
    ```
    git clone "https://github.com/Vishnu-Gupta-K/AI-Auto-Grader"
    ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up your Google Gemini API key:
   - Copy `.env.example` to `.env`
   - Add your Gemini API key to the `.env` file

## Usage

Run the application:
```
python main.py
```

Follow the on-screen prompts to navigate between Teacher and Student modes.

### Teacher Mode

1. Create questions by providing subject, topic, and question text
2. Optionally provide expected answers and grading criteria
3. View all questions and their details
4. Review student submissions and LLM evaluations

### Student Mode

1. Browse available questions
2. Submit answers to questions
3. Receive immediate feedback and evaluation from the LLM
4. Review your past submissions and evaluations

## Demo Mode

If no Gemini API key is provided, the application will run in demo mode with simulated evaluations based on answer length.

## Requirements

- Python 3.6+
- Google Gemini API key (for full functionality)
- Required packages listed in requirements.txt

## Data Storage

All data is stored locally in JSON files:
- Questions are stored in `data/questions/`
- Student submissions are stored in `data/submissions/`
