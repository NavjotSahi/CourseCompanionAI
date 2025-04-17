# backend/api/chatbot_utils.py

import os
import PyPDF2
import docx
from langchain.text_splitter import RecursiveCharacterTextSplitter


def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text


def extract_text_from_docx(file_path):
    """Extracts text from a DOCX file."""
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
    return text


def extract_text_from_txt(file_path):
    """Extracts text from a TXT file."""
    text = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
    return text


def process_and_embed_document(file_path, course_id, original_filename, vectorstore, embeddings_model):
    """
    Extracts text, splits into chunks, embeds, and adds to vector store.
    Requires external vectorstore and embeddings_model to be passed in.
    """
    if not vectorstore or not embeddings_model:
        print("ERROR (process_and_embed_document): Vectorstore or embeddings model not provided.")
        return False

    _, extension = os.path.splitext(file_path)
    extension = extension.lower()
    text = ""

    if extension == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif extension == ".docx":
        text = extract_text_from_docx(file_path)
    elif extension == ".txt":
        text = extract_text_from_txt(file_path)
    else:
        print(f"Unsupported file type: {extension}")
        return False

    if not text:
        print("No text extracted from file.")
        return False

    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        if not chunks:
            print("Text splitting resulted in no chunks.")
            return False

        metadatas = [{'course_id': str(course_id), 'source': original_filename} for _ in chunks]
        base_id = f"doc_{course_id}_{original_filename.replace(' ', '_')}"
        ids = [f"{base_id}_{i}" for i in range(len(chunks))]

        print(f"Adding {len(chunks)} chunks from {original_filename} for course {course_id} to vector store...")
        vectorstore.add_texts(texts=chunks, metadatas=metadatas, ids=ids)
        print("Successfully added document chunks to vector store.")
        return True

    except Exception as e:
        print(f"Error during chunking, embedding or vector store addition: {e}")
        return False
