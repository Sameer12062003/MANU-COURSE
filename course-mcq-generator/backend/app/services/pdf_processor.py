import os
import fitz  # PyMuPDF
import pdfplumber
from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def find_course_pdf(self, course_code: str) -> Optional[str]:
        """Find the PDF file for a given course code"""
        course_dir = os.path.join(settings.COURSE_PDF_DIR, course_code)

        if not os.path.exists(course_dir):
            return None

        # Look for PDF files in the course directory
        for file in os.listdir(course_dir):
            if file.lower().endswith('.pdf'):
                return os.path.join(course_dir, file)

        return None

    def extract_text_pymupdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""

            for page_num in range(doc.page_count):
                page = doc[page_num]
                text += page.get_text()
                text += "\n\n"  # Add page break

            doc.close()
            return text.strip()

        except Exception as e:
            raise Exception(f"Error extracting text with PyMuPDF: {str(e)}")

    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber (fallback method)"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                        text += "\n\n"

            return text.strip()

        except Exception as e:
            raise Exception(f"Error extracting text with pdfplumber: {str(e)}")

    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF using primary method with fallback"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            # Try PyMuPDF first
            return self.extract_text_pymupdf(pdf_path)
        except Exception:
            # Fallback to pdfplumber
            return self.extract_text_pdfplumber(pdf_path)

    def chunk_text(self, text: str) -> List[str]:
        """Split text into manageable chunks"""
        if not text.strip():
            raise ValueError("Empty text provided for chunking")

        chunks = self.text_splitter.split_text(text)

        # Filter out very short chunks
        chunks = [chunk for chunk in chunks if len(chunk.strip()) > 50]

        return chunks

    def process_course_pdf(self, course_code: str) -> List[str]:
        """Complete processing pipeline for a course PDF"""
        # Find PDF file
        pdf_path = self.find_course_pdf(course_code)
        if not pdf_path:
            raise FileNotFoundError(f"No PDF found for course: {course_code}")

        # Extract text
        text = self.extract_text(pdf_path)
        if not text.strip():
            raise ValueError(f"No text content extracted from PDF: {pdf_path}")

        # Chunk text
        chunks = self.chunk_text(text)
        if not chunks:
            raise ValueError(f"No valid chunks created from PDF: {pdf_path}")

        return chunks

# Initialize processor instance
pdf_processor = PDFProcessor()