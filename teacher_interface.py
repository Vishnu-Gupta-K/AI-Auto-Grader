from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import os

class RubricItem(BaseModel):
    description: str
    points: float
    keywords: List[str]
    concepts: List[str]

class Question(BaseModel):
    id: str
    text: str
    subject: str
    reference_answer: str
    rubric: Dict[str, RubricItem]
    total_points: float

class GradingOverride(BaseModel):
    question_id: str
    student_id: str
    original_score: float
    override_score: float
    override_reason: str
    override_date: datetime
    teacher_id: str

class TeacherInterface:
    def __init__(self, data_directory: str = "data"):
        self.data_directory = data_directory
        self.questions_file = os.path.join(data_directory, "questions.json")
        self.overrides_file = os.path.join(data_directory, "grading_overrides.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_directory, exist_ok=True)
        
        # Initialize storage files if they don't exist
        if not os.path.exists(self.questions_file):
            self._save_questions({})
        if not os.path.exists(self.overrides_file):
            self._save_overrides([])

    def _load_questions(self) -> Dict[str, Question]:
        try:
            with open(self.questions_file, 'r') as f:
                data = json.load(f)
                return {qid: Question(**q) for qid, q in data.items()}
        except Exception as e:
            print(f"Error loading questions: {e}")
            return {}

    def _save_questions(self, questions: Dict[str, dict]) -> None:
        with open(self.questions_file, 'w') as f:
            json.dump(questions, f, indent=2, default=str)

    def _load_overrides(self) -> List[GradingOverride]:
        try:
            with open(self.overrides_file, 'r') as f:
                data = json.load(f)
                return [GradingOverride(**override) for override in data]
        except Exception as e:
            print(f"Error loading overrides: {e}")
            return []

    def _save_overrides(self, overrides: List[dict]) -> None:
        with open(self.overrides_file, 'w') as f:
            json.dump(overrides, f, indent=2, default=str)

    def add_question(self, question: Question) -> bool:
        questions = self._load_questions()
        if question.id in questions:
            return False
        
        questions[question.id] = question.dict()
        self._save_questions(questions)
        return True

    def update_question(self, question: Question) -> bool:
        questions = self._load_questions()
        if question.id not in questions:
            return False
        
        questions[question.id] = question.dict()
        self._save_questions(questions)
        return True

    def get_question(self, question_id: str) -> Optional[Question]:
        questions = self._load_questions()
        return questions.get(question_id)

    def list_questions(self, subject: Optional[str] = None) -> List[Question]:
        questions = self._load_questions()
        if subject:
            return [q for q in questions.values() if q.subject == subject]
        return list(questions.values())

    def add_override(self, override: GradingOverride) -> bool:
        overrides = self._load_overrides()
        overrides.append(override.dict())
        self._save_overrides(overrides)
        return True

    def get_overrides(self, 
                      question_id: Optional[str] = None, 
                      student_id: Optional[str] = None) -> List[GradingOverride]:
        overrides = self._load_overrides()
        
        if question_id:
            overrides = [o for o in overrides if o.question_id == question_id]
        if student_id:
            overrides = [o for o in overrides if o.student_id == student_id]
            
        return overrides

    def update_rubric(self, 
                      question_id: str, 
                      rubric_updates: Dict[str, RubricItem]) -> bool:
        questions = self._load_questions()
        if question_id not in questions:
            return False
        
        question = questions[question_id]
        question.rubric.update(rubric_updates)
        self._save_questions(questions)
        return True

    def bulk_import_questions(self, questions: List[Question]) -> tuple[int, List[str]]:
        existing_questions = self._load_questions()
        imported_count = 0
        failed_ids = []

        for question in questions:
            if question.id not in existing_questions:
                existing_questions[question.id] = question.dict()
                imported_count += 1
            else:
                failed_ids.append(question.id)

        self._save_questions(existing_questions)
        return imported_count, failed_ids

    def export_questions(self, subject: Optional[str] = None) -> List[Question]:
        return self.list_questions(subject)

    def delete_question(self, question_id: str) -> bool:
        questions = self._load_questions()
        if question_id not in questions:
            return False
        
        del questions[question_id]
        self._save_questions(questions)
        return True