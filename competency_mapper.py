import streamlit as st
import pandas as pd
from linkedin_scraper import get_jd_from_linkedin
from PyPDF2 import PdfReader
import os
import google.generativeai as genai
from dotenv import load_dotenv
from report_generator import create_radar_chart, create_pdf_report
from io import StringIO

# --- CONFIGURATION ---
st.set_page_config(page_title="AI-Fit Score Mapper", layout="wide", initial_sidebar_state="collapsed")
load_dotenv()

# Configure Gemini API
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except (AttributeError, TypeError):
    st.error("🚨 Google API Key not found. Please ensure it's set in your .env file.")
    st.stop()

# --- MODEL AND PROMPTS ---
model = genai.GenerativeModel("gemini-1.5-flash")

prompt_template = """
You are an expert ATS and career strategist. Your task is to perform a complete competency mapping of a resume against a job description.
The output must be structured in two parts separated by '---'.

Part 1: A valid CSV for the Competency Matrix with the following columns:
Skill/Keyword,Present in Resume (✅/❌),Competency Rating (1-10),Suggestion to Improve

Part 2: A Markdown-formatted report containing:
- **Overall Resume Match Score:** A percentage (out of 100).
- **Top 5 Matched Skills:** A bulleted list.
- **Top 5 Missing Skills:** A bulleted list.
- **Industry Benchmark Score:** A percentage (e.g., 75% for a senior role in tech).
- **Personalized AI Tip of the Day:** A single, actionable tip.
- **Final Review:** A summary paragraph.

**Input:**

**Job Description:**
{jd_text}

**Resume:**
{resume_text}

**Output:**
"""

# --- CORE FUNCTIONS ---
def get_gemini_response(prompt):
    try:
        response = model.generate_content(prompt, request_options={"timeout": 180})
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
        /* Modern UI Styles */
        .main .block-container { padding: 1rem 3rem; }
        h1 { font-size: 2.8rem; font-weight: 700; }
        h2 { font-size: 1.9rem; font-weight: 600; border-bottom: 3px solid #007bff; padding-bottom: 0.4rem; }
        .st-emotion-cache-1y4p8pa { max-width: 100%; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🎯 AI-Fit Score Dashboard")
    st.markdown("An intelligent platform to map your skills, score your fit, and coach you to success.")

    # --- Initialize Session State ---
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
        st.session_state.competency_df = pd.DataFrame()
        st.session_state.report_text = ""
        st.session_state.radar_chart = None

    # --- Input Section ---
    with st.expander("Step 1: Provide Inputs", expanded=not st.session_state.analysis_complete):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📄 Your Resume")
            resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"], label_visibility="collapsed")

        with col2:
            st.subheader("📝 The Job Description")
            jd_input_method = st.radio("Choose JD source:", ["Paste Manually", "Upload PDF", "LinkedIn URL"], horizontal=True, label_visibility="collapsed")
            
            job_description = ""
            if jd_input_method == "Paste Manually":
                job_description = st.text_area("Paste the job description:", height=210, label_visibility="collapsed")
            elif jd_input_method == "Upload PDF":
                jd_file = st.file_uploader("Upload JD (PDF)", type=["pdf"], label_visibility="collapsed")
                if jd_file:
                    job_description = extract_text_from_pdf(jd_file)
            else:
                linkedin_url = st.text_input("Enter LinkedIn job URL:", label_visibility="collapsed")
                if linkedin_url:
                    job_description = get_jd_from_linkedin(linkedin_url)

    if st.button("🚀 Analyze & Generate Dashboard", use_container_width=True, type="primary"):
        if job_description and resume_file:
            with st.spinner("AI is analyzing... Please wait a moment."):
                resume_text = extract_text_from_pdf(resume_file)
                if not resume_text:
                    st.error("Could not extract text from resume.")
                    st.stop()

                prompt = prompt_template.format(jd_text=job_description, resume_text=resume_text)
                analysis_result = get_gemini_response(prompt)

                if analysis_result and '---' in analysis_result:
                    csv_data, report_text = analysis_result.split('---', 1)
                    df = pd.read_csv(StringIO(csv_data))
                    
                    st.session_state.competency_df = df
                    st.session_state.report_text = report_text.strip()
                    st.session_state.radar_chart = create_radar_chart(df)
                    st.session_state.analysis_complete = True
                    st.rerun()
                else:
                    st.error("Failed to get a valid analysis from the AI model. Please try again.")
        else:
            st.warning("Please provide both a resume and a job description.")

    # --- Results Dashboard ---
    if st.session_state.analysis_complete:
        st.header("📊 Your Results Dashboard")
        
        tab1, tab2, tab3 = st.tabs(["📈 AI-Fit Score & Review", "📋 Competency Matrix", "📄 Full Report"])

        with tab1:
            st.subheader("AI-Fit Score & Review")
            if st.session_state.radar_chart:
                st.image(st.session_state.radar_chart, use_column_width=True)
            st.markdown(st.session_state.report_text)

        with tab2:
            st.subheader("Competency Matrix")
            st.dataframe(st.session_state.competency_df, use_container_width=True)

        with tab3:
            st.subheader("Full Report")
            st.markdown("### Competency Matrix")
            st.dataframe(st.session_state.competency_df, use_container_width=True)
            st.markdown("### Analysis & Review")
            st.markdown(st.session_state.report_text)
            
            # --- Download Button ---
            pdf_report = create_pdf_report(st.session_state.report_text, st.session_state.competency_df, st.session_state.radar_chart)
            st.download_button(
                label="📥 Download Full Report as PDF",
                data=pdf_report,
                file_name="AI_Fit_Score_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

if __name__ == "__main__":
    main()