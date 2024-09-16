import os
import platform
import random

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire import webdriver
import time
import logging
from selenium.webdriver.chrome.service import Service as ChromeService
from concurrent.futures import ThreadPoolExecutor, as_completed
from project.errors import check_nginx_502_error
from project.parsing import navigate_to_login_page, click_iin_bin_link, enter_iin, enter_password, \
    click_login_button, \
    click_continue_button, change_language_to_russian, click_register_button
from project.functions import change_account_status

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("../log.txt", mode='a', encoding='utf-8'),
    logging.StreamHandler()
])

# Отключаем все логи уровня INFO и ниже
logging.getLogger('seleniumwire').setLevel(logging.ERROR)


def login_and_continue(driver, account):
    login_url = "https://damubala.kz/sign-in"
    navigate_to_login_page(driver, account, login_url)
    click_iin_bin_link(driver, account)
    enter_iin(driver, account)
    enter_password(driver, account)
    click_login_button(driver, account)

    time.sleep(1.5)
    wait = WebDriverWait(driver, 2)
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@class='otp-input one']"))).send_keys(
        account['phone_number'][0])
    driver.find_element(By.XPATH, "//input[@class='otp-input two']").send_keys(account['phone_number'][1])
    driver.find_element(By.XPATH, "//input[@class='otp-input three']").send_keys(account['phone_number'][2])
    driver.find_element(By.XPATH, "//input[@class='otp-input four']").send_keys(account['phone_number'][3])

    try:
        success_popup = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.swal2-popup.swal2-icon-success')))

        if success_popup.is_displayed():
            continue_button = success_popup.find_element(By.CSS_SELECTOR, '.swal2-confirm')
            wait.until(EC.element_to_be_clickable(continue_button))
            continue_button.click()

    except Exception as e:
        error_popup = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "swal2-popup")))
        error_icon = driver.find_element(By.CLASS_NAME, "swal2-icon-error")
        if error_icon.is_displayed():
            raise Exception("Ошибка: Неверные последние 4 цифры номера телефона!")
        else:
            raise Exception("login_and_continue error")

    logging.info(f"Account {account['iin']}: Logged into main menu")


def process_account(account, accounts, proxies, csv_path):
    proxy = random.choice(proxies)
    ip, port, user, password = proxy.split(':')

    proxy_options = {
        'proxy': {
            'http': f'http://{user}:{password}@{ip}:{port}',
            'https': f'https://{user}:{password}@{ip}:{port}',
            'no_proxy': 'localhost,127.0.0.1'  # Список адресов, для которых прокси не используется
        }
    }

    chrome_install = ChromeDriverManager().install()
    folder = os.path.dirname(chrome_install)

    # Определяем имя файла ChromeDriver в зависимости от ОС
    if platform.system() == "Windows":
        chromedriver_path = os.path.join(folder, "chromedriver.exe")
    else:
        chromedriver_path = os.path.join(folder, "chromedriver")

    # Указываем путь к ChromeDriver
    service = ChromeService(chromedriver_path)

    # Настройки для безголового режима Chrome
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')

    # Запуск браузера с заданными опциями и сервисом
    with webdriver.Chrome(seleniumwire_options=proxy_options, service=service, options=chrome_options) as driver:
        try:
            change_account_status(accounts, account, "Running", csv_path)

            login_and_continue(driver, account)
            time.sleep(3)
            try:
                popup_button = driver.find_element("css selector", "button.swal2-confirm.btn-light-danger")
                if popup_button.is_displayed():
                    popup_button.click()
                    logging.info("Попап закрыт.")
                else:
                    logging.info("Попап не отображается.")
            except NoSuchElementException:
                logging.info("Попап не найден.")

            change_language_to_russian(driver, account)

            driver.get(account["target_url"])
            if not check_nginx_502_error(driver):
                logging.error("Failed to resolve 502 error after retries, exiting...")
                return
            logging.info(f"Account {account['iin']}: Navigated to {account['target_url']}")
            time.sleep(5)
            click_register_button(driver, account, accounts, csv_path)

        except Exception as e:
            change_account_status(accounts, account, "Error", csv_path)
            logging.error(f"Error processing account {account['iin']}: {e}")


def main(proxies, accounts, csv_path):
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for account in accounts:
            if account['status'] != "Finished":
                future = executor.submit(process_account, account, accounts, proxies, csv_path)
                futures.append(future)

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Exception in thread: {e}")
