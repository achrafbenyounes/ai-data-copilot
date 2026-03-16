# context_loader.py
import pandas as pd
import fitz  # PyMuPDF

def extract_file_content(uploaded_file) -> str:
    """
    Returns a string representing the content of the uploaded file.
    Works for CSV, TXT, PDF.
    Always resets the file cursor before reading (defensive seek).
    """
    file_type = uploaded_file.name.split(".")[-1].lower()

    # FIX: always reset cursor before reading (defensive)
    uploaded_file.seek(0)

    if file_type == "csv":
        df = pd.read_csv(uploaded_file, nrows=50)  # first 50 rows only for context
        return df.to_string(index=False)

    elif file_type == "txt":
        return uploaded_file.read().decode("utf-8")[:5000]  # limit to 5000 chars

    elif file_type == "pdf":
        pdf_bytes = uploaded_file.read()
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in pdf_doc:
            text += page.get_text()
        return text[:5000]  # limit to 5000 chars

    else:
        return ""
