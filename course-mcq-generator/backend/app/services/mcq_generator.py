import json
import re
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from app.core.config import settings
from app.models.schemas import MCQ, MCQOption

class MCQGenerator:
    def __init__(self):
        """Initialize the MCQ generator with Gemini LLM"""
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.7,
            max_tokens=4000
        )

    def create_mcq_prompt(self, context: str, num_questions: int) -> str:
        """Create a prompt for MCQ generation"""
        prompt = f"""
You are an expert educational content creator. Generate {num_questions} high-quality multiple-choice questions based on the following course material.

COURSE MATERIAL:
{context}

INSTRUCTIONS:
1. Generate exactly {num_questions} multiple-choice questions
2. Each question should have exactly 4 options (A, B, C, D)
3. Only ONE option should be correct
4. Questions should test understanding, not just memorization
5. Include a brief explanation for the correct answer
6. Questions should be clear, unambiguous, and educational
7. Cover different aspects of the material

REQUIRED JSON FORMAT:
{{
    "questions": [
        {{
            "question_id": 1,
            "question": "What is...?",
            "options": [
                {{"option_id": "A", "text": "Option A text", "is_correct": false}},
                {{"option_id": "B", "text": "Option B text", "is_correct": true}},
                {{"option_id": "C", "text": "Option C text", "is_correct": false}},
                {{"option_id": "D", "text": "Option D text", "is_correct": false}}
            ],
            "correct_answer": "B",
            "explanation": "Brief explanation why B is correct"
        }}
    ]
}}

Generate the questions now:
"""
        return prompt

    def parse_mcq_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse the LLM response to extract MCQ data"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                return data.get("questions", [])

            # If no JSON found, try to parse the entire response
            try:
                data = json.loads(response_text.strip())
                return data.get("questions", [])
            except json.JSONDecodeError:
                # Fallback: extract questions manually
                return self.manual_parse_questions(response_text)

        except Exception as e:
            raise Exception(f"Error parsing MCQ response: {str(e)}")

    def manual_parse_questions(self, text: str) -> List[Dict[str, Any]]:
        """Manually parse questions if JSON parsing fails"""
        questions = []

        # Split by question numbers or patterns
        question_parts = re.split(r'\n\s*(?:Question )?\d+[.:]', text)

        for i, part in enumerate(question_parts[1:], 1):  # Skip first empty part
            try:
                question_data = self.extract_question_components(part, i)
                if question_data:
                    questions.append(question_data)
            except Exception:
                continue

        return questions

    def extract_question_components(self, text: str, question_id: int) -> Dict[str, Any]:
        """Extract question components from text"""
        lines = text.strip().split('\n')

        # Find question text (usually the first non-empty line)
        question = ""
        options = []
        correct_answer = ""
        explanation = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if it's an option
            if re.match(r'^[A-D][.)]', line):
                option_match = re.match(r'^([A-D])[.)]\s*(.+)', line)
                if option_match:
                    option_id = option_match.group(1)
                    option_text = option_match.group(2)
                    options.append({
                        "option_id": option_id,
                        "text": option_text,
                        "is_correct": False
                    })
            elif not question and not line.startswith(('Answer:', 'Explanation:', 'Correct:')):
                question = line
            elif line.startswith(('Answer:', 'Correct:')):
                correct_match = re.search(r'([A-D])', line)
                if correct_match:
                    correct_answer = correct_match.group(1)
            elif line.startswith('Explanation:'):
                explanation = line.replace('Explanation:', '').strip()

        # Mark correct option
        for option in options:
            if option["option_id"] == correct_answer:
                option["is_correct"] = True

        if question and len(options) == 4 and correct_answer:
            return {
                "question_id": question_id,
                "question": question,
                "options": options,
                "correct_answer": correct_answer,
                "explanation": explanation or f"Option {correct_answer} is correct."
            }

        return None

    def validate_mcq_data(self, mcq_data: List[Dict[str, Any]]) -> List[MCQ]:
        """Validate and convert MCQ data to Pydantic models"""
        validated_mcqs = []

        for i, question_data in enumerate(mcq_data, 1):
            try:
                # Ensure required fields exist
                if not all(key in question_data for key in ["question", "options", "correct_answer"]):
                    continue

                # Validate options
                options = question_data["options"]
                if len(options) != 4:
                    continue

                # Create MCQOption objects
                mcq_options = []
                correct_count = 0

                for option in options:
                    if not all(key in option for key in ["option_id", "text", "is_correct"]):
                        continue

                    mcq_option = MCQOption(
                        option_id=option["option_id"],
                        text=option["text"],
                        is_correct=option["is_correct"]
                    )
                    mcq_options.append(mcq_option)

                    if option["is_correct"]:
                        correct_count += 1

                # Ensure exactly one correct answer
                if correct_count != 1 or len(mcq_options) != 4:
                    continue

                # Create MCQ object
                mcq = MCQ(
                    question_id=question_data.get("question_id", i),
                    question=question_data["question"],
                    options=mcq_options,
                    correct_answer=question_data["correct_answer"],
                    explanation=question_data.get("explanation")
                )

                validated_mcqs.append(mcq)

            except Exception as e:
                print(f"Error validating MCQ {i}: {str(e)}")
                continue

        return validated_mcqs

    def generate_mcqs(self, context: List[str], num_questions: int) -> List[MCQ]:
        """Generate MCQs from course content"""
        try:
            # Combine context chunks
            combined_context = "\n\n".join(context[:10])  # Use first 10 chunks to avoid token limits

            # Truncate if too long (rough estimate for token limit)
            if len(combined_context) > 15000:
                combined_context = combined_context[:15000] + "..."

            # Create prompt
            prompt = self.create_mcq_prompt(combined_context, num_questions)

            # Generate response
            messages = [
                SystemMessage(content="You are an expert educational content creator specialized in creating high-quality multiple-choice questions."),
                HumanMessage(content=prompt)
            ]

            response = self.llm(messages)
            response_text = response.content

            # Parse response
            mcq_data = self.parse_mcq_response(response_text)

            # Validate and convert to MCQ objects
            validated_mcqs = self.validate_mcq_data(mcq_data)

            # If we don't have enough valid MCQs, try to generate more
            if len(validated_mcqs) < num_questions:
                print(f"Only {len(validated_mcqs)} valid MCQs generated, expected {num_questions}")

                # Try with different context if we have more chunks
                if len(context) > 10:
                    additional_context = "\n\n".join(context[10:20])
                    if len(additional_context) > 15000:
                        additional_context = additional_context[:15000] + "..."

                    additional_prompt = self.create_mcq_prompt(additional_context, num_questions - len(validated_mcqs))
                    additional_messages = [
                        SystemMessage(content="You are an expert educational content creator specialized in creating high-quality multiple-choice questions."),
                        HumanMessage(content=additional_prompt)
                    ]

                    additional_response = self.llm(additional_messages)
                    additional_mcq_data = self.parse_mcq_response(additional_response.content)
                    additional_validated_mcqs = self.validate_mcq_data(additional_mcq_data)

                    validated_mcqs.extend(additional_validated_mcqs)

            return validated_mcqs[:num_questions]  # Return only requested number

        except Exception as e:
            raise Exception(f"Error generating MCQs: {str(e)}")

# Initialize MCQ generator
mcq_generator = MCQGenerator()