import os
from PyPDF2 import PdfReader
import tkinter as tk
from tkinter import filedialog

def test_pdf_parser():
    """
    A diagnostic script to test the PDF text extraction functionality.
    It opens a file dialog to select a PDF and prints the extracted text.
    """
    print("--- Starting PDF Parser Test ---")

    # Set up a simple Tkinter root window (it won't be shown)
    root = tk.Tk()
    root.withdraw()

    # Open a file dialog to choose a PDF
    print("Please select a PDF file to test...")
    file_path = filedialog.askopenfilename(
        title="Select a Resume PDF",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not file_path:
        print("No file selected. Exiting test.")
        return

    print(f"▶️ Testing with file: {file_path}")

    try:
        with open(file_path, "rb") as f:
            pdf_reader = PdfReader(f)
            text = "".join(page.extract_text() or "" for page in pdf_reader.pages)

        if text:
            print("\\n--- ✅ PDF Parsed Successfully ---")
            print(f"Total characters extracted: {len(text)}")
            print("\\n--- First 500 Characters ---")
            print(text[:500] + "...")
            print("------------------------------")
        else:
            print("\\n--- ⚠️ PDF Parsed, but no text was extracted. ---")
            print("The PDF might be image-based or have non-standard encoding.")

    except Exception as e:
        print(f"\\n--- ❌ PDF PARSING FAILED ---")
        print(f"An error occurred: {e}")

    print("\\n--- PDF Parser Test Finished ---")

if __name__ == "__main__":
    test_pdf_parser()
