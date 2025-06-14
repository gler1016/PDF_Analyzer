import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

from pdf_extractor import PDFExtractor
#from data_enricher import DataEnricher  # Skip enrichment
from excel_exporter import ExcelExporter
from utils import setup_logging, create_directories

def main():
    # Setup
    load_dotenv()
    setup_logging()
    create_directories()
    
    # Initialize components
    pdf_extractor = PDFExtractor()
    #data_enricher = DataEnricher()  # Skip enrichment
    excel_exporter = ExcelExporter()
    
    # Get list of PDF files
    input_dir = Path("input_pdfs")
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logging.error("No PDF files found in input_pdfs directory")
        return
    
    logging.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF
    all_contacts = []
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        try:
            # Extract data from PDF
            extracted_data = pdf_extractor.extract(pdf_file)
            
            # Skip enrichment
            for contact in extracted_data:
                contact['source_pdf'] = pdf_file.name
                contact['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            all_contacts.extend(extracted_data)
            
        except Exception as e:
            logging.error(f"Error processing {pdf_file.name}: {str(e)}")
            continue
    
    if not all_contacts:
        logging.error("No contacts were extracted from the PDFs")
        return
    
    # Export to Excel
    output_file = Path("output") / "contacts.xlsx"
    excel_exporter.export(all_contacts, output_file)
    
    logging.info(f"Successfully processed {len(all_contacts)} contacts")
    logging.info(f"Results saved to {output_file}")

if __name__ == "__main__":
    main() 