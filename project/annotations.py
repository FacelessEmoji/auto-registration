import logging
import time
from functools import wraps
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def check_and_click_modal_button(driver):
    try:
        modal_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Да') or contains(text(), 'Иә')]")
        if modal_button.is_displayed():
            modal_button.click()
    except NoSuchElementException:
        logging.debug(f"Modal button not found")


def with_modal_check(func):
    @wraps(func)
    def wrapper(driver, *args, **kwargs):
        check_and_click_modal_button(driver)
        result = func(driver, *args, **kwargs)
        check_and_click_modal_button(driver)
        return result

    return wrapper
