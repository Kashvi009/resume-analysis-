import streamlit as st
import pandas as pd
from linkedin_scraper import get_jd_from_linkedin
from PyPDF2 import PdfReader
import os
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except AttributeError:
    st.error("Google API Key not found. Please make sure it's set in your .env file.")
    st.stop()

# --- MODEL AND PROMPTS ---
model = genai.GenerativeModel("gemini-1.5-flash")

prompt_template = """
You are an expert ATS and career strategist. Perform a complete competency mapping of a resume against a given job description.

**Tasks:**

1.  **Extract Top 10-15 Keywords:** From the job description, identify the most critical skills and competency keywords.
2.  **Competency Mapping Table:** Create a Markdown table comparing the extracted JD keywords against the resume.
    -   **Columns:**
        -   `Skill / Keyword`
        -   `Required in JD` (✅)
        -   `Present in Resume` (✅/❌)
        -   `Match Level` (High, Medium, Low, or Missing)
        -   `Competency Rating` (Score out of 10)
        -   `Suggestion to improve` (if missing or low)
3.  **Overall Scores:**
    -   **Top JD Keywords:** List the top 5 most relevant keywords.
    -   **Resume Match Score:** A percentage score (out of 100).
    -   **Competency Summary Rating:** A brief summary of the overall competency match.
4.  **Review Section:** A plain-language paragraph summarizing strengths, gaps, and what to improve.

**Input:**

**Job Description:**
{jd_text}

**Resume:**
{resume_text}

**Output:**
"""

# --- CORE FUNCTIONS ---
def get_gemini_response(prompt):
    """Generates content from the Gemini model."""
    try:
        response = model.generate_content(prompt, request_options={"timeout": 120})
        return response.text
    except Exception as e:
        st.error(f"An API error occurred: {e}")
        return None

def extract_text_from_pdf(uploaded_file):
    """Extracts text from an uploaded PDF file."""
    if uploaded_file:
        try:
            pdf_reader = PdfReader(uploaded_file)
            text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
            return text
        except Exception as e:
            st.error(f"Error reading PDF file: {e}")
    return None

# --- UI LAYOUT ---
def main():
    st.set_page_config(page_title="Competency Skills Mapper", layout="wide", initial_sidebar_state="collapsed")

    # --- Custom CSS for a modern look ---
    st.markdown("""
    <style>
        /* General Body and Font */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f2f6;
        }
        /* Main container */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        /* Notion/Figma inspired UI elements */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 10px;
            transition: border-color 0.2s;
        }
        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }
        .stButton>button {
            background-color: #007bff;
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            border: none;
            transition: background-color 0.2s;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        /* Custom headers */
        h1, h2, h3 {
            color: #1a1a1a;
        }
        /* Card-like sections */
        .stExpander {
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 1rem;
            background-color: #FFFFFF;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("Competency Skills Mapping Tool")
    st.markdown("Analyze your resume against a job description to identify skill gaps and strengths.")

    # --- Step 1: Job Description Input ---
    st.header("Step 1: Provide the Job Description")
    jd_input_method = st.radio("Choose input method:", ["Paste Manually", "Extract from LinkedIn URL"], horizontal=True)

    job_description = ""
    if jd_input_method == "Paste Manually":
        job_description = st.text_area("Paste the job description here:", height=250)
    else:
        linkedin_url = st.text_input("Enter the LinkedIn job URL:")
        if st.button("Extract Job Description"):
            with st.spinner("Extracting job description from LinkedIn..."):
                job_description = get_jd_from_linkedin(linkedin_url)
                if job_description:
                    st.text_area("Extracted Job Description:", value=job_description, height=250)

    # --- Step 2: Resume Upload ---
    st.header("Step 2: Upload Your Resume")
    resume_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

    # --- Step 3: Analysis ---
    if st.button("Analyze and Map Competencies", type="primary"):
        if job_description and resume_file:
            with st.spinner("Analyzing... This may take a moment."):
                resume_text = extract_text_from_pdf(resume_file)
                if not resume_text:
                    st.error("Could not extract text from the resume. Please try another file.")
                    st.stop()

                # --- Generate the analysis ---
                prompt = prompt_template.format(jd_text=job_description, resume_text=resume_text)
                analysis_result = get_gemini_response(prompt)

                if analysis_result:
                    st.header("Competency Mapping Results")
                    st.markdown(analysis_result)

                    # Bonus: Export to PDF (placeholder)
                    st.download_button(
                        label="Export Results as PDF",
                        data="PDF export feature coming soon!",
                        file_name="competency_report.txt",
                        mime="text/plain",
                    )
        else:
            st.warning("Please provide both a job description and a resume to start the analysis.")

if __name__ == "__main__":
    main()