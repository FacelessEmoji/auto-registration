import logging
import time
from functools import wraps
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def check_and_click_modal_button(driver, account):
    try:
        modal_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Да') or contains(text(), 'Иә')]")
        if modal_button.is_displayed():
            modal_button.click()
            logging.info(f"Account {account['iin']}: Modal button clicked")
            time.sleep(0.5)
    except NoSuchElementException:
        logging.debug(f"Account {account['iin']}: Modal button not found")


def with_modal_check(func):
    @wraps(func)
    def wrapper(driver, account, *args, **kwargs):
        check_and_click_modal_button(driver, account)
        result = func(driver, account, *args, **kwargs)
        check_and_click_modal_button(driver, account)
        return result

    return wrapper
