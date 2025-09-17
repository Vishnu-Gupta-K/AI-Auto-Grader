import os
import json
import uuid
from datetime import datetime
from llm_evaluator import LLMEvaluator

class Student:
    def __init__(self):
        self.questions_dir = "data/questions"
        self.submissions_dir = "data/submissions"
        self.evaluator = LLMEvaluator()
    
    def menu(self):
        print("\n===== Student Mode =====")
        print("1. View available questions")
        print("2. Submit an answer")
        print("3. View my submissions")
        print("4. Return to main menu")
        
        choice = input("\nSelect option: ")
        
        if choice == "1":
            self.view_available_questions()
        elif choice == "2":
            self.submit_answer()
        elif choice == "3":
            self.view_my_submissions()
        elif choice == "4":
            return
        else:
            print("Invalid choice. Please try again.")
        
        self.menu()
    
    def view_available_questions(self):
        print("\n===== Available Questions =====")
        questions = self.get_all_questions()
        
        if not questions:
            print("No questions available.")
            input("\nPress Enter to continue...")
            return
        
        for i, q in enumerate(questions, 1):
            print(f"{i}. [{q['id']}] {q['subject']} - {q['topic']}: {q['question'][:50]}...")
        
        choice = input("\nEnter number to view details (or press Enter to go back): ")
        if choice.isdigit() and 1 <= int(choice) <= len(questions):
            self.view_question_detail(questions[int(choice)-1])
    
    def view_question_detail(self, question):
        print(f"\n===== Question Details: {question['id']} =====")
        print(f"Subject: {question['subject']}")
        print(f"Topic: {question['topic']}")
        print(f"Question: {question['question']}")
        
        # Ask if student wants to answer this question
        choice = input("\nWould you like to answer this question? (y/n): ")
        if choice.lower() == 'y':
            self.answer_question(question)
        else:
            input("\nPress Enter to continue...")
    
    def answer_question(self, question):
        print(f"\n===== Answer Question: {question['id']} =====")
        print(f"Question: {question['question']}")
        
        student_name = input("\nYour name: ")
        print("\nEnter your answer (type 'DONE' on a new line when finished):")
        
        answer_lines = []
        while True:
            line = input()
            if line == "DONE":
                break
            answer_lines.append(line)
        
        answer = "\n".join(answer_lines)
        
        # Create submission
        submission_id = str(uuid.uuid4())[:8]
        submission = {
            "id": submission_id,
            "question_id": question['id'],
            "student_name": student_name,
            "answer": answer,
            "submitted_at": datetime.now().isoformat()
        }
        
        # Evaluate the answer using LLM
        print("\nEvaluating your answer...")
        evaluation, score = self.evaluator.evaluate_answer(
            question['question'],
            answer,
            question.get('expected_answer', ''),
            question.get('grading_criteria', '')
        )
        
        submission['evaluation'] = evaluation
        submission['score'] = score
        
        # Save submission
        submission_dir = f"{self.submissions_dir}/{question['id']}"
        os.makedirs(submission_dir, exist_ok=True)
        
        with open(f"{submission_dir}/{submission_id}.json", 'w') as f:
            json.dump(submission, f, indent=4)
        
        print("\nYour answer has been submitted and evaluated!")
        print(f"Evaluation:\n{evaluation}")
        print(f"Score: {score}")
        
        input("\nPress Enter to continue...")
    
    def submit_answer(self):
        print("\n===== Submit Answer =====")
        questions = self.get_all_questions()
        
        if not questions:
            print("No questions available.")
            input("\nPress Enter to continue...")
            return
        
        for i, q in enumerate(questions, 1):
            print(f"{i}. [{q['id']}] {q['subject']} - {q['topic']}: {q['question'][:50]}...")
        
        choice = input("\nEnter question number to answer: ")
        if choice.isdigit() and 1 <= int(choice) <= len(questions):
            self.answer_question(questions[int(choice)-1])
    
    def view_my_submissions(self):
        print("\n===== My Submissions =====")
        student_name = input("Your name: ")
        
        all_submissions = []
        
        # Search through all question directories for submissions by this student
        if os.path.exists(self.submissions_dir):
            for question_dir in os.listdir(self.submissions_dir):
                question_submissions_dir = f"{self.submissions_dir}/{question_dir}"
                if os.path.isdir(question_submissions_dir):
                    for filename in os.listdir(question_submissions_dir):
                        if filename.endswith('.json'):
                            with open(f"{question_submissions_dir}/{filename}", 'r') as f:
                                submission = json.load(f)
                                if submission['student_name'].lower() == student_name.lower():
                                    # Get question details
                                    question_file = f"{self.questions_dir}/{submission['question_id']}.json"
                                    if os.path.exists(question_file):
                                        with open(question_file, 'r') as qf:
                                            question = json.load(qf)
                                            submission['question_text'] = question['question']
                                            submission['subject'] = question['subject']
                                    all_submissions.append(submission)
        
        if not all_submissions:
            print(f"\nNo submissions found for student: {student_name}")
            input("Press Enter to continue...")
            return
        
        print(f"\nFound {len(all_submissions)} submissions for {student_name}:")
        for i, sub in enumerate(all_submissions, 1):
            subject = sub.get('subject', 'Unknown')
            question_preview = sub.get('question_text', 'Unknown')[:30]
            print(f"{i}. {subject} - {question_preview}... Score: {sub.get('score', 'Not graded')}")
        
        choice = input("\nEnter number to view submission details (or press Enter to go back): ")
        if choice.isdigit() and 1 <= int(choice) <= len(all_submissions):
            self.view_submission_detail(all_submissions[int(choice)-1])
    
    def view_submission_detail(self, submission):
        print(f"\n===== Submission Details =====")
        print(f"Student: {submission['student_name']}")
        print(f"Submitted: {submission['submitted_at']}")
        
        # Get question details if available
        if 'question_text' in submission:
            print(f"\nQuestion: {submission['question_text']}")
        else:
            question_file = f"{self.questions_dir}/{submission['question_id']}.json"
            if os.path.exists(question_file):
                with open(question_file, 'r') as f:
                    question = json.load(f)
                    print(f"\nQuestion: {question['question']}")
        
        print(f"\nYour Answer:\n{submission['answer']}")
        
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