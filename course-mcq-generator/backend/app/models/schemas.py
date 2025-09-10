from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MCQRequest(BaseModel):
    course_code: str = Field(..., description="Unique course code")
    num_questions: int = Field(..., ge=1, le=20, description="Number of MCQs to generate (1-20)")

    class Config:
        json_schema_extra = {
            "example": {
                "course_code": "CS101",
                "num_questions": 5
            }
        }

class MCQOption(BaseModel):
    option_id: str
    text: str
    is_correct: bool

class MCQ(BaseModel):
    question_id: int
    question: str
    options: List[MCQOption]
    correct_answer: str
    explanation: Optional[str] = None

class MCQResponse(BaseModel):
    course_code: str
    num_questions: int
    questions: List[MCQ]
    generated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "course_code": "CS101",
                "num_questions": 2,
                "questions": [
                    {
                        "question_id": 1,
                        "question": "What is the time complexity of binary search?",
                        "options": [
                            {"option_id": "A", "text": "O(n)", "is_correct": False},
                            {"option_id": "B", "text": "O(log n)", "is_correct": True},
                            {"option_id": "C", "text": "O(n^2)", "is_correct": False},
                            {"option_id": "D", "text": "O(1)", "is_correct": False}
                        ],
                        "correct_answer": "B",
                        "explanation": "Binary search divides the search space in half at each step"
                    }
                ],
                "generated_at": "2025-09-10T18:58:00Z"
            }
        }

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

class CourseInfo(BaseModel):
    course_code: str
    course_name: Optional[str] = None
    pdf_exists: bool
    pdf_path: Optional[str] = None