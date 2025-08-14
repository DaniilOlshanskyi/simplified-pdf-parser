import re
import easyocr
from pdf2image import convert_from_path
import numpy as np
import streamlit as st
import tempfile
import os
import pandas as pd

# Common keys for form extraction - can be replaced with DB call later
COMMON_KEYS = [
    "Name", "First Name", "Last Name", "Full Name",
    "Policy Number", "Policy ID", "Reference Number",
    "Date of Birth", "DOB", "Birth Date",
    "Address", "Street Address", "City", "State", "ZIP", "Postal Code",
    "Phone", "Phone Number", "Mobile", "Telephone",
    "Email", "Email Address",
    "Date", "Incident Date", "Claim Date",
    "Amount", "Total Amount", "Premium",
    "Vehicle", "Make", "Model", "Year",
    "License", "License Number", "Driver License",
    "Gender", "Sex", "Occupation"
]

def extract_text_from_pdf(pdf_path: str, add_page_numbers: bool = True) -> str:
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
        
        if add_page_numbers:
            full_text += f"--- Page {i+1} ---\n"
        for (bbox, text, confidence) in results:
            full_text += text + "\n"
        full_text += "\n"
    return full_text

def search_keys_in_text(text: str, keys: list[str]) -> dict[str, str]:
    """Search for keys in OCR text and return key-value pairs."""
    lines = text.split('\n')
    results = {}
    keys_lower = [key.lower().strip() for key in keys]
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        if not line_lower:  # Skip empty lines
            continue
            
        for key_index, key in enumerate(keys_lower):
            if keys[key_index] not in results and line_lower == key:
                # Found the key, look for value in next non-empty line
                for j in range(i + 1, len(lines)):
                    potential_value = lines[j].strip()
                    if potential_value:  # Found non-empty line
                        results[keys[key_index]] = potential_value
                        break
                break  # Stop checking other keys for this line
    
    return results

def extract_alternating_key_values(text: str) -> dict[str, str]:
    """Extract key-value pairs by treating non-empty lines as alternating keys and values."""
    lines = text.split('\n')
    results = {}
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    # Process pairs of lines (key, value)
    for i in range(0, len(non_empty_lines) - 1, 2):
        key = non_empty_lines[i]
        value = non_empty_lines[i + 1] if i + 1 < len(non_empty_lines) else ""
        
        if key and value:  # Only add if both key and value exist
            results[key] = value
    
    return results

def display_and_download_results(found_values: dict[str, str], base_name: str, file_suffix: str, button_label: str):
    """Display results in table format and provide CSV download."""
    # Display results in a table format
    results_df = pd.DataFrame([
        {"Key": key, "Value": value} 
        for key, value in found_values.items()
    ])
    
    st.success(f"Found {len(found_values)} key-value pairs!")
    st.table(results_df)
    
    # Create CSV for download
    csv_data = results_df.to_csv(index=False)
    csv_filename = f"{base_name}_{file_suffix}.csv"
    
    st.download_button(
        label=button_label,
        data=csv_data,
        file_name=csv_filename,
        mime="text/csv"
    )

def main():
    st.title("PDF Key-Value Extraction")
    st.write("Upload a PDF file to extract key-value pairs")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Display file details
        st.write(f"**File name:** {uploaded_file.name}")
        st.write(f"**File size:** {uploaded_file.size} bytes")
        
        # Extraction mode selection
        st.subheader("Choose extraction mode:")
        
        extraction_mode = st.radio(
            "Select how you want to extract data:",
            options=[
                "I know the keys I need the values for!",
                "I don't know the keys, extract common ones",
                "I don't know the keys, extract everything"
            ],
            index=0,  # No default selection
            help="Choose the extraction method that best fits your needs. First option allows you to search for the keys. Second option uses a pre-defined list of common keys. Third option treats non-empty lines as alternating keys and values."
        )
        
        # Key input for mode 1
        search_keys = []
        if extraction_mode == "I know the keys I need the values for!":
            st.subheader("Select keys to search for:")
            
            # Multiselect with common options
            selected_keys = st.multiselect(
                "Choose from common keys:",
                options=COMMON_KEYS,
                help="Select multiple keys from the list or type custom keys below"
            )
            
            # Option to add custom keys
            custom_keys_input = st.text_input(
                "Add custom keys (comma-separated):",
                placeholder="e.g. Custom Field 1, Special Code, Other Info"
            )
            
            # Combine selected and custom keys
            if custom_keys_input.strip():
                custom_keys = [key.strip() for key in custom_keys_input.split(',') if key.strip()]
                search_keys = selected_keys + custom_keys
            else:
                search_keys = selected_keys
            
            if search_keys:
                st.write(f"**Keys to search for:** {', '.join(search_keys)}")
            else:
                st.info("Please select at least one key to search for.")
        
        # Process button
        if st.button("Extract Key-Value Pairs"):
            with st.spinner("Processing PDF... This may take a few moments."):
                try:
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_pdf_path = tmp_file.name
                    
                    # Extract text from PDF
                    if extraction_mode == "I don't know the keys, extract everything":
                        extracted_text = extract_text_from_pdf(tmp_pdf_path, add_page_numbers=False)
                    else:
                        extracted_text = extract_text_from_pdf(tmp_pdf_path)
                    
                    # Generate output filename based on uploaded file name
                    base_name = os.path.splitext(uploaded_file.name)[0]

                    # Clean up temporary file
                    os.unlink(tmp_pdf_path)
                    
                    # Show success message
                    # st.success(f"Extraction completed!")
                    
                    # Process based on selected mode
                    if extraction_mode == "I know the keys I need the values for!" and search_keys:
                        # Search for specific keys
                        st.subheader("Key-Value Search Results:")
                        found_values = search_keys_in_text(extracted_text, search_keys)
                        
                        if found_values:
                            display_and_download_results(
                                found_values, 
                                base_name, 
                                "key_search_results", 
                                "Download Key-Value Results (CSV)"
                            )
                        else:
                            st.warning("No matching keys found in the OCR text. Please check your keys or try different variations.")
                            
                        # Show expandable full text
                        with st.expander("View Full OCR Text"):
                            st.text_area("Complete OCR Results", extracted_text, height=300)
                    
                    elif extraction_mode == "I don't know the keys, extract common ones":
                        # Use all common keys for automatic extraction
                        st.subheader("Common Key-Value Extraction Results:")
                        
                        found_values = search_keys_in_text(extracted_text, COMMON_KEYS)
                        
                        if found_values:
                            display_and_download_results(
                                found_values, 
                                base_name, 
                                "common_keys_extraction", 
                                "Download Common Keys Results (CSV)"
                            )
                        else:
                            st.warning("No common keys found in the OCR text. The document might not contain standard form fields, or they might be formatted differently.")
                            
                                                # Show expandable full text
                        with st.expander("View Full OCR Text"):
                            st.text_area("Complete OCR Results", extracted_text, height=300)
                    
                    elif extraction_mode == "I don't know the keys, extract everything":
                        # Extract all text treating lines as alternating keys and values
                        st.subheader("Alternating Key-Value Extraction Results:")
                        st.info("Treating non-empty lines as alternating keys and values...")
                        
                        found_values = extract_alternating_key_values(extracted_text)
                        
                        if found_values:
                            display_and_download_results(
                                found_values, 
                                base_name, 
                                "alternating_extraction", 
                                "Download Alternating Extraction Results (CSV)"
                            )
                        else:
                            st.warning("No key-value pairs could be extracted. The document might not have enough content or proper structure.")
                            
                        # Show expandable full text
                        with st.expander("View Full OCR Text"):
                            st.text_area("Complete OCR Results", extracted_text, height=300)
 
                    else:
                        # Default behavior - show full extracted text
                        st.subheader("Extracted Text:")
                        st.text_area("OCR Results", extracted_text, height=300)
                        
                except Exception as e:
                    st.error(f"An error occurred during processing: {str(e)}")
                    # Clean up temporary file if it exists
                    if 'tmp_pdf_path' in locals() and os.path.exists(tmp_pdf_path):
                        os.unlink(tmp_pdf_path)

if __name__ == "__main__":
    main()
