# -------------------------------
# AI Data Copilot - First MVP (Refactored)
# -------------------------------

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import fitz

from core.ai.context_loader import extract_file_content
from core.ai.ai_brain_with_api import query_ai

# -------------------------------
# Helper functions
# -------------------------------

def read_csv(file) -> pd.DataFrame:
    file.seek(0)
    return pd.read_csv(file)

def read_txt(file) -> str:
    file.seek(0)
    return file.read().decode("utf-8")

def read_pdf(file) -> str:
    file.seek(0)
    pdf_bytes = file.read()
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "".join([page.get_text() for page in pdf_doc])

def process_file(file):
    """Detect file type and process accordingly"""
    file_type = file.name.split(".")[-1].lower()
    st.write(f"File type detected: {file_type}")

    if file_type == "csv":
        df = read_csv(file)
        st.subheader("Preview of dataset")
        st.dataframe(df.head())
        return df
    elif file_type == "txt":
        text = read_txt(file)
        st.subheader("Text content preview")
        st.text(text[:1000])
        return text
    elif file_type == "pdf":
        text = read_pdf(file)
        st.subheader("PDF text preview")
        st.text(text[:1000])
        return text
    else:
        st.error("Unsupported file type!")
        return None

# -------------------------------
# Streamlit UI
# -------------------------------

st.title("AI Data Copilot")

uploaded_file = st.file_uploader(
    "Upload a file (CSV, TXT, PDF)",
    type=["csv", "txt", "pdf"]
)

if uploaded_file:
    content = process_file(uploaded_file)

    if content is not None:
        user_question = st.text_input("Ask AI about your file / Posez une question à l'IA")

        if user_question and user_question.strip():

            uploaded_file.seek(0)
            file_context = extract_file_content(uploaded_file)

            full_prompt = f"Here is the content of the file:\n{file_context}\n\nAnswer the question: {user_question}"

            st.subheader("AI Answer / Réponse IA")

            # FIX: spinner to show the user the AI is working
            with st.spinner("Llama3 is thinking... please wait ⏳"):
                answer = query_ai(full_prompt)

            st.markdown(answer)
