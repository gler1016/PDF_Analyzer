# PDF Contact Extractor and Enricher

This project automates the extraction and enrichment of contact information from PDF documents, specifically focused on pension funds and financial institutions.

## Features

- PDF text extraction and parsing
- Company information extraction
- Contact person details extraction
- Website scraping for additional information
- LinkedIn profile URL extraction
- Email address verification
- Excel export with formatted data

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys (see `.env.example`)

## Usage

1. Place your PDF files in the `input_pdfs` directory
2. Run the main script:
   ```bash
   python main.py
   ```
3. Find the enriched data in `output/contacts.xlsx`

## Project Structure

- `main.py`: Main script to run the extraction and enrichment process
- `pdf_extractor.py`: PDF text extraction and parsing
- `data_enricher.py`: Data enrichment using various APIs and web scraping
- `excel_exporter.py`: Excel file generation and formatting
- `utils.py`: Utility functions and helpers

## Requirements

- Python 3.8+
- Chrome/Firefox browser (for web scraping)
- Internet connection (for data enrichment)
- API keys for enrichment services (optional)

## Output Format

The generated Excel file will contain the following columns:
- Company Name
- Company Website
- Contact Person Full Name
- Job Title/Role
- LinkedIn Profile URL
- Email Address
- Source PDF
- Last Updated 