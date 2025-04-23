import logging
import json
import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Set up logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
PDF_FOLDER = "case_pdfs"
BASE_URL = "https://indiankanoon.org/search/?formInput=corporate%20%20doctypes%3A%20judgments+year:2024"
# BASE_URL = "https://indiankanoon.org/search/?formInput=corporate%20%20%20%20%20%20%20doctypes%3A%20judgments%20year%3A%202024&pagenum=22"
JSON_FILENAME = "corporate_cases_law_2024.json"

# Create necessary directories
os.makedirs(PDF_FOLDER, exist_ok=True)


def setup_driver():
    """Set up the Selenium WebDriver with headless options."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    prefs = {
        "download.default_directory": os.path.abspath(PDF_FOLDER),  # Set your custom directory
        "download.prompt_for_download": False,  # Disable download prompt
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # Ensures PDF is downloaded instead of opened
    }
    options.add_experimental_option("prefs", prefs)

    logging.debug("Initializing WebDriver...")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def open_page(driver, url):
    """Open a webpage and wait until it's fully loaded."""
    print(f"Opening URL: {url}")
    driver.get(url)
    WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(2)


def extract_cases(driver):
    """Extract case details from the current page."""
    cases = []

    results_content = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "results_content"))
    )
    results_middle = results_content.find_element(By.CLASS_NAME, "results_middle")
    case_elements = results_middle.find_elements(By.CLASS_NAME, "result")

    for case in case_elements:
        try:
            title_element = case.find_element(By.CLASS_NAME, "result_title").find_element(By.TAG_NAME, "a")
            title = title_element.text.strip()
            link = title_element.get_attribute("href")
            cases.append({"title": title, "link": link})
        except Exception as e:
            logging.error(f"Error extracting case: {e}")

    return cases


def get_secondary_link(driver, case_url):
    """Retrieve the secondary document link if available."""
    driver.get(case_url)
    time.sleep(2)

    try:
        doc_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "docfragment_title"))
        )
        return doc_title.find_element(By.TAG_NAME, "a").get_attribute("href")
    except Exception as e:
        logging.error(f"No secondary document link for {case_url}: {e}")
        return None


def download_pdf(driver, secondary_link,title):
    """Find and return the PDF URL from the secondary document page."""
    driver.get(secondary_link)
    time.sleep(2)
    
    pdf_filename = os.path.join(PDF_FOLDER, f"{title}.pdf")
    
    # Check if the file already exists
    if os.path.exists(pdf_filename):
        print(f"PDF already exists: {pdf_filename}. Skipping download.")
        return None

    try:
        pdf_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "pdfdoc"))
        )
        pdf_button.click()
        time.sleep(2)  # Allow time for redirection
        print(f"PDF saved: {pdf_filename}")
    except Exception as e:
        logging.error(f"Could not find PDF button: {e}")


def get_next_page_url(driver):
    """Get the URL of the next page if available."""
    try:
        time.sleep(5)
        pagination_div = driver.find_element(By.CLASS_NAME, "bottom")
        next_button = pagination_div.find_element(By.LINK_TEXT, "Next")
        return next_button.get_attribute("href")
    except Exception:
        print("No 'Next' button found.")
        return None


def main():
    driver = setup_driver()
    open_page(driver, BASE_URL)
    cases = []

    while True:
        print("Scraping current page...")
        page_cases = extract_cases(driver)
        
        for case in page_cases:
            
            current_page_url = driver.current_url  

            secondary_link = get_secondary_link(driver, case["link"])
            if secondary_link:
                download_pdf(driver, secondary_link,case["title"])
                # if pdf_url:
                #     download_pdf(pdf_url, case["title"])
            
            open_page(driver, current_page_url)  
            time.sleep(2)
            
        cases.extend(page_cases)
        
        
        next_page_url = get_next_page_url(driver)
        if not next_page_url:
            break
        open_page(driver, next_page_url)

    with open(JSON_FILENAME, "w", encoding="utf-8") as file:
        json.dump(cases, file, indent=4, ensure_ascii=False)

    print(f"Scraping completed! Data saved in {JSON_FILENAME}")
    driver.quit()


if __name__ == "__main__":
    main()