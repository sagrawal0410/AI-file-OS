import os
import logging
from PyPDF2 import PdfReader
import docx

logging.basicConfig(level=logging.INFO)

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        #print("here")
        return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        #print("here")
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def extract_text_from_txt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            #print("here")
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
        return ""

def scan_directory(directory):
    documents = []
    #print(os.listdir(directory))
    for root, _, files in os.walk(directory):
        #print("here")
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif file.lower().endswith('.docx'):
                text = extract_text_from_docx(file_path)
            elif file.lower().endswith('.txt'):
                text = extract_text_from_txt(file_path)
            else:
                continue  # unsupported file type
            if text:
                documents.append({'path': file_path, 'text': text})
    return documents