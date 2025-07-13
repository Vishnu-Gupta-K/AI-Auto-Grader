from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import os

class SubmittedAnswer(BaseModel):
    question_id: str
    student_id: str
    answer_text: str
    submission_time: datetime
    score: Optional[float] = None
    feedback: Optional[str] = None
    graded: bool = False

class StudentProgress(BaseModel):
    student_id: str
    completed_questions: List[str]
    average_score: float
    improvement_areas: List[str]

class StudentInterface:
    def __init__(self, data_directory: str = "data"):
        self.data_directory = data_directory
        self.submissions_file = os.path.join(data_directory, "submissions.json")
        self.progress_file = os.path.join(data_directory, "student_progress.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_directory, exist_ok=True)
        
        # Initialize storage files if they don't exist
        if not os.path.exists(self.submissions_file):
            self._save_submissions([])
        if not os.path.exists(self.progress_file):
            self._save_progress({})

    def _load_submissions(self) -> List[SubmittedAnswer]:
        try:
            with open(self.submissions_file, 'r') as f:
                data = json.load(f)
                return [SubmittedAnswer(**submission) for submission in data]
        except Exception as e:
            print(f"Error loading submissions: {e}")
            return []

    def _save_submissions(self, submissions: List[dict]) -> None:
        with open(self.submissions_file, 'w') as f:
            json.dump(submissions, f, indent=2, default=str)

    def _load_progress(self) -> Dict[str, StudentProgress]:
        try:
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                return {sid: StudentProgress(**progress) for sid, progress in data.items()}
        except Exception as e:
            print(f"Error loading progress: {e}")
            return {}

    def _save_progress(self, progress: Dict[str, dict]) -> None:
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2, default=str)

    def submit_answer(self, answer: SubmittedAnswer) -> bool:
        submissions = self._load_submissions()
        
        # Check for duplicate submission
        for submission in submissions:
            if (submission.question_id == answer.question_id and 
                submission.student_id == answer.student_id):
                return False
        
        submissions.append(answer.dict())
        self._save_submissions(submissions)
        return True

    def get_student_submissions(self, student_id: str) -> List[SubmittedAnswer]:
        submissions = self._load_submissions()
        return [s for s in submissions if s.student_id == student_id]

    def get_submission(self, student_id: str, question_id: str) -> Optional[SubmittedAnswer]:
        submissions = self._load_submissions()
        for submission in submissions:
            if (submission.student_id == student_id and 
                submission.question_id == question_id):
                return submission
        return None

    def update_submission_grade(self, 
                               student_id: str, 
                               question_id: str, 
                               score: float, 
                               feedback: str) -> bool:
        submissions = self._load_submissions()
        updated = False
        
        for submission in submissions:
            if (submission.student_id == student_id and 
                submission.question_id == question_id):
                submission.score = score
                submission.feedback = feedback
                submission.graded = True
                updated = True
                break
        
        if updated:
            self._save_submissions(submissions)
            self._update_student_progress(student_id)
        return updated

    def _update_student_progress(self, student_id: str) -> None:
        submissions = self.get_student_submissions(student_id)
        progress = self._load_progress()
        
        if not submissions:
            return
        
        # Calculate progress metrics
        completed_questions = [s.question_id for s in submissions if s.graded]
        graded_submissions = [s for s in submissions if s.graded and s.score is not None]
        
        if graded_submissions:
            average_score = sum(s.score for s in graded_submissions) / len(graded_submissions)
        else:
            average_score = 0.0
        
        # Identify improvement areas based on low scores
        improvement_areas = [s.question_id for s in graded_submissions 
                           if s.score is not None and s.score < average_score]
        
        # Update progress
        progress[student_id] = StudentProgress(
            student_id=student_id,
            completed_questions=completed_questions,
            average_score=average_score,
            improvement_areas=improvement_areas
        ).dict()
        
        self._save_progress(progress)

    def get_student_progress(self, student_id: str) -> Optional[StudentProgress]:
        progress = self._load_progress()
        return progress.get(student_id)

    def get_ungraded_submissions(self) -> List[SubmittedAnswer]:
        submissions = self._load_submissions()
        return [s for s in submissions if not s.graded]

    def get_student_performance_summary(self, student_id: str) -> dict:
        submissions = self.get_student_submissions(student_id)
        progress = self.get_student_progress(student_id)
        
        if not submissions or not progress:
            return {}
        
        graded_submissions = [s for s in submissions if s.graded]
        
        return {
            "total_submissions": len(submissions),
            "graded_submissions": len(graded_submissions),
            "average_score": progress.average_score,
            "completed_questions": len(progress.completed_questions),
            "improvement_areas": progress.improvement_areas
        }