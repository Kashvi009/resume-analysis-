import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
from linkedin_scraper import get_jd_from_linkedin
from report_generator import create_pdf_report
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Advanced ATS Resume Checker - Human Resources Information System", layout="wide", initial_sidebar_state="auto")
load_dotenv()

# Configure Gemini API
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except (AttributeError, TypeError):
    st.error("🚨 Google API Key not found. Please ensure it's set in your .env file.")
    st.stop()

# --- MODEL AND PROMPTS ---
model = genai.GenerativeModel("gemini-2.5-flash-lite")

prompt_templates = {
    "Similarity Score": """
        You are an expert ATS. Analyze the resume against the job description.
        - **Overall Match Score:** Provide a percentage score.
        - **✅ Skills Matched:** List the key skills found in both the resume and JD.
        - **❌ Skills Missing:** List critical skills from the JD that are missing in the resume.
        - **📈 Recommended Additions:** Suggest specific skills or keywords to add.
        Resume: {resume_text}
        Job Description: {jd_text}
        """,
    "Competency Matrix": """
        You are an expert ATS. Create a competency matrix comparing the resume to the job description.
        The output should be a markdown table with the following columns:
        - Skill/Keyword
        - Present in Resume (✅/❌)
        - Competency Rating (1-10)
        - Suggestion to Improve
        Resume: {resume_text}
        Job Description: {jd_text}
        """,
    "Improvement Suggestions": """
        You are an expert career coach. Provide a detailed, bullet-pointed list of suggestions to improve the resume based on the job description.
        Focus on action verbs, quantifiable achievements, and tailoring.
        Resume: {resume_text}
        Job Description: {jd_text}
        """,
}

# --- CORE FUNCTIONS ---
def get_gemini_response(prompt):
    try:
        response = model.generate_content(prompt, request_options={"timeout": 120})
        return response.text
    except Exception as e:
        st.error(f"🚨 API Error: {e}")
        return None

def extract_text_from_pdf(uploaded_file):
    if uploaded_file:
        try:
            pdf_reader = PdfReader(uploaded_file)
            return "".join(page.extract_text() or "" for page in pdf_reader.pages)
        except Exception as e:
            st.error(f"Error reading PDF file: {e}")
    return None

# --- UI LAYOUT ---
def main():
    st.markdown("""
    <style>
        .main .block-container { padding: 1rem 3rem; }
        h1 { font-size: 2.8rem; font-weight: 700; }
        h2 { font-size: 1.9rem; font-weight: 600; border-bottom: 3px solid #007bff; padding-bottom: 0.4rem; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Inputs & Analysis")
        st.subheader("1. Job Description")
        jd_input_method = st.radio("Source:", ["Paste Manually", "Upload PDF", "LinkedIn URL"], key="jd_source")
        job_description = ""
        if jd_input_method == "Paste Manually":
            job_description = st.text_area("Paste the job description:", height=150, label_visibility="collapsed")
        elif jd_input_method == "Upload PDF":
            jd_file = st.file_uploader("Upload JD (PDF)", type=["pdf"], label_visibility="collapsed")
            if jd_file:
                job_description = extract_text_from_pdf(jd_file)
        else:
            linkedin_url = st.text_input("Enter LinkedIn job URL:", label_visibility="collapsed")
            if linkedin_url:
                job_description = get_jd_from_linkedin(linkedin_url)

        st.subheader("2. Your Resume")
        resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"], label_visibility="collapsed")

        st.subheader("3. Analysis Type")
        analysis_type = st.selectbox("Select:", list(prompt_templates.keys()), label_visibility="collapsed")
        
        analyze_button = st.button("Analyze Resume", use_container_width=True, type="primary")

    st.title("🚀 Advanced ATS Resume Checker")
    st.markdown("Get AI-powered feedback to optimize your resume and beat the bots.")

    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = ""

    if analyze_button:
        if job_description and resume_file:
            with st.spinner(f"Running '{analysis_type}' analysis..."):
                resume_text = extract_text_from_pdf(resume_file)
                if not resume_text:
                    st.error("Could not extract text from resume.")
                    st.stop()
                
                prompt = prompt_templates[analysis_type].format(jd_text=job_description, resume_text=resume_text)
                st.session_state.analysis_result = get_gemini_response(prompt)
        else:
            st.warning("Please provide a job description and a resume in the sidebar.")

    if st.session_state.analysis_result:
        st.header("📊 Analysis Report")
        st.markdown(st.session_state.analysis_result)
        
        empty_df = pd.DataFrame() # This tool doesn't generate a competency matrix for the PDF report
        pdf_report = create_pdf_report(st.session_state.analysis_result, empty_df, None, None)
        st.download_button(
            label="📥 Download Report as PDF",
            data=pdf_report,
            file_name=f"{analysis_type.replace(' ', '_')}_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("Provide your details in the sidebar and click 'Analyze' to begin.")

if __name__ == "__main__":
    main()
