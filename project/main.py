import os
import random
import threading
import time
import logging

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from concurrent.futures import ThreadPoolExecutor, as_completed

from db.queries import get_account_by_id, load_accounts_from_db, change_account_status
from project.errors import check_nginx_502_error
from project.exceptions import PhoneNumbersError, AuthenticationError, IncorrectGroupLink, LanguageChangeError
from project.parsing import navigate_to_login_page, click_iin_bin_link, enter_iin, enter_password, \
    click_login_button, \
    change_language_to_russian, click_register_button, enter_phone_number, click_popup_button, check_page_unavailable

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("./log.txt", mode='a', encoding='utf-8'),
    logging.StreamHandler()
])

# Отключаем все логи уровня INFO и ниже
logging.getLogger('seleniumwire').setLevel(logging.ERROR)

engine = create_engine('sqlite:///db/accounts.db')
Session = scoped_session(sessionmaker(bind=engine))



def login_and_continue(driver, account):
    login_url = "https://damubala.kz/sign-in"
    navigate_to_login_page(driver, login_url)
    click_iin_bin_link(driver)
    enter_iin(driver, account)
    enter_password(driver, account)
    click_login_button(driver)
    enter_phone_number(driver, account)
    click_popup_button(driver, account)
    logging.info(f"Account {account['iin']}: Logged into main menu")


def process_account(account, proxies, session):
    # -----------------------------------------Config-------------------------------------------------------------------
    # Проверяем, какая операционная система используется
    if os.name == 'nt':  # Если это Windows
        # Глебы
        # chrome_driver_path = r"C:\Users\Raven\Desktop\auto-registration\ch\chromedriver-win64\chromedriver.exe"
        # chrome_binary_path = r"C:\Users\Raven\Desktop\auto-registration\ch\chrome-win64\chrome.exe"
        # Иваны
        chrome_driver_path = r"C:\Users\Emoji\Desktop\KzChrome\chromedriver-win64\chromedriver.exe"
        chrome_binary_path = r"C:\Users\Emoji\Desktop\KzChrome\chrome-win64\chrome.exe"
    else:  # Если это Linux
        chrome_driver_path = "/usr/bin/chromedriver"
        chrome_binary_path = "/opt/google-chrome/chrome"

    chrome_options = Options()
    chrome_options.binary_location = chrome_binary_path
    service = ChromeService(executable_path=chrome_driver_path)

    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')

    # __________________________________________________________________________________________________________________

    # --------------------------------------------Proxy Config----------------------------------------------------------
    proxy = random.choice(proxies)
    ip, port, user, password = proxy.split(':')

    proxy_options = {
        'proxy': {
            'http': f'http://{user}:{password}@{ip}:{port}',
            'https': f'https://{user}:{password}@{ip}:{port}',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }
    # __________________________________________________________________________________________________________________

    # with webdriver.Chrome(seleniumwire_options=proxy_options, service=service, options=chrome_options) as driver:
    with webdriver.Chrome(service=service, options=chrome_options) as driver:
        try:

            change_account_status(session, account['id'], "Running")
            login_and_continue(driver, account)

            time.sleep(2)
            try:
                popup_button = driver.find_element("css selector", "button.swal2-confirm.btn-light-danger")
                if popup_button.is_displayed():
                    popup_button.click()
                    logging.info("Попап закрыт.")
            except NoSuchElementException:
                pass
            change_language_to_russian(driver, account)
            driver.get(account["target_url"])
            check_page_unavailable(driver, account)
            if not check_nginx_502_error(driver):
                logging.error("Failed to resolve 502 error after retries, exiting...")
                return
            logging.info(f"Account {account['iin']}: Navigated to {account['target_url']}")
            click_register_button(driver, account, session)
        except AuthenticationError as e:
            change_account_status(session, account['id'], "Authentication Error")
            logging.error(f"{e}")
        except PhoneNumbersError as e:
            change_account_status(session, account['id'], "Phone Numbers Error")
            logging.error(f"{e}")
        except IncorrectGroupLink as e:
            change_account_status(session, account['id'], "Incorrect Group Link")
            logging.error(f"{e}")
        except LanguageChangeError as e:
            change_account_status(session, account['id'], "Language Change Error")
            logging.error(f"{e}")
        except Exception as e:
            error_name = type(e).__name__
            logging.error(f"Error {error_name} processing account {account['iin']}: {e}")
            change_account_status(session, account['id'], "Error")



def main(proxies):
    session = Session()
    try:
        accounts = load_accounts_from_db(session)
    except Exception as e:
        print(e)
        return
    finally:
        session.close()

    ignored_statuses = ["Finished", "No Available Group", "Phone Numbers Error",
                        "Incorrect Child Name", "Incorrect Group Link"]
    iin_locks = {}

    def process_account_with_lock(account, *args):
        iin = account['iin']

        if iin not in iin_locks:
            iin_locks[iin] = threading.Lock()

        with iin_locks[iin]:
            process_account(account, *args)

    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = []

        for account in accounts:
            iin = account['iin']

            if account['status'] not in ignored_statuses:
                future = executor.submit(process_account_with_lock, account, proxies, session)
                futures.append(future)

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Exception in thread: {e}")
