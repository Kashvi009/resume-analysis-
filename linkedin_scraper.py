import requests
from bs4 import BeautifulSoup
import streamlit as st

def get_jd_from_linkedin(url: str) -> str | None:
    """
    Extracts the job description text from a LinkedIn job posting URL.

    Args:
        url: The URL of the LinkedIn job posting.

    Returns:
        The job description text as a string, or None if an error occurs.
    """
    if not url or "linkedin.com/jobs/view/" not in url:
        st.error("Invalid LinkedIn job URL provided.")
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'lxml')

    # Primary target for the main job description content
    job_description_div = soup.find('div', class_='description__text')
    if job_description_div:
        return job_description_div.get_text(separator='\\n').strip()

    # Fallback target if the primary class name isn't found
    job_description_div = soup.find('section', class_='show-more-less-html')
    if job_description_div:
        return job_description_div.get_text(separator='\\n').strip()

    st.warning("Could not automatically extract the job description. The page structure may have changed. Please paste it manually.")
    return None

if __name__ == '__main__':
    # This block is for direct testing of the scraper.
    # To use, run `python linkedin_scraper.py` in your terminal.
    test_url = "https://www.linkedin.com/jobs/view/3971619535"  # Replace with a valid, current URL for testing
    print(f"Attempting to scrape: {test_url}")
    jd = get_jd_from_linkedin(test_url)
    if jd:
        print("\\n--- Job Description Extracted Successfully ---")
        print(jd[:500] + "...") # Print first 500 chars
        print("--------------------------------------------")
    else:
        print("\\n--- Failed to extract job description. ---")