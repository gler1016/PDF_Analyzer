import os
from flask import Flask, request, render_template, send_file, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from pathlib import Path
import logging
from datetime import datetime
from pdf_extractor import PDFExtractor
from excel_exporter import ExcelExporter
from utils import setup_logging, create_directories, is_valid_pdf
import tempfile
import io
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Configure upload settings
ALLOWED_EXTENSIONS = {'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# In-memory storage for files
file_storage = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
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
                file_id = str(uuid.uuid4())
                file_content = file.read()
                file_storage[file_id] = {
                    'filename': filename,
                    'content': file_content
                }
                uploaded_files.append(filename)
            else:
                flash(f'Invalid file type: {file.filename}. Only PDF files are allowed.')
        
        if uploaded_files:
            session['uploaded_files'] = list(file_storage.keys())
            flash(f'Successfully uploaded: {", ".join(uploaded_files)}')
            return redirect(url_for('process_files'))
    
    return render_template('upload.html')

@app.route('/process')
def process_files():
    try:
        if 'uploaded_files' not in session:
            flash('No files to process')
            return redirect(url_for('upload_file'))

        # Initialize components
        pdf_extractor = PDFExtractor()
        excel_exporter = ExcelExporter()
        
        # Process each PDF
        all_contacts = []
        for file_id in session['uploaded_files']:
            if file_id not in file_storage:
                continue
                
            file_data = file_storage[file_id]
            try:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    temp_file.write(file_data['content'])
                    temp_file.flush()
                    
                    # Extract data from PDF
                    extracted_data = pdf_extractor.extract(Path(temp_file.name))
                    
                    # Add source information
                    for contact in extracted_data:
                        contact['source_pdf'] = file_data['filename']
                        contact['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    all_contacts.extend(extracted_data)
                    
                # Clean up temporary file
                os.unlink(temp_file.name)
                
            except Exception as e:
                flash(f'Error processing {file_data["filename"]}: {str(e)}')
                continue
        
        if not all_contacts:
            flash('No contacts were extracted from the PDFs')
            return redirect(url_for('upload_file'))
        
        # Create Excel file in memory
        output = io.BytesIO()
        excel_exporter.export(all_contacts, output)
        output.seek(0)
        
        # Clear processed files
        session.pop('uploaded_files', None)
        file_storage.clear()
        
        flash(f'Successfully processed {len(all_contacts)} contacts')
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='contacts.xlsx'
        )
        
    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(url_for('upload_file'))

@app.route('/clear', methods=['POST'])
def clear_files():
    try:
        session.pop('uploaded_files', None)
        file_storage.clear()
        flash('All uploaded files have been cleared')
    except Exception as e:
        flash(f'Error clearing files: {str(e)}')
    return redirect(url_for('upload_file'))

# For local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False) 