import re
import logging
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2

class PDFExtractor:
    def __init__(self):
        self.name_pattern = re.compile(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)')
        self.title_pattern = re.compile(r'(?:CEO|CTO|CFO|Director|Manager|Head|Lead|Senior|Junior|Analyst|Consultant|Advisor|Specialist|Officer|Coordinator|Executive|President|Vice President|VP|MD|Managing Director|Chief|Partner|Principal|Associate|Assistant|Representative|Administrator|Supervisor|Coordinator|Consultant|Advisor|Specialist|Officer|Executive|President|Vice President|VP|MD|Managing Director|Chief|Partner|Principal|Associate|Assistant|Representative|Administrator|Supervisor)', re.IGNORECASE)
        self.email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
        self.website_pattern = re.compile(r'(?:https?://)?(?:www\.)?[\w.]+(?:\.[\w.]+)+(?:/[\w./?%&=-]*)?')
        self.linkedin_pattern = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+/?')

    def extract(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Extract contact information from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing extracted contact information
        """
        try:
            text = self._extract_text(pdf_path)
            return self._parse_text(text)
        except Exception as e:
            logging.error(f"Error extracting data from {pdf_path}: {str(e)}")
            return []

    def _extract_text(self, pdf_path: Path) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _parse_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse extracted text to find contact information."""
        contacts = []
        
        # Split text into potential contact blocks
        blocks = text.split('\n\n')
        
        for block in blocks:
            contact = {
                'company_name': self._extract_company_name(block),
                'contact_name': self._extract_name(block),
                'job_title': self._extract_title(block),
                'email': self._extract_email(block),
                'website': self._extract_website(block),
                'linkedin': self._extract_linkedin(block)
            }
            
            # Only add if we found at least some useful information
            if any(contact.values()):
                contacts.append(contact)
        
        return contacts

    def _extract_company_name(self, text: str) -> str:
        """Extract company name from text."""
        # Look for common company name patterns
        # This is a simplified version - you might want to enhance this
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['fund', 'pension', 'investment', 'management', 'ltd', 'inc', 'ag', 'sa']):
                return line.strip()
        return ""

    def _extract_name(self, text: str) -> str:
        """Extract person's name from text."""
        names = self.name_pattern.findall(text)
        return names[0] if names else ""

    def _extract_title(self, text: str) -> str:
        """Extract job title from text."""
        titles = self.title_pattern.findall(text)
        return titles[0] if titles else ""

    def _extract_email(self, text: str) -> str:
        """Extract email address from text."""
        emails = self.email_pattern.findall(text)
        return emails[0] if emails else ""

    def _extract_website(self, text: str) -> str:
        """Extract website URL from text."""
        websites = self.website_pattern.findall(text)
        return websites[0] if websites else ""

    def _extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn profile URL from text."""
        linkedin_urls = self.linkedin_pattern.findall(text)
        return linkedin_urls[0] if linkedin_urls else "" 