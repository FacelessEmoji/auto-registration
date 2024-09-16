import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

from project.annotations import with_modal_check
from project.errors import check_nginx_502_error
from project.exceptions import NoAvailableGroupsError
from project.functions import change_account_status


@with_modal_check
def navigate_to_login_page(driver, account, login_url):
    logging.info(f"Account {account['iin']}: Logging in")
    driver.get(login_url)
    if not check_nginx_502_error(driver):
        logging.error("Failed to resolve 502 error after retries, exiting...")
        return
    time.sleep(3)


@with_modal_check
def click_iin_bin_link(driver, account):
    wait = WebDriverWait(driver, 10)
    link_element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "ИИН/БИН")))
    link_element.click()


@with_modal_check
def enter_iin(driver, account):
    logging.info(f"Account {account['iin']}: Entering IIN")
    iin_field = driver.find_element(By.NAME, "iin")
    iin_field.send_keys(account["iin"])


@with_modal_check
def enter_password(driver, account):
    logging.info(f"Account {account['iin']}: Entering password")
    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(account["password"])


@with_modal_check
def click_login_button(driver, account):
    wait = WebDriverWait(driver, 10)
    login_button = wait.until(EC.element_to_be_clickable((By.ID, "kt_sign_in_submit")))
    login_button.click()


@with_modal_check
def click_continue_button(driver, account):
    wait = WebDriverWait(driver, 10)
    continue_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@class, 'swal2-confirm') and contains(text(), 'Продолжить')]")))
    continue_button.click()


@with_modal_check
def change_language_to_russian(driver, account):
    if not check_nginx_502_error(driver):
        logging.error("Failed to resolve 502 error after retries, exiting...")
        return
    wait = WebDriverWait(driver, 10)
    try:
        user_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'cursor-pointer symbol symbol-circle symbol-30px symbol-md-40px')]")))
        user_button.click()

        language_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='dropdownMenuButton' and contains(text(), 'Тіл')]")))
        language_button.click()

        russian_language_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Русский')]")))
        russian_language_option.click()

        logging.info(f"Account {account['iin']}: Language changed to Russian")
    except Exception as e:
        logging.error(f"Account {account['iin']}: Error changing language to Russian - {e}")


def click_each_tab_and_check_group(driver):
    indices_with_mismatch = []

    try:
        # Найти ul элемент с классом nav nav-tabs nav-line-tabs nav-line-tabs-2x mb-12 fs-5
        ul_xpath = "//ul[@class='nav nav-tabs nav-line-tabs nav-line-tabs-2x mb-12 fs-5']"
        ul_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ul_xpath)))

        # Прокрутка до ul элемента
        driver.execute_script("arguments[0].scrollIntoView(true);", ul_element)
        time.sleep(0.5)  # Добавить небольшую паузу, чтобы прокрутка завершилась

        # Найти все li элементы внутри ul
        li_elements = ul_element.find_elements(By.XPATH, ".//li[@class='nav-item']")

        if not li_elements:
            return indices_with_mismatch

        for index, li in enumerate(li_elements):
            try:
                if index != 0:  # Пропустить первый элемент
                    driver.execute_script("arguments[0].scrollIntoView(true);", li)
                    time.sleep(0.3)  # Добавить небольшую паузу, чтобы прокрутка завершилась

                    a_element = li.find_element(By.XPATH, ".//a[@class='nav-link m-0 me-4']")
                    driver.execute_script("arguments[0].scrollIntoView(true);", a_element)
                    time.sleep(0.3)  # Добавить небольшую паузу, чтобы прокрутка завершилась

                    driver.execute_script("arguments[0].click();", a_element)
                    time.sleep(1)  # Добавить паузу между кликами, если нужно

                progress_info_xpath = "//div[@class='section__schedule-progress']"
                progress_info_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, progress_info_xpath))
                )

                time.sleep(0.5)

                students_text = progress_info_element.find_element(By.XPATH, ".//div/span/span").text
                students_current, students_total = map(int, students_text.split('/'))

                queue_text = progress_info_element.find_element(By.XPATH, ".//div[@class='mt-5']/h3/span").text
                queue_count = int(queue_text)

                # Проверка на возможное деление на ноль
                if students_total == 0:
                    logging.error(f"Total students is 0 in group at index {index + 1}, skipping group.")
                    continue

                total_participants = students_current + queue_count
                percentage_filled = total_participants / students_total

                # Проверка, если процент не равен 1
                if percentage_filled != 1:
                    indices_with_mismatch.append(index + 1)  # Добавить индекс (начинается с 1)
                    logging.info(
                        f"Added group {index + 1}: filled {total_participants}/{students_total} )")

            except Exception as e:
                logging.error(f"Error occurred while processing group at index {index + 1}: {e}")

    except Exception as e:
        logging.error(f"Error occurred while clicking each tab: {e}")

    return indices_with_mismatch


@with_modal_check
def click_register_button(driver, account, accounts, csv_path):
    attempts = 0
    if not check_nginx_502_error(driver):
        logging.error("Failed to resolve 502 error after retries, exiting...")
        return
    while attempts < 500:
        try:
            wait = WebDriverWait(driver, 50)
            button_xpath = "//button[contains(@class, 'btn') and contains(@class, 'btn-sm') and contains(@class, 'btn-primary') and contains(@class, 'text-nowrap') and contains(@class, 'ms-3')]"

            button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
            button_text = button.find_element(By.XPATH, "./span").text.strip()

            if button_text == "Записаться":
                button.click()
            else:
                logging.warning(f"Button has unexpected text: {button_text}")

            error_popup = ""
            try:
                error_popup = driver.find_element(By.CSS_SELECTOR,
                                                  'div.swal2-popup.swal2-modal.swal2-icon-warning.swal2-show')
            except:
                None
            if error_popup:
                raise Exception()
            else:
                logging.info(f"Modal content on the site")
                fill_modal_form(driver, account, accounts, csv_path)
                return


        except Exception as e:
            attempts += 1
            logging.warning(f"Attempt {attempts} failed: {e}")
            logging.info("Refreshing the page and retrying...")
            driver.refresh()
            if not check_nginx_502_error(driver):
                logging.error("Failed to resolve 502 error after retries, exiting...")
                return
            time.sleep(3)

    raise Exception("Reached maximum number of attempts. Exiting...")


def fill_modal_form(driver, account, accounts, csv_path):
    list_of_groups = click_each_tab_and_check_group(driver)

    if not list_of_groups:
        change_account_status(accounts, account, "No Available Group", csv_path)
        logging.error(f"Failed to enroll account {account['iin']} in group: No available spots.")
        return

    # group_number = random.choice(list_of_groups)
    group_number = 2

    if check_nginx_502_error(driver):
        try:
            wait = WebDriverWait(driver, 10)
            first_element_xpath = "//div[@class='vs__selected-options']/input[@placeholder='Выберите ребенка']"
            first_element = wait.until(EC.element_to_be_clickable((By.XPATH, first_element_xpath)))
            first_element.click()

            try:
                wait = WebDriverWait(driver, 0.3)
                element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'vs__no-options')))
                if element:
                    change_account_status(accounts, account, "Finished", csv_path)
                    logging.info(f"No options in modal form for account {account['iin']}, acc registered")
                    return
            except:
                None

            first_option_xpath = f"//ul[@id='vs2__listbox' and contains(@class, 'vs__dropdown-menu')]/li[@role='option'][{account.get('child_in_order')}]"

            wait = WebDriverWait(driver, 10)
            first_option = wait.until(EC.element_to_be_clickable((By.XPATH, first_option_xpath)))
            first_option.click()

            second_element_xpath = "//div[@class='vs__selected-options']/input[@placeholder='Выберите группу' and not(@disabled)]"
            second_element = wait.until(EC.element_to_be_clickable((By.XPATH, second_element_xpath)))
            second_element.click()

            try:
                wait = WebDriverWait(driver, 0.3)
                element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'vs__no-options')))
                if element:
                    change_account_status(accounts, account, "Finished", csv_path)
                    logging.info(f"No options in modal form for account {account['iin']}, acc registered")
                    return
            except:
                None

            wait = WebDriverWait(driver, 10)
            second_first_option_xpath = f"//ul[@id='vs3__listbox' and contains(@class, 'vs__dropdown-menu')]/li[@role='option'][{group_number}]"
            second_first_option = wait.until(EC.element_to_be_clickable((By.XPATH, second_first_option_xpath)))
            second_first_option.click()

            checkbox_xpath = "//input[@type='checkbox' and @id='checkbox']"
            checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, checkbox_xpath)))
            checkbox.click()

            submit_button_xpath = "//button[contains(text(), 'Записаться')]"
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, submit_button_xpath)))

            submit_button.click()

            try:
                element = WebDriverWait(driver, 1).until(
                    EC.visibility_of_element_located((By.ID, "swal2-content"))
                )
                if "Ошибка!" in element.text:
                    logging.error(f"Failed to enroll account {account['iin']} in group: No available spots.")
                    change_account_status(accounts, account, "No Spots", csv_path)
                    raise NoAvailableGroupsError("No available spots in the group.")
            except NoAvailableGroupsError as e:
                raise Exception(e)
            except Exception:
                None

            change_account_status(accounts, account, "Finished", csv_path)
            logging.info(f"Successfully enrolled account {account['iin']} in group.")

        except Exception as e:
            logging.error(f"Error filling form in account {account['iin']}: {e}")
