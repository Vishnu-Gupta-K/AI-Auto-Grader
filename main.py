import os
import json
from teacher import Teacher
from student import Student
from llm_evaluator import LLMEvaluator

def main():
    while True:
        print("\n===== LLM-Based Question and Answer System =====")
        print("1. Teacher Mode")
        print("2. Student Mode")
        print("3. Exit")
        
        choice = input("\nSelect mode: ")
        
        if choice == "1":
            teacher = Teacher()
            teacher.menu()
        elif choice == "2":
            student = Student()
            student.menu()
        elif choice == "3":
            print("Exiting program. Goodbye!")
            exit()
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Create data directories if they don't exist
    os.makedirs("data/questions", exist_ok=True)
    os.makedirs("data/submissions", exist_ok=True)
    
    main()