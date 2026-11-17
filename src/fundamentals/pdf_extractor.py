"""
PDF Text Extraction Engine.
Extracts clean textual contents from BSE corporate announcement PDF filings.
"""

from pathlib import Path
from typing import Optional
import io
import httpx
from pypdf import PdfReader


class PDFAnnouncementExtractor:
    """Extracts text from local or remote announcement PDF files."""

    def __init__(self):
        self.client = httpx.Client(timeout=15.0, headers={"User-Agent": "Mozilla/5.0"})

    def extract_from_bytes(self, pdf_bytes: bytes, max_pages: int = 5) -> str:
        """Extracts text from PDF byte buffer."""
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text_parts = []
            num_pages = min(len(reader.pages), max_pages)

            for i in range(num_pages):
                page_text = reader.pages[i].extract_text()
                if page_text:
                    text_parts.append(page_text.strip())

            return "\n\n".join(text_parts)
        except Exception as e:
            return f"Error extracting PDF: {e}"

    def extract_from_file(self, file_path: Path, max_pages: int = 5) -> str:
        """Extracts text from a local PDF file."""
        if not file_path.exists():
            return ""
        with open(file_path, "rb") as f:
            return self.extract_from_bytes(f.read(), max_pages=max_pages)

    def extract_from_url(self, url: str, max_pages: int = 5) -> str:
        """Downloads remote PDF and extracts text."""
        try:
            resp = self.client.get(url)
            if resp.status_code == 200:
                return self.extract_from_bytes(resp.content, max_pages=max_pages)
            return ""
        except Exception:
            return ""

