import os
import requests
import json
import google.generativeai as genai
from dotenv import load_dotenv

class LLMEvaluator:
    def __init__(self):
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        # Get API key from environment variable
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")  # Updated to use the correct model name
        
        # Check if API key is available
        if not self.api_key:
            print("Warning: Gemini API key not found. Please set GEMINI_API_KEY in environment variables or .env file.")
            print("Evaluation will be simulated in demo mode.")
        else:
            # Configure the Gemini API
            genai.configure(api_key=self.api_key)
    
    def evaluate_answer(self, question, student_answer, expected_answer="", grading_criteria=""):
        """Evaluate a student's answer using an LLM.
        
        Args:
            question (str): The question that was asked
            student_answer (str): The student's answer
            expected_answer (str, optional): The expected answer if provided by teacher
            grading_criteria (str, optional): Specific grading criteria if provided by teacher
            
        Returns:
            tuple: (evaluation_text, score)
        """
        if not self.api_key:
            # Demo mode - simulate evaluation
            return self._simulate_evaluation(student_answer, question, expected_answer, grading_criteria)
        
        # Construct the prompt for the LLM
        prompt = self._construct_evaluation_prompt(
            question, student_answer, expected_answer, grading_criteria
        )
        
        try:
            # Call Gemini API
            response = self._call_gemini_api(prompt)
            
            # Parse the response
            evaluation, score = self._parse_evaluation_response(response)
            return evaluation, score
            
        except Exception as e:
            print(f"Error during LLM evaluation: {e}")
            # Fallback to simulated evaluation
            return self._simulate_evaluation(student_answer, question, expected_answer, grading_criteria)
    
    def _construct_evaluation_prompt(self, question, student_answer, expected_answer, grading_criteria):
        """Construct a prompt for the LLM to evaluate the answer."""
        # Determine max score based on grading criteria
        max_score = 100
        try:
            if grading_criteria and grading_criteria.isdigit():
                max_score = int(grading_criteria)
        except:
            pass
            
        system_prompt = f"""
        You are an expert educational evaluator. Your task is to evaluate a student's answer to a question.
        Provide constructive feedback, highlighting strengths and areas for improvement.
        After your evaluation, assign a score from 0-{max_score} based on the accuracy and completeness of the answer.
        
        Format your response as follows:
        EVALUATION: [Your detailed evaluation here]
        SCORE: [Numeric score between 0-{max_score}]
        """
        
        content = f"Question: {question}\n\nStudent Answer: {student_answer}"
        
        if expected_answer:
            content += f"\n\nExpected Answer: {expected_answer}"
        
        if grading_criteria:
            content += f"\n\nGrading Criteria: {grading_criteria}"
        
        # For Gemini, we'll combine the system prompt and user content
        full_prompt = f"{system_prompt}\n\n{content}"
        
        return full_prompt
    
    def _call_gemini_api(self, prompt):
        """Call the Gemini API with the given prompt."""
        try:
            # Create a generative model
            model = genai.GenerativeModel(self.model)
            
            # Generate content
            response = model.generate_content(prompt)
            
            # Return the text response
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API call failed: {str(e)}")
    
    def _parse_evaluation_response(self, response):
        """Parse the LLM response to extract evaluation and score."""
        # Default values in case parsing fails
        evaluation = response
        score = 0
        
        try:
            # Try to extract EVALUATION and SCORE sections
            if "EVALUATION:" in response and "SCORE:" in response:
                evaluation_part = response.split("EVALUATION:")[1].split("SCORE:")[0].strip()
                score_part = response.split("SCORE:")[1].strip()
                
                # Extract numeric score
                import re
                score_match = re.search(r'\d+', score_part)
                if score_match:
                    score = int(score_match.group())
                    # No need to scale the score as we've already set the max score in the prompt
                    # Just ensure it's not negative
                    score = max(0, score)
                
                evaluation = evaluation_part
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            # Use the full response as evaluation if parsing fails
            evaluation = response
        
        return evaluation, score
    
    def _simulate_evaluation(self, student_answer, question="", expected_answer="", grading_criteria=""):
        """Simulate an evaluation when API key is not available (demo mode)."""
        # Determine max score based on grading criteria
        max_score = 100
        try:
            if grading_criteria and grading_criteria.isdigit():
                max_score = int(grading_criteria)
        except:
            pass
            
        # Simple heuristic: longer answers get better scores
        word_count = len(student_answer.split())
        
        # Calculate score as a percentage of max_score
        if word_count < 10:
            percentage = 0.3  # 30%
            evaluation = "Your answer is too brief. Please provide more details and explanation."
        elif word_count < 30:
            percentage = 0.6  # 60%
            evaluation = "Your answer covers some key points but could be more comprehensive."
        elif word_count < 50:
            percentage = 0.8  # 80%
            evaluation = "Good answer! You've covered most of the important aspects of the question."
        else:
            percentage = 0.9  # 90%
            evaluation = "Excellent answer! Comprehensive and well-articulated."
        
        score = int(max_score * percentage)
        
        evaluation += "\n\nNote: This is a simulated evaluation (demo mode). For actual LLM evaluation, please set up your Gemini API key."
        
        return evaluation, score