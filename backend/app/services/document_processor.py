"""Document processing service for extracting and chunking text."""
import io
from typing import List, Dict
from pathlib import Path
import aiofiles
from app.core.logging_config import logger


class DocumentProcessor:
    """Service for processing documents (PDF, DOCX, etc.)."""
    
    async def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            import PyPDF2
            
            text = ""
            async with aiofiles.open(file_path, "rb") as f:
                content = await f.read()
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise
    
    async def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            raise
    
    async def extract_text_from_url(self, url: str) -> str:
        """Extract text from URL."""
        try:
            import httpx
            from bs4 import BeautifulSoup
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "lxml")
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text()
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = "\n".join(chunk for chunk in chunks if chunk)
                
                return text
        except Exception as e:
            logger.error(f"URL extraction failed: {e}")
            raise
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> List[Dict[str, any]]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of chunk dicts with content, start_char, end_char
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            
            # Try to break at sentence boundary
            if end < text_length:
                # Look for sentence endings
                for punct in [". ", ".\n", "! ", "!\n", "? ", "?\n"]:
                    last_punct = text.rfind(punct, start, end)
                    if last_punct > start:
                        end = last_punct + len(punct)
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "content": chunk_text,
                    "start_char": start,
                    "end_char": end,
                })
            
            # Move start position with overlap
            start = end - chunk_overlap if end < text_length else end
        
        return chunks


# Singleton instance
document_processor = DocumentProcessor()
