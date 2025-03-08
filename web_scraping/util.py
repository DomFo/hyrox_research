from time import sleep

from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select


def get_select(driver, select_id, retries=5, timeout=10):
    for _ in range(retries):
        try:
            elem = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, select_id))
            )
            if elem.tag_name.lower() == "select":
                return Select(elem)
        except StaleElementReferenceException:
            sleep(0.5)
    raise TimeoutException(f"Could not get select element with id '{select_id}' after {retries} retries.")
