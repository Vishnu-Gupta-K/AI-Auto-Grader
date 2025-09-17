import os
import json
import uuid
from datetime import datetime

class Teacher:
    def __init__(self):
        self.questions_dir = "data/questions"
    
    def menu(self):
        print("\n===== Teacher Mode =====")
        print("1. Create a new question")
        print("2. View all questions")
        print("3. View student submissions for a question")
        print("4. Return to main menu")
        
        choice = input("\nSelect option: ")
        
        if choice == "1":
            self.create_question()
        elif choice == "2":
            self.view_all_questions()
        elif choice == "3":
            self.view_submissions()
        elif choice == "4":
            return
        else:
            print("Invalid choice. Please try again.")
        
        self.menu()
    
    def create_question(self):
        print("\n===== Create New Question =====")
        subject = input("Subject: ")
        topic = input("Topic: ")
        question_text = input("Question: ")
        
        # Optional: Add expected answer or grading criteria
        expected_answer = input("Expected answer (optional): ")
        grading_criteria = input("Grading criteria (optional): ")
        
        # Generate unique ID for the question
        question_id = str(uuid.uuid4())[:8]
        
        question_data = {
            "id": question_id,
            "subject": subject,
            "topic": topic,
            "question": question_text,
            "expected_answer": expected_answer,
            "grading_criteria": grading_criteria,
            "created_at": datetime.now().isoformat()
        }
        
        # Save question to file
        filename = f"{self.questions_dir}/{question_id}.json"
        with open(filename, 'w') as f:
            json.dump(question_data, f, indent=4)
        
        print(f"\nQuestion created successfully! Question ID: {question_id}")
    
    def view_all_questions(self):
        print("\n===== All Questions =====")
        questions = self.get_all_questions()
        
        if not questions:
            print("No questions found.")
            return
        
        for i, q in enumerate(questions, 1):
            print(f"{i}. [{q['id']}] {q['subject']} - {q['topic']}: {q['question'][:50]}...")
        
        # Option to view a specific question in detail
        choice = input("\nEnter number to view details (or press Enter to go back): ")
        if choice.isdigit() and 1 <= int(choice) <= len(questions):
            self.view_question_detail(questions[int(choice)-1])
    
    def view_question_detail(self, question):
        print(f"\n===== Question Details: {question['id']} =====")
        print(f"Subject: {question['subject']}")
        print(f"Topic: {question['topic']}")
        print(f"Question: {question['question']}")
        if question['expected_answer']:
            print(f"Expected Answer: {question['expected_answer']}")
        if question['grading_criteria']:
            print(f"Grading Criteria: {question['grading_criteria']}")
        print(f"Created: {question['created_at']}")
        
        input("\nPress Enter to continue...")
    
    def view_submissions(self):
        print("\n===== View Submissions =====")
        questions = self.get_all_questions()
        
        if not questions:
            print("No questions found.")
            return
        
        for i, q in enumerate(questions, 1):
            print(f"{i}. [{q['id']}] {q['subject']} - {q['topic']}: {q['question'][:50]}...")
        
        choice = input("\nEnter question number to view submissions: ")
        if choice.isdigit() and 1 <= int(choice) <= len(questions):
            self.view_question_submissions(questions[int(choice)-1]['id'])
    
    def view_question_submissions(self, question_id):
        submissions_dir = f"data/submissions/{question_id}"
        if not os.path.exists(submissions_dir):
            print("\nNo submissions found for this question.")
            input("Press Enter to continue...")
            return
        
        submissions = []
        for filename in os.listdir(submissions_dir):
            if filename.endswith('.json'):
                with open(f"{submissions_dir}/{filename}", 'r') as f:
                    submissions.append(json.load(f))
        
        if not submissions:
            print("\nNo submissions found for this question.")
            input("Press Enter to continue...")
            return
        
        print(f"\n===== Submissions for Question {question_id} =====")
        for i, sub in enumerate(submissions, 1):
            print(f"{i}. Student: {sub['student_name']} - Score: {sub.get('score', 'Not graded')}")
        
        choice = input("\nEnter number to view submission details (or press Enter to go back): ")
        if choice.isdigit() and 1 <= int(choice) <= len(submissions):
            self.view_submission_detail(submissions[int(choice)-1])
    
    def view_submission_detail(self, submission):
        print(f"\n===== Submission Details =====")
        print(f"Student: {submission['student_name']}")
        print(f"Submitted: {submission['submitted_at']}")
        print(f"\nAnswer:\n{submission['answer']}")
        
        if 'evaluation' in submission:
            print(f"\nLLM Evaluation:\n{submission['evaluation']}")
        
        if 'score' in submission:
            print(f"\nScore: {submission['score']}")
        
        input("\nPress Enter to continue...")
    
    def get_all_questions(self):
        questions = []
        if os.path.exists(self.questions_dir):
            for filename in os.listdir(self.questions_dir):
                if filename.endswith('.json'):
                    with open(f"{self.questions_dir}/{filename}", 'r') as f:
                        questions.append(json.load(f))
        return questions