import os
from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from pathlib import Path
import logging
from datetime import datetime
from pdf_extractor import PDFExtractor
from excel_exporter import ExcelExporter
from utils import setup_logging, create_directories, is_valid_pdf
import tempfile

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flashing messages

# Configure upload settings
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / "input_pdfs"
OUTPUT_FOLDER = Path(tempfile.gettempdir()) / "output"
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories
for directory in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    Path(directory).mkdir(exist_ok=True)
    logging.info(f"Created directory: {directory}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        files = request.files.getlist('file')
        
        if not files or files[0].filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        uploaded_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = app.config['UPLOAD_FOLDER'] / filename
                file.save(file_path)
                uploaded_files.append(filename)
            else:
                flash(f'Invalid file type: {file.filename}. Only PDF files are allowed.')
        
        if uploaded_files:
            flash(f'Successfully uploaded: {", ".join(uploaded_files)}')
            return redirect(url_for('process_files'))
    
    return render_template('upload.html')

@app.route('/process')
def process_files():
    try:
        # Initialize components
        pdf_extractor = PDFExtractor()
        excel_exporter = ExcelExporter()
        
        # Get list of PDF files
        pdf_files = list(app.config['UPLOAD_FOLDER'].glob("*.pdf"))
        
        if not pdf_files:
            flash('No PDF files found in input_pdfs directory')
            return redirect(url_for('upload_file'))
        
        # Process each PDF
        all_contacts = []
        for pdf_file in pdf_files:
            try:
                # Extract data from PDF
                extracted_data = pdf_extractor.extract(pdf_file)
                
                # Add source information
                for contact in extracted_data:
                    contact['source_pdf'] = pdf_file.name
                    contact['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                all_contacts.extend(extracted_data)
                
            except Exception as e:
                flash(f'Error processing {pdf_file.name}: {str(e)}')
                continue
        
        if not all_contacts:
            flash('No contacts were extracted from the PDFs')
            return redirect(url_for('upload_file'))
        
        # Export to Excel
        output_file = OUTPUT_FOLDER / "contacts.xlsx"
        excel_exporter.export(all_contacts, output_file)
        
        flash(f'Successfully processed {len(all_contacts)} contacts')
        return send_file(output_file, as_attachment=True)
        
    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(url_for('upload_file'))

@app.route('/clear', methods=['POST'])
def clear_files():
    try:
        # Clear input_pdfs directory
        for file in app.config['UPLOAD_FOLDER'].glob("*.pdf"):
            file.unlink()
        flash('All uploaded files have been cleared')
    except Exception as e:
        flash(f'Error clearing files: {str(e)}')
    return redirect(url_for('upload_file'))

# For local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False) 