import os
from typing import List, Optional
from datetime import datetime
from app.core.config import settings
from app.models.schemas import CourseInfo, MCQ, MCQResponse
from app.services.pdf_processor import pdf_processor
from app.services.embedding_service import embedding_service
from app.services.mcq_generator import mcq_generator

class CourseService:
    def __init__(self):
        self.pdf_processor = pdf_processor
        self.embedding_service = embedding_service
        self.mcq_generator = mcq_generator

    def get_available_courses(self) -> List[CourseInfo]:
        """Get list of available courses"""
        courses = []

        if not os.path.exists(settings.COURSE_PDF_DIR):
            return courses

        for course_dir in os.listdir(settings.COURSE_PDF_DIR):
            course_path = os.path.join(settings.COURSE_PDF_DIR, course_dir)

            if os.path.isdir(course_path):
                # Check if PDF exists
                pdf_path = self.pdf_processor.find_course_pdf(course_dir)

                course_info = CourseInfo(
                    course_code=course_dir,
                    course_name=f"Course {course_dir}",  # You can enhance this
                    pdf_exists=pdf_path is not None,
                    pdf_path=pdf_path
                )
                courses.append(course_info)

        return courses

    def validate_course(self, course_code: str) -> bool:
        """Validate if course exists and has PDF"""
        pdf_path = self.pdf_processor.find_course_pdf(course_code)
        return pdf_path is not None

    def generate_course_mcqs(self, course_code: str, num_questions: int) -> MCQResponse:
        """Generate MCQs for a specific course"""
        try:
            # Validate course
            if not self.validate_course(course_code):
                raise ValueError(f"Course {course_code} not found or no PDF available")

            # Process PDF to get text chunks
            print(f"Processing PDF for course: {course_code}")
            chunks = self.pdf_processor.process_course_pdf(course_code)

            if not chunks:
                raise ValueError(f"No content extracted from course {course_code} PDF")

            print(f"Extracted {len(chunks)} chunks from PDF")

            # Get relevant context using embedding service
            print("Getting relevant context for MCQ generation...")
            relevant_context = self.embedding_service.get_relevant_context(chunks, num_questions)

            if not relevant_context:
                raise ValueError("No relevant context found for MCQ generation")

            print(f"Using {len(relevant_context)} relevant chunks for MCQ generation")

            # Generate MCQs
            print(f"Generating {num_questions} MCQs...")
            mcqs = self.mcq_generator.generate_mcqs(relevant_context, num_questions)

            if not mcqs:
                raise ValueError("Failed to generate any valid MCQs")

            print(f"Successfully generated {len(mcqs)} MCQs")

            # Create response
            response = MCQResponse(
                course_code=course_code,
                num_questions=len(mcqs),
                questions=mcqs,
                generated_at=datetime.now()
            )

            return response

        except Exception as e:
            raise Exception(f"Error generating MCQs for course {course_code}: {str(e)}")

    def get_course_info(self, course_code: str) -> Optional[CourseInfo]:
        """Get information about a specific course"""
        try:
            pdf_path = self.pdf_processor.find_course_pdf(course_code)

            if pdf_path:
                return CourseInfo(
                    course_code=course_code,
                    course_name=f"Course {course_code}",
                    pdf_exists=True,
                    pdf_path=pdf_path
                )

            return None

        except Exception:
            return None

# Initialize course service
course_service = CourseService()