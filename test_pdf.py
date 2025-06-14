from fpdf import FPDF
import os

def create_test_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Add title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Sample Pension Fund Contact Information', ln=True, align='C')
    pdf.ln(10)
    
    # Add contact information
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'Company: Swiss Pension Fund AG', ln=True)
    pdf.cell(0, 10, 'Website: www.swisspensionfund.ch', ln=True)
    pdf.cell(0, 10, 'Contact: John Smith', ln=True)
    pdf.cell(0, 10, 'Position: Investment Manager', ln=True)
    pdf.cell(0, 10, 'Email: john.smith@swisspensionfund.ch', ln=True)
    pdf.cell(0, 10, 'LinkedIn: linkedin.com/in/johnsmith', ln=True)
    
    # Save the PDF
    if not os.path.exists('input_pdfs'):
        os.makedirs('input_pdfs')
    pdf.output('input_pdfs/test_contact.pdf')
    print("Test PDF created successfully!")

if __name__ == '__main__':
    create_test_pdf() 