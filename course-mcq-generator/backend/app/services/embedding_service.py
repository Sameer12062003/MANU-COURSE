import os
import numpy as np
import faiss
from typing import List, Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        """Initialize the embedding service with Gemini embeddings"""
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.GEMINI_EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY
        )
        self.index = None
        self.chunks = []

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts"""
        try:
            # Get embeddings from Gemini
            embeddings = self.embeddings.embed_documents(texts)

            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)

            return embeddings_array

        except Exception as e:
            raise Exception(f"Error creating embeddings: {str(e)}")

    def create_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Create and train a FAISS index"""
        try:
            dimension = embeddings.shape[1]

            # Use IndexFlatL2 for exact search (suitable for smaller datasets)
            # For larger datasets, consider IndexIVFFlat
            if len(embeddings) > 10000:
                # Use IVF index for larger datasets
                nlist = min(100, len(embeddings) // 10)  # Number of clusters
                quantizer = faiss.IndexFlatL2(dimension)
                index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

                # Train the index
                index.train(embeddings)
            else:
                # Use flat index for smaller datasets
                index = faiss.IndexFlatL2(dimension)

            # Add vectors to index
            index.add(embeddings)

            return index

        except Exception as e:
            raise Exception(f"Error creating FAISS index: {str(e)}")

    def save_index(self, index: faiss.Index, index_path: str):
        """Save FAISS index to disk"""
        try:
            faiss.write_index(index, index_path)
        except Exception as e:
            raise Exception(f"Error saving FAISS index: {str(e)}")

    def load_index(self, index_path: str) -> faiss.Index:
        """Load FAISS index from disk"""
        try:
            if os.path.exists(index_path):
                return faiss.read_index(index_path)
            return None
        except Exception as e:
            raise Exception(f"Error loading FAISS index: {str(e)}")

    def build_vector_store(self, chunks: List[str], course_code: str) -> faiss.Index:
        """Build complete vector store for a course"""
        try:
            # Create embeddings
            print(f"Creating embeddings for {len(chunks)} chunks...")
            embeddings = self.create_embeddings(chunks)

            # Create FAISS index
            print("Creating FAISS index...")
            index = self.create_faiss_index(embeddings)

            # Save index and chunks for this course
            index_path = f"faiss_index_{course_code}.bin"
            self.save_index(index, index_path)

            # Store chunks for retrieval
            self.chunks = chunks
            self.index = index

            print(f"Vector store built successfully for course {course_code}")
            return index

        except Exception as e:
            raise Exception(f"Error building vector store: {str(e)}")

    def similarity_search(self, query: str, k: int = 5) -> List[str]:
        """Perform similarity search in the vector store"""
        try:
            if self.index is None:
                raise ValueError("Vector store not initialized")

            # Create embedding for query
            query_embedding = self.embeddings.embed_query(query)
            query_vector = np.array([query_embedding], dtype=np.float32)

            # Search in FAISS index
            distances, indices = self.index.search(query_vector, k)

            # Retrieve relevant chunks
            relevant_chunks = []
            for idx in indices[0]:
                if idx < len(self.chunks):
                    relevant_chunks.append(self.chunks[idx])

            return relevant_chunks

        except Exception as e:
            raise Exception(f"Error performing similarity search: {str(e)}")

    def get_relevant_context(self, course_content_chunks: List[str], num_questions: int) -> List[str]:
        """Get relevant context for MCQ generation"""
        try:
            # Build vector store if not exists
            if self.index is None:
                self.build_vector_store(course_content_chunks, "temp")

            # Create diverse queries to get comprehensive context
            queries = [
                "key concepts and definitions",
                "important topics and theories", 
                "main principles and methods",
                "fundamental concepts",
                "important examples and applications"
            ]

            relevant_chunks = set()

            # Get relevant chunks for each query
            for query in queries:
                chunks = self.similarity_search(query, k=3)
                relevant_chunks.update(chunks)

            # Ensure we have enough context
            if len(relevant_chunks) < num_questions * 2:
                # Add more random chunks to ensure sufficient context
                remaining_chunks = [chunk for chunk in course_content_chunks if chunk not in relevant_chunks]
                additional_needed = max(0, (num_questions * 3) - len(relevant_chunks))
                relevant_chunks.update(remaining_chunks[:additional_needed])

            return list(relevant_chunks)

        except Exception as e:
            raise Exception(f"Error getting relevant context: {str(e)}")

# Initialize embedding service
embedding_service = EmbeddingService()