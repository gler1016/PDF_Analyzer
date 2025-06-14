import logging
import os
from pathlib import Path

def setup_logging():
    """Configure logging for the application."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )

def create_directories():
    """Create necessary directories for the application."""
    directories = [
        Path("input_pdfs"),
        Path("output"),
        Path("logs")
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        logging.info(f"Created directory: {directory}")

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special characters but keep basic punctuation
    text = "".join(c for c in text if c.isprintable())
    
    return text.strip()

def validate_email(email: str) -> bool:
    """Validate email address format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_url(url: str) -> bool:
    """Validate URL format."""
    import re
    pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url))

def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def is_valid_pdf(file_path: Path) -> bool:
    """Check if file is a valid PDF."""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(5)
            return header.startswith(b'%PDF-')
    except:
        return False 