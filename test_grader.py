import unittest
from app import (
    Answer, 
    check_keyword_presence, 
    evaluate_concept_coverage, 
    calculate_semantic_similarity,
    generate_feedback
)
from teacher_interface import TeacherInterface, Question, RubricItem
from student_interface import StudentInterface, SubmittedAnswer
from datetime import datetime
import os
import shutil

class TestAutoGrader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create test data directory
        cls.test_data_dir = "test_data"
        os.makedirs(cls.test_data_dir, exist_ok=True)
        
        # Initialize interfaces with test directory
        cls.teacher = TeacherInterface(cls.test_data_dir)
        cls.student = StudentInterface(cls.test_data_dir)

    @classmethod
    def tearDownClass(cls):
        # Clean up test data directory
        shutil.rmtree(cls.test_data_dir)

    def test_keyword_detection(self):
        text = "The process of photosynthesis converts light energy into chemical energy"
        keywords = ["photosynthesis", "light energy", "chemical energy"]
        
        matches = check_keyword_presence(text, keywords)
        
        self.assertTrue(matches["photosynthesis"])
        self.assertTrue(matches["light energy"])
        self.assertTrue(matches["chemical energy"])

    def test_concept_evaluation(self):
        text = "The water cycle involves evaporation, condensation, and precipitation"
        concepts = ["water cycle process", "weather patterns"]
        
        coverage = evaluate_concept_coverage(text, concepts)
        
        self.assertGreater(coverage["water cycle process"], 0.7)
        self.assertLess(coverage["weather patterns"], 0.7)

    def test_semantic_similarity(self):
        text1 = "The Earth orbits around the Sun"
        text2 = "Our planet revolves around the solar system's star"
        
        similarity = calculate_semantic_similarity(text1, text2)
        
        self.assertGreater(similarity, 0.8)

    def test_question_management(self):
        # Create test question
        question = Question(
            id="Q1",
            text="Explain the process of photosynthesis",
            subject="Biology",
            reference_answer="Photosynthesis is the process where plants convert light energy into chemical energy",
            rubric={
                "basic": RubricItem(
                    description="Basic understanding",
                    points=5.0,
                    keywords=["photosynthesis", "light energy", "chemical energy"],
                    concepts=["energy conversion", "plant process"]
                )
            },
            total_points=5.0
        )
        
        # Test adding question
        self.assertTrue(self.teacher.add_question(question))
        
        # Test retrieving question
        retrieved = self.teacher.get_question("Q1")
        self.assertEqual(retrieved.text, question.text)

    def test_answer_submission(self):
        # Create test submission
        submission = SubmittedAnswer(
            question_id="Q1",
            student_id="S1",
            answer_text="Photosynthesis converts sunlight into energy that plants can use",
            submission_time=datetime.now()
        )
        
        # Test submitting answer
        self.assertTrue(self.student.submit_answer(submission))
        
        # Test retrieving submission
        retrieved = self.student.get_submission("S1", "Q1")
        self.assertEqual(retrieved.answer_text, submission.answer_text)

    def test_grading_and_feedback(self):
        # Test answer for grading
        answer = Answer(
            student_response="Photosynthesis converts sunlight into energy that plants can use",
            reference_answer="Photosynthesis is the process where plants convert light energy into chemical energy",
            keywords=["photosynthesis", "light energy", "chemical energy"],
            concepts=["energy conversion", "plant process"],
            total_points=5.0,
            rubric={"photosynthesis": 2.0, "light energy": 1.5, "chemical energy": 1.5}
        )
        
        # Test keyword matches
        keyword_matches = check_keyword_presence(answer.student_response, answer.keywords)
        self.assertTrue(keyword_matches["photosynthesis"])
        
        # Test feedback generation
        concept_scores = evaluate_concept_coverage(answer.student_response, answer.concepts)
        feedback, suggestions = generate_feedback(
            keyword_matches,
            concept_scores,
            4.0,
            answer.total_points
        )
        
        self.assertIsInstance(feedback, str)
        self.assertIsInstance(suggestions, list)

    def test_grade_override(self):
        # Update submission grade
        self.assertTrue(
            self.student.update_submission_grade(
                student_id="S1",
                question_id="Q1",
                score=4.5,
                feedback="Good understanding of photosynthesis concept"
            )
        )
        
        # Check updated grade
        submission = self.student.get_submission("S1", "Q1")
        self.assertEqual(submission.score, 4.5)

    def test_student_progress(self):
        # Get student progress
        progress = self.student.get_student_progress("S1")
        
        self.assertIsNotNone(progress)
        self.assertEqual(progress.student_id, "S1")
        self.assertGreater(progress.average_score, 0)

if __name__ == '__main__':
    unittest.main()