from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
import time
import logging


def is_502_error_page(driver):
    try:
        error_element = driver.find_element(By.XPATH, "//h1[contains(text(), '502 Bad Gateway')]")
        return error_element is not None
    except Exception as e:
        logging.debug(f"Error checking 502 page: {e}")
        return False


def check_nginx_502_error(driver):
    max_retries = 500
    retries = 0
    while retries < max_retries:
        try:
            if not is_502_error_page(driver):
                return True
            else:
                logging.error("Nginx 502 Bad Gateway error detected, refreshing page.")
                time.sleep(5)
                driver.refresh()
                retries += 1
        except TimeoutException as e:
            logging.error(f"TimeoutException encountered: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return False
    logging.error("Max retries reached, exiting...")
    return False
