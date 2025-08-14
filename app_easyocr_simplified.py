import easyocr
from pdf2image import convert_from_path
import numpy as np

# Set the PDF file name here
PDF_FILE_NAME = ""

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using EasyOCR."""
    # Initialize EasyOCR reader
    reader = easyocr.Reader(['en'])
    
    # Convert PDF to images
    images = convert_from_path(pdf_path)
    
    # Extract text from each page
    full_text = ""
    for i, image in enumerate(images):
        # Convert PIL image to numpy array for EasyOCR
        image_array = np.array(image)
        results = reader.readtext(image_array)
        
        full_text += f"--- Page {i+1} ---\n"
        for (bbox, text, confidence) in results:
            full_text += text + "\n"
        full_text += "\n"
    
    return full_text

if __name__ == "__main__":
    # Extract text from PDF
    extracted_text = extract_text_from_pdf(PDF_FILE_NAME)
    
    # Save output to file
    output_filename = f"{PDF_FILE_NAME.replace('.pdf', '')}_easyocr_output.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(extracted_text)
    
    print(f"EasyOCR extraction completed. Output saved to: {output_filename}")
