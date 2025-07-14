import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except AttributeError as e:
    st.error("Google API Key not found. Please make sure it's set in your .env file.")
    st.stop()

# --- MODEL AND PROMPTS ---
model = genai.GenerativeModel("gemini-1.5-flash")

prompt_templates = {
    "similarity": """
        You are an expert ATS. Compare the resume against the job description and calculate a percentage match score.
        Explain the reasoning for the score, highlighting areas of strong alignment and areas for improvement.
        Resume: {resume_text}
        Job Description: {jd_text}
        """,
    "missing_keywords": """
        You are an expert ATS. Analyze the resume and the job description.
        Identify and list the top 10 most critical keywords and skills from the job description that are missing in the resume.
        For each missing keyword, provide a brief suggestion on how to incorporate it naturally into the resume.
        Resume: {resume_text}
        Job Description: {jd_text}
        """,
    "improvement": """
        You are an expert career coach. Review the resume in the context of the job description.
        Provide a detailed, bullet-pointed list of suggestions to improve the resume.
        Focus on action verbs, quantifiable achievements, and tailoring the content to the job description.
        Provide specific examples of improved bullet points.
        Resume: {resume_text}
        Job Description: {jd_text}
        """,
    "competency_mapping": """
        You are an expert ATS and career strategist. I want you to perform a complete competency mapping of a resume against a given job description.

        Please do the following tasks:

        1. **Competency Mapping Table**:
           - Create a table comparing skills/keywords found in the resume and job description.
           - Columns should include:
             - Competency Area
             - Required in JD (Yes/No)
             - Present in Resume (Yes/No)
             - Match Level (High, Medium, Low, or Missing)
             - Suggestion to improve (if missing or low match)

        2. **Missing Keywords**:
           - List the top 10 most important keywords or skills from the job description that are not present in the resume.
           - For each, suggest how to incorporate it naturally into the resume.

        3. **Overall Match Rating**:
           - Give a match percentage between 0–100 based on how well the resume aligns with the job.
           - Use a weighted scoring method giving more importance to core job skills and competencies.

        4. **Score Justification Using Nash Equilibrium**:
           - Assume the job seeker and employer are players in a game.
           - Justify the score using the concept of Nash Equilibrium: If both keep their strategies (resume vs JD), is it a stable match? If not, what should the resume update (strategy shift) to improve stability?

        5. **Design Feedback**:
           - Based on the resume content, suggest improvements in layout, UI, or structure.
           - Use ATS-friendly principles but also consider design appeal (if a human recruiter is reading).

        Make your output clear and easy to read. Use bullet points or Markdown formatting if supported. Be as specific as possible.

        Resume:
        {resume_text}

        Job Description:
        {jd_text}
        """
}

# --- CORE FUNCTIONS ---
@st.cache_data(show_spinner=False)
def get_cached_response(prompt):
    return get_gemini_response(prompt)

def get_gemini_response(prompt):
    """Generates content from the Gemini model."""
    try:
        # Add a timeout of 60 seconds to the request
        request_options = {"timeout": 60}
        response = model.generate_content(prompt, request_options=request_options)
        return response.text
    except Exception as e:
        # Check if the error is a timeout error
        if "DeadlineExceeded" in str(e) or "timeout" in str(e).lower():
            st.error("The request to the AI model timed out after 60 seconds. This could be due to a network issue or the model taking too long to respond. Please check your internet connection and try again.")
        else:
            st.error(f"An API error occurred. Please check your API key and network connection. Details: {e}")
        return None

def extract_text_from_pdf(uploaded_file):
    """Extracts text from an uploaded PDF file."""
    if uploaded_file is not None:
        try:
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            st.error(f"Error reading PDF file: {e}")
            return None
    return None

# --- UI LAYOUT ---
def main():
    st.set_page_config(page_title="Advanced ATS Resume Checker", layout="wide")
    st.title("Advanced ATS Resume Checker")
    st.subheader("Get a competitive edge by optimizing your resume for any job.")

    # Custom CSS
    st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stTextArea>div>div>textarea {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.header("Your Resume")
        resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"], label_visibility="collapsed")

    with col2:
        st.header("Job Description")
        job_description = st.text_area("Paste the job description", height=300, label_visibility="collapsed")

    if resume_file and job_description:
        resume_text = extract_text_from_pdf(resume_file)
        if not resume_text:
            st.error("Could not extract text from the resume. Please try another file.")
            st.stop()

        st.markdown("---")
        st.header("Choose Your Analysis")

        analysis_col1, analysis_col2, analysis_col3, analysis_col4 = st.columns(4)

        with analysis_col1:
            if st.button("Similarity Score"):
                with st.spinner("Calculating similarity score..."):
                    prompt = prompt_templates["similarity"].format(resume_text=resume_text, jd_text=job_description)
                    response = get_gemini_response(prompt)
                    st.subheader("Similarity Score & Analysis")
                    st.markdown(response)

        with analysis_col2:
            if st.button("Missing Keywords"):
                with st.spinner("Identifying missing keywords..."):
                    prompt = prompt_templates["missing_keywords"].format(resume_text=resume_text, jd_text=job_description)
                    response = get_gemini_response(prompt)
                    st.subheader("Missing Keywords")
                    st.markdown(response)

        with analysis_col3:
            if st.button("Improvement Suggestions"):
                with st.spinner("Generating improvement suggestions..."):
                    prompt = prompt_templates["improvement"].format(resume_text=resume_text, jd_text=job_description)
                    response = get_gemini_response(prompt)
                    st.subheader("Resume Improvement Suggestions")
                    st.markdown(response)

        with analysis_col4:
            if st.button("Competency Mapping"):
                with st.spinner("Performing Competency Mapping..."):
                    prompt = prompt_templates["competency_mapping"].format(resume_text=resume_text, jd_text=job_description)
                    response = get_gemini_response(prompt)
                    st.subheader("Competency Mapping & Nash Scoring")
                    st.markdown(response)
    else:
        st.info("Please upload a resume and paste a job description to enable analysis.")

if __name__ == "__main__":
    main()
