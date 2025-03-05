"""
Document Extraction Agent Module
----------------------------------
This module provides the DocumentExtractionAgent class, which extracts text content
from uploaded documents in PDF, DOCX, and TXT formats.

External Libraries:
- PyMuPDF (imported as fitz) for PDF processing (pip install pymupdf)
- docx2txt for DOCX processing (pip install docx2txt)
- tempfile & os for handling temporary files for DOCX extraction
"""

import logging
import fitz  # PyMuPDF library for handling PDFs
import docx2txt  # Library to extract text from DOCX files
import tempfile
import os

class DocumentExtractionAgent:
    def __init__(self):
        """
        Initialize the DocumentExtractionAgent and configure logging.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.hasHandlers():
            logging.basicConfig(level=logging.INFO)

    def extract_text(self, file_obj):
        """
        Extract text from the provided file object.
        
        Supports PDF, DOCX, and TXT file types. The file_obj must have a 'name'
        attribute to determine its extension.

        :param file_obj: File-like object (PDF, DOCX, or TXT)
        :return: Extracted text as a string, or None if extraction fails.
        """
        # Determine the file extension from the file object's name
        try:
            file_name = file_obj.name
            file_extension = file_name.split('.')[-1].lower()
            self.logger.info(f"Processing file: {file_name} with extension: {file_extension}")
        except AttributeError:
            self.logger.error("Provided file object does not have a 'name' attribute.")
            return None

        text = ""
        try:
            if file_extension == 'pdf':
                # Read the entire file as bytes
                file_bytes = file_obj.read()
                # Open the PDF from bytes using PyMuPDF
                with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                    for page in doc:
                        text += page.get_text()
                self.logger.info("PDF text extraction completed.")

            elif file_extension == 'docx':
                # DOCX extraction requires a file path, so write the content to a temporary file.
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                    tmp.write(file_obj.read())
                    tmp.flush()
                    tmp_filename = tmp.name
                # Extract text using docx2txt
                text = docx2txt.process(tmp_filename)
                self.logger.info("DOCX text extraction completed.")
                # Clean up the temporary file after processing
                os.remove(tmp_filename)

            elif file_extension == 'txt':
                # For TXT files, attempt to read the content directly.
                try:
                    text = file_obj.read()
                except Exception:
                    # In case the file is in binary mode, decode the content.
                    file_obj.seek(0)
                    text = file_obj.read().decode("utf-8")
                self.logger.info("TXT text extraction completed.")

            else:
                self.logger.error(f"Unsupported file extension: {file_extension}")
                return None

        except Exception as e:
            self.logger.error(f"Error during text extraction: {e}")
            return None

        return text
