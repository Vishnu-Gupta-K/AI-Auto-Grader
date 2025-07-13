# AI Auto Grader

An intelligent system for automatically grading written answers using natural language processing and machine learning techniques. The system evaluates student responses against teacher-provided rubrics, keywords, and concepts while maintaining consistency and providing constructive feedback.

## Features

- Automated grading of written answers using NLP and semantic analysis
- Keyword and concept detection with partial credit support
- Customizable rubrics and grading criteria
- Teacher override system for manual grade adjustments
- Detailed feedback generation for student improvement
- Progress tracking and performance analytics
- Support for multiple subjects and question types

## System Requirements

- Python 3.8 or higher
- Required packages listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd llm-auto-grader
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download required NLP models:
```bash
python -m spacy download en_core_web_sm
```

## Usage

### Starting the Server

```bash
python app.py
```

The server will start at `http://localhost:8000`

### API Endpoints

- `POST /grade/`: Submit an answer for grading
- `GET /health`: Check server health status

### Teacher Interface

The `TeacherInterface` class provides methods for:
- Managing questions and rubrics
- Reviewing and overriding grades
- Importing/exporting questions
- Tracking student performance

```python
from teacher_interface import TeacherInterface

teacher = TeacherInterface()
# Add a new question
teacher.add_question(question)
# Override a grade
teacher.add_override(override)
```

### Student Interface

The `StudentInterface` class handles:
- Answer submissions
- Progress tracking
- Performance analytics
- Feedback access

```python
from student_interface import StudentInterface

student = StudentInterface()
# Submit an answer
student.submit_answer(answer)
# View progress
student.get_student_progress(student_id)
```

## Project Structure

```
llm-auto-grader/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Project dependencies
├── teacher_interface.py   # Teacher management module
├── student_interface.py   # Student interaction module
└── data/                 # Data storage directory
    ├── questions.json     # Question bank storage
    ├── submissions.json   # Student submissions
    ├── grading_overrides.json  # Teacher overrides
    └── student_progress.json   # Progress tracking
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with FastAPI
- Uses Hugging Face Transformers for NLP
- Powered by spaCy for text processing