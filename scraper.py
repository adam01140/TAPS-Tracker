from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# Set up the WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Define the base URL and initial ticket number
base_url = "https://ucsc.aimsparking.com/tickets/"
plate_number = "9HXG851"
ticket_numbers = [f"24PK40010{i}" for i in range(3, 10)]

# Open the base URL
driver.get(base_url)
print("Opened base URL")

# Iterate over the ticket numbers
for ticket_number in ticket_numbers:
    try:
        # Find the plate_vin input field and enter the plate number
        plate_input = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.ID, "plate_vin"))
        )
        plate_input.clear()
        plate_input.send_keys(plate_number)
        print(f"Entered plate number: {plate_number}")

        # Find the ticket_number input field and enter the ticket number
        ticket_input = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.ID, "ticket_number"))
        )
        ticket_input.clear()
        ticket_input.send_keys(ticket_number)
        print(f"Entered ticket number: {ticket_number}")

        # Find and click the search button
        search_button = WebDriverWait(driver, 0).until(
            EC.element_to_be_clickable((By.ID, "search_ticket"))
        )
        driver.execute_script("arguments[0].click();", search_button)
        print(f"Clicked search button for ticket number: {ticket_number}")

        # Wait for the results to load
        time.sleep(1)

        # Check if the results page loaded by looking for a known element
        try:
            ticket_info = WebDriverWait(driver, 0).until(
                EC.presence_of_element_located((By.XPATH, "//h3[text()='Ticket Information']"))
            )
            print(" ")
            print("----------------------------------------------------------")
            print("************[  Ladies and gentlemen, we got 'em  ]**************")
            print("----------------------------------------------------------")
            issue_date_time = driver.find_element(By.XPATH, "//p[strong[text()='Issue Date and Time:']]").text
            current_status = driver.find_element(By.XPATH, "//p[strong[text()='Current Status:']]/span").text
            location = driver.find_element(By.XPATH, "//p[strong[text()='Location:']]").text
         
            # Print or store the scraped information
            print(f"Ticket Number: {ticket_number}")
            print(f"Issue Date and Time: {issue_date_time}")
            print(f"Current Status: {current_status}")
            print(f"Location: {location}")
            print(" ")
            print(" ")
        except TimeoutException:
            print(f"Ticket number {ticket_number}: Doesn't exist")
            print(" ")
        except Exception as e:
            print(f"Error scraping data for ticket number {ticket_number}: {e}")

        # Go back to the base URL to search for the next ticket
        driver.get(base_url)
        print(f"Returned to base URL for next search")

    except Exception as e:
        print(f"Error processing ticket number {ticket_number}: {e}")

# Close the WebDriver
driver.quit()
print("Closed WebDriver")
