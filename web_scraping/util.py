from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (StaleElementReferenceException, TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

# html element IDs:
# Results Select Page select IDs
race_select_id = "default-lists-event_main_group"
division_select_id = "default-lists-event"
gender_select_id = "default-lists-sex"
num_results_select_id = "default-num_results"


def get_select(driver, select_id, retries=5, timeout=10):
    # print("Getting select with id:", select_id)
    for _ in range(retries):
        try:
            elem = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, select_id)))
            if elem.tag_name.lower() == "select":
                return Select(elem)
        except StaleElementReferenceException:
            print("StaleElementReferenceException")
            sleep(0.5)
    raise TimeoutException(f"Could not get select element with id '{select_id}' after {retries} retries.")


def get_names_from_select(race_select):
    race_names = []
    for option in race_select.options:
        race_names.append(option.text.strip())
    return race_names


def get_selenium_driver(url: str):
    driver = webdriver.Chrome()
    driver.get(url)
    return driver
