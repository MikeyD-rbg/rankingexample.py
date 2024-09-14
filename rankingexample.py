import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import keyboard

# User credentials
USERNAME = 'XXXXXX'
PASSWORD = 'XXXXXX'

# Paths
chrome_driver_path = r"C:\Users\micha\Documents\PythonProgramming\IG\chromedriver-win64\chromedriver.exe"
brave_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Global variables for pause functionality
paused = False
pause_condition = threading.Condition()

def setup_webdriver():
    options = webdriver.ChromeOptions()
    options.binary_location = brave_path
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def is_logged_in(driver):
    try:
        logout_link = driver.find_element(By.XPATH, "//a[contains(@href, 'logout')]")
        return logout_link.is_displayed()
    except Exception:
        return False

def login(driver, wait):
    driver.get("https://www.infamousgangsters.com/")
    if is_logged_in(driver):
        logging.info("Already logged in.")
        return

    username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']")))
    login_button.click()

    if is_logged_in(driver):
        logging.info("Login successful.")
    else:
        logging.error("Login failed. Please check your credentials or the website's login process.")

def select_crime_checkboxes(driver, wait):
    try:
        driver.get("http://www.infamousgangsters.com/site.php?page=crimes")
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][name*=' ']")
        
        for checkbox in checkboxes:
            if checkbox.is_displayed() and checkbox.is_enabled():
                checkbox.click()
        
        logging.info("Crime checkboxes selected successfully.")
    except Exception as e:
        logging.error(f"Error selecting crime checkboxes: {e}")

    try:
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @name='submit' and @value='Commit!']")))
        submit_button.click()
    except Exception as e:
        logging.error(f"Error clicking submit button: {e}")

def perform_actions(driver, wait):
    driver.get("http://www.infamousgangsters.com/site.php?page=crimes")
    select_crime_checkboxes(driver, wait)

    driver.get("http://www.infamousgangsters.com/site.php?page=gta")
    steal_car_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Steal a car!']")))
    steal_car_button.click()

    driver.get("http://www.infamousgangsters.com/site.php?page=bullets")
    # Select the second radio button for melting the car
    melt_car_radios = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@type='radio' and @name='meltcar']")))
    if len(melt_car_radios) >= 2:
        melt_car_radios[1].click()
    else:
        logging.error("Not enough cars available to melt the second one.")
        return

    melt_car_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @name='melt' and @value='Melt car!']")))
    melt_car_button.click()

    driver.get("http://www.infamousgangsters.com/site.php?page=oc")
    accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @name='Submit' and @value='Accept']")))
    accept_button.click()

def toggle_pause():
    global paused
    with pause_condition:
        paused = not paused
        if paused:
            logging.info("Script paused. Press CTRL + ALT + C to continue.")
        else:
            logging.info("Script resumed.")
            pause_condition.notify()

def main():
    driver = setup_webdriver()
    wait = WebDriverWait(driver, 10)
    
    login(driver, wait)
    
    # Set up keyboard listeners
    keyboard.add_hotkey('ctrl+alt+p', toggle_pause)
    keyboard.add_hotkey('ctrl+alt+c', toggle_pause)
    
    while True:
        try:
            with pause_condition:
                while paused:
                    pause_condition.wait()
            
            perform_actions(driver, wait)
            logging.info("Waiting for 20 seconds before next iteration...")
            time.sleep(20)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
    
    driver.quit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script terminated by user.")