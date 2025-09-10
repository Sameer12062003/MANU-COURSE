from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.schemas import MCQRequest, MCQResponse, CourseInfo, ErrorResponse
from app.services.course_service import course_service

router = APIRouter()

@router.get("/courses", response_model=List[CourseInfo])
async def get_courses():
    """Get list of available courses"""
    try:
        courses = course_service.get_available_courses()
        return courses
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching courses: {str(e)}"
        )

@router.get("/courses/{course_code}", response_model=CourseInfo)
async def get_course_info(course_code: str):
    """Get information about a specific course"""
    try:
        course_info = course_service.get_course_info(course_code)
        if not course_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course {course_code} not found"
            )
        return course_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching course info: {str(e)}"
        )

@router.post("/generate-mcqs", response_model=MCQResponse)
async def generate_mcqs(request: MCQRequest):
    """Generate MCQs for a course"""
    try:
        # Validate request
        if not request.course_code or not request.course_code.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course code is required"
            )

        if request.num_questions < 1 or request.num_questions > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Number of questions must be between 1 and 20"
            )

        # Generate MCQs
        response = course_service.generate_course_mcqs(
            course_code=request.course_code,
            num_questions=request.num_questions
        )

        return response

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating MCQs: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Course MCQ Generator API is running"}