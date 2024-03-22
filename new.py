import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore

BASE_URL = "https://www.paymycite.com/SearchAgency.aspx?agency=147&plate=&cite="

# Firebase initialization
cred = credentials.Certificate('defundtaps-firebase-adminsdk-l7ji6-497e092431.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_citation_details(citation_number, driver):
    driver.get(BASE_URL + str(citation_number))

    try:
        # Try to find the "Contest the Citation" button
        button = driver.find_element(By.ID, "DataGrid1_ctl02_cmdContest")

        # If button is found but is not interactable, log and continue to next citation
        if not button.is_displayed() or not button.is_enabled():
            return f"Citation number {citation_number} doesn't have a button"

        button.click()

        # Once on the details page, parse the content with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract required data
        cite_number = soup.find("span", {"id": "txtCiteNumber"}).text.strip()
        cite_date = soup.find("span", {"id": "txtCiteDate"}).text.strip()
        cite_time = soup.find("span", {"id": "txtCiteTime"}).text.strip()
        cite_location = soup.find("span", {"id": "txtVioLocation"}).text.strip()

        return cite_number, cite_date, cite_time, cite_location

    except NoSuchElementException:
        return f"Citation number {citation_number} doesn't have a button"
    except ElementNotInteractableException:
        return f"Citation number {citation_number} doesn't have a button"
    except Exception as e:
        return str(e)

def upload_to_firestore(cite_number, cite_date, cite_time, cite_location):
    doc_ref = db.collection('citations').document(cite_number)
    doc_ref.set({
        'citationNumber': cite_number,
        'timestamp': cite_date,
        'time': cite_time,
        'college': cite_location
    })

def main():
    # Set up the Selenium driver
    driver = webdriver.Chrome()

    # Read the valid citation ranges from the output of citations.py
    valid_ranges = [
        
        (388123456,388127706),
        (399123456,399129426),

    ]

    for start, end in valid_ranges:
        base_citation_number = start
        while base_citation_number <= end:
            details = get_citation_details(base_citation_number, driver)

            if isinstance(details, tuple):
                cite_number, cite_date, cite_time, cite_location = details
                print(f"[{cite_number}] occurred at [{cite_location}] at [{cite_time}] on [{cite_date}]")
                upload_to_firestore(cite_number, cite_date, cite_time, cite_location)
            else:
                print(details)

            base_citation_number += 1

    # Close the browser window when done
    driver.quit()

if __name__ == "__main__":
    main()
