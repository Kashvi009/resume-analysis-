# Advanced-ATS-Resume-Checker

![image](https://github.com/user-attachments/assets/f915239c-efa0-40dd-967d-d72fc0506ca0)

### What's This All About?

75% of resumes never reach human eyes. They're killed by ATS (Applicant Tracking Systems).

This Advanced ATS Resume Checker is designed to help you beat the bots. It analyzes your resume against a job description to give you the insights you need to land more interviews.

### What Does It Do?

1.  **Similarity Score**: Calculates a percentage match between your resume and a job description.
2.  **Missing Keywords**: Identifies crucial keywords from the job description that are missing in your resume.
3.  **Improvement Suggestions**: Provides actionable, GPT-powered advice to enhance your resume's impact.

### Tech Stack

-   **Frontend**: Streamlit
-   **AI Brain**: Google's Gemini-1.5-Flash
-   **PDF Handling**: pypdf

### How to Use

1.  **Clone this repo:**
    ```bash
    git clone https://github.com/your-username/Advanced-ATS-Resume-Checker.git
    cd Advanced-ATS-Resume-Checker
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your Google API key:**
    Create a `.env` file in the root directory and add your key:
    ```
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

4.  **Run the app:**
    You can run either of the two available tools:

    **Original ATS Resume Checker:**
    ```bash
    streamlit run resumeATS.py
    ```

    **New Competency Skills Mapping Tool:**
    ```bash
    streamlit run competency_mapper.py
    ```

### Want to Contribute?

Contributions are welcome! Here's how you can help:

1.  Fork the repo
2.  Create your feature branch: `git checkout -b my-new-feature`
3.  Commit your changes: `git commit -am 'Add some feature'`
4.  Push to the branch: `git push origin my-new-feature`
5.  Submit a pull request

### License

MIT License. See `LICENSE` for more information.
