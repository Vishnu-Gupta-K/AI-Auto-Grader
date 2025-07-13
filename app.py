from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import spacy
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(title="AI Auto Grader")

# Load NLP models
nlp = spacy.load("en_core_web_sm")
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-mpnet-base-v2")

class Answer(BaseModel):
    student_response: str
    reference_answer: str
    keywords: List[str]
    concepts: List[str]
    total_points: float
    rubric: Dict[str, float]

class GradingResult(BaseModel):
    score: float
    feedback: str
    keyword_matches: Dict[str, bool]
    concept_coverage: Dict[str, float]
    improvement_suggestions: List[str]

def extract_embeddings(text: str) -> np.ndarray:
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()

def calculate_semantic_similarity(text1: str, text2: str) -> float:
    emb1 = extract_embeddings(text1)
    emb2 = extract_embeddings(text2)
    return float(cosine_similarity(emb1, emb2)[0][0])

def check_keyword_presence(text: str, keywords: List[str]) -> Dict[str, bool]:
    text_lower = text.lower()
    doc = nlp(text_lower)
    lemmatized_text = " ".join([token.lemma_ for token in doc])
    
    keyword_matches = {}
    for keyword in keywords:
        keyword_lower = keyword.lower()
        keyword_doc = nlp(keyword_lower)
        keyword_lemma = " ".join([token.lemma_ for token in keyword_doc])
        keyword_matches[keyword] = (keyword_lemma in lemmatized_text)
    
    return keyword_matches

def evaluate_concept_coverage(text: str, concepts: List[str]) -> Dict[str, float]:
    concept_scores = {}
    for concept in concepts:
        similarity = calculate_semantic_similarity(text, concept)
        concept_scores[concept] = similarity
    return concept_scores

def generate_feedback(keyword_matches: Dict[str, bool], 
                     concept_scores: Dict[str, float],
                     score: float,
                     total_points: float) -> tuple[str, List[str]]:
    feedback = f"Score: {score:.2f}/{total_points:.2f}\n\n"
    suggestions = []

    # Keyword feedback
    missing_keywords = [k for k, v in keyword_matches.items() if not v]
    if missing_keywords:
        feedback += "Missing important keywords: " + ", ".join(missing_keywords) + "\n"
        suggestions.append(f"Try to incorporate these keywords: {', '.join(missing_keywords)}")

    # Concept feedback
    weak_concepts = [c for c, s in concept_scores.items() if s < 0.7]
    if weak_concepts:
        feedback += "Concepts needing improvement: " + ", ".join(weak_concepts) + "\n"
        suggestions.append(f"Strengthen your understanding of: {', '.join(weak_concepts)}")

    return feedback, suggestions

@app.post("/grade/", response_model=GradingResult)
async def grade_answer(answer: Answer) -> GradingResult:
    # Check keywords
    keyword_matches = check_keyword_presence(answer.student_response, answer.keywords)
    keyword_score = sum(answer.rubric.get(k, 1) for k, v in keyword_matches.items() if v)

    # Evaluate concepts
    concept_coverage = evaluate_concept_coverage(answer.student_response, answer.concepts)
    concept_score = sum(score * answer.rubric.get(concept, 1) 
                       for concept, score in concept_coverage.items())

    # Calculate total score
    total_score = keyword_score + concept_score

    # Generate feedback
    feedback, suggestions = generate_feedback(
        keyword_matches,
        concept_coverage,
        total_score,
        answer.total_points
    )

    return GradingResult(
        score=total_score,
        feedback=feedback,
        keyword_matches=keyword_matches,
        concept_coverage=concept_coverage,
        improvement_suggestions=suggestions
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)