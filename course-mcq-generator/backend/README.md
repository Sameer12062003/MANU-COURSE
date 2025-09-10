# Course MCQ Generator - Backend

FastAPI backend service for generating Multiple Choice Questions from course PDFs using Gemini LLM and RAG.

## Features

- **PDF Processing**: Extract text from course PDFs using PyMuPDF and pdfplumber
- **Vector Embeddings**: Create semantic embeddings using Google Gemini embedding model
- **FAISS Vector Database**: Fast similarity search and retrieval
- **LLM Integration**: Generate MCQs using Gemini LLM with LangChain
- **RAG Pipeline**: Retrieval-Augmented Generation for contextually relevant questions
- **REST API**: Clean FastAPI endpoints with automatic documentation

## Prerequisites

- Python 3.10 or higher
- Google API Key for Gemini models
- PDF files organized in coursePdf directory structure

## Installation

1. **Clone the repository and navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Environment Setup:**
```bash
cp .env.example .env
# Edit .env file and add your Google API key
```

5. **Create course directory structure:**
```bash
mkdir -p coursePdf/CS101
mkdir -p coursePdf/CS102
# Add your PDF files to respective course directories
```

## Configuration

### Environment Variables (.env)

```env
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-pro
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001
COURSE_PDF_DIR=coursePdf
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Course PDF Structure

```
coursePdf/
├── CS101/
│   └── course_material.pdf
├── CS102/
│   └── course_material.pdf
└── [CourseCode]/
    └── course_material.pdf
```

## Getting Google API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new project or select existing one
3. Generate an API key
4. Add the key to your .env file

## Running the Application

### Development Mode
```bash
python -m app.main
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
```http
GET /health
```

### Get Available Courses
```http
GET /api/v1/courses
```

### Get Course Information
```http
GET /api/v1/courses/{course_code}
```

### Generate MCQs
```http
POST /api/v1/generate-mcqs
Content-Type: application/json

{
  "course_code": "CS101",
  "num_questions": 5
}
```

## Example Usage

```python
import requests

# Generate MCQs
response = requests.post(
    "http://localhost:8000/api/v1/generate-mcqs",
    json={
        "course_code": "CS101",
        "num_questions": 5
    }
)

mcqs = response.json()
```

## Architecture

### Services

1. **PDFProcessor**: Extracts and chunks text from PDF files
2. **EmbeddingService**: Creates vector embeddings and manages FAISS index
3. **MCQGenerator**: Generates MCQs using Gemini LLM
4. **CourseService**: Orchestrates the complete MCQ generation pipeline

### Data Flow

1. User requests MCQ generation for a course
2. System locates course PDF file
3. PDF content is extracted and chunked
4. Text chunks are converted to vector embeddings
5. FAISS index is created for similarity search
6. Relevant context is retrieved using semantic search
7. Gemini LLM generates MCQs based on context
8. Structured JSON response is returned

## Troubleshooting

### Common Issues

1. **Google API Key Error**
   - Ensure API key is valid and has Gemini access enabled
   - Check quota and billing settings

2. **PDF Processing Error**
   - Verify PDF file exists and is readable
   - Check file permissions

3. **Memory Issues**
   - Reduce CHUNK_SIZE in configuration
   - Limit number of questions generated

4. **Installation Issues**
   - Update pip: `pip install --upgrade pip`
   - Install build tools if needed

### Performance Optimization

- Use FAISS GPU version for larger datasets
- Implement caching for frequently accessed courses
- Consider using IndexIVFFlat for large document collections

## Development

### Running Tests
```bash
pytest tests/
```

### Code Format
```bash
black app/
flake8 app/
```

### Adding New Course
1. Create directory: `coursePdf/[COURSE_CODE]/`
2. Add PDF: `coursePdf/[COURSE_CODE]/course_material.pdf`
3. Restart application

## License

MIT License - see LICENSE file for details.
