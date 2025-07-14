import requests
from bs4 import BeautifulSoup
import streamlit as st

def get_jd_from_linkedin(url):
    """
    Extracts the job description text from a LinkedIn job posting URL.
    """
    if not url or "linkedin.com/jobs/view/" not in url:
        st.error("Please provide a valid LinkedIn job URL.")
        return None

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'lxml')

    # Find the main job description container
    # The class names on LinkedIn can change, so this might need updating.
    # Using a more generic selector to be more robust.
    job_description_div = soup.find('div', class_='description__text')

    if job_description_div:
        return job_description_div.get_text(separator='\\n').strip()
    else:
        # Fallback for different class names
        job_description_div = soup.find('section', class_='show-more-less-html')
        if job_description_div:
            return job_description_div.get_text(separator='\\n').strip()
        else:
            st.warning("Could not find the job description on the page. The page structure may have changed. Please paste the job description manually.")
            return None

if __name__ == '__main__':
    # Example usage for testing
    test_url = "https://www.linkedin.com/jobs/view/3971619535"  # Replace with a current, valid URL for testing
    jd = get_jd_from_linkedin(test_url)
    if jd:
        print("--- Job Description Extracted ---")
        print(jd)
        print("---------------------------------")
    else:
        print("Failed to extract job description.")