import time
import logging

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db.queries import change_account_status
from project.annotations import with_modal_check
from project.errors import check_nginx_502_error
from project.exceptions import AuthenticationError, PhoneNumbersError, IncorrectGroupLink, LanguageChangeError


@with_modal_check
def navigate_to_login_page(driver, login_url):
    driver.get(login_url)
    if not check_nginx_502_error(driver):
        logging.error("Failed to resolve 502 error after retries, exiting...")
        return
    # Зачем?
    time.sleep(3)


@with_modal_check
def click_iin_bin_link(driver):
    wait = WebDriverWait(driver, 10)
    link_element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "ИИН/БИН")))
    link_element.click()


@with_modal_check
def enter_iin(driver, account):
    iin_field = driver.find_element(By.NAME, "iin")
    iin_field.send_keys(account["iin"])


@with_modal_check
def enter_password(driver, account):
    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(account["password"])


@with_modal_check
def click_login_button(driver):
    wait = WebDriverWait(driver, 10)
    login_button = wait.until(EC.element_to_be_clickable((By.ID, "kt_sign_in_submit")))
    login_button.click()
    time.sleep(4)


@with_modal_check
def enter_phone_number(driver, account):
    wait_var = WebDriverWait(driver, 4)
    try:
        wait_var.until(EC.presence_of_element_located((By.XPATH, "//input[@class='otp-input one']"))).send_keys(
            account['phone_number'])
    except Exception as e:
        raise AuthenticationError(f"Account {account['iin']}: Error entering phone number: {e}!")


@with_modal_check
def click_popup_button(driver, account):
    wait_var = WebDriverWait(driver, 2)
    try:
        success_popup = wait_var.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.swal2-popup.swal2-icon-success')))
        if success_popup.is_displayed():
            continue_button = success_popup.find_element(By.CSS_SELECTOR, '.swal2-confirm')
            wait_var.until(EC.element_to_be_clickable(continue_button))
            continue_button.click()
    except:
        error_icon = driver.find_element(By.CLASS_NAME, "swal2-icon-error")
        if error_icon.is_displayed():
            raise PhoneNumbersError(
                f"Account {account['iin']}: Invalid last 4 digits of phone number!")
        else:
            raise Exception("Unexpected login_and_continue Error")


@with_modal_check
def click_continue_button(driver):
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
        raise LanguageChangeError(f"Account {account['iin']}: Error changing language to Russian - {e}")


def check_page_unavailable(driver, account):
    time.sleep(3)

    current_url = driver.current_url
    if "https://damubala.kz/parent/children" in current_url:
        raise IncorrectGroupLink(f"Account {account['iin']}: Incorrect group link for child. Supplier in link.")

    wait_var = WebDriverWait(driver, 3)
    try:
        wait_var.until(EC.presence_of_element_located(
            (By.XPATH, "//h1[contains(text(), 'Страница недоступна в данный момент')]")
        ))
        raise IncorrectGroupLink(f"Account {account['iin']}: Incorrect group link for child. Section is unavailable.")
    except TimeoutException:
        pass



def click_each_tab_and_check_group(driver):
    indices_with_mismatch = []

    try:
        # Найти ul элемент с классом nav nav-tabs nav-line-tabs nav-line-tabs-2x mb-12 fs-5
        ul_xpath = "//ul[@class='nav nav-tabs nav-line-tabs nav-line-tabs-2x mb-12 fs-5']"
        ul_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ul_xpath)))

        # Прокрутка до ul элемента
        driver.execute_script("arguments[0].scrollIntoView(true);", ul_element)
        time.sleep(0.1)  # Добавить небольшую паузу, чтобы прокрутка завершилась

        # Найти все li элементы внутри ul
        li_elements = ul_element.find_elements(By.XPATH, ".//li[@class='nav-item']")

        if not li_elements:
            return indices_with_mismatch

        for index, li in enumerate(li_elements):
            try:
                if index != 0:  # Пропустить первый элемент
                    driver.execute_script("arguments[0].scrollIntoView(true);", li)
                    time.sleep(0.1)  # Добавить небольшую паузу, чтобы прокрутка завершилась

                    a_element = li.find_element(By.XPATH, ".//a[@class='nav-link m-0 me-4']")
                    driver.execute_script("arguments[0].scrollIntoView(true);", a_element)
                    time.sleep(0.1)  # Добавить небольшую паузу, чтобы прокрутка завершилась

                    driver.execute_script("arguments[0].click();", a_element)
                    time.sleep(0.4)  # Добавить паузу между кликами, если нужно

                progress_info_xpath = "//div[@class='section__schedule-progress']"
                progress_info_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, progress_info_xpath))
                )

                students_text = progress_info_element.find_element(By.XPATH, ".//div/span/span").text
                students_current, students_total = map(int, students_text.split('/'))

                queue_text = progress_info_element.find_element(By.XPATH, ".//div[@class='mt-5']/h3/span").text
                queue_count = int(queue_text)

                if students_total == 0:
                    continue

                total_participants = students_current + queue_count
                percentage_filled = total_participants / students_total

                if percentage_filled != 1:
                    return index + 1

            except Exception as e:
                logging.error(f"Error occurred while processing group at index {index + 1}: {e}")

    except Exception as e:
        logging.error(f"Error occurred while clicking each tab: {e}")

    return 1


@with_modal_check
def click_register_button(driver, account, session):
    attempts = 0
    if not check_nginx_502_error(driver):
        logging.error("Failed to resolve 502 error after retries, exiting...")
        return
    # while attempts < 500: TODO: УБРАТЬ НАХУЙ
    while attempts < 3:
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
                logging.info(f"Account {account['iin']}: Form is open.")
                fill_modal_form(driver, account, session)
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


def fill_modal_form(driver, account, session):
    selected_group = click_each_tab_and_check_group(driver)

    if not selected_group:
        change_account_status(session, account['id'], "No Available Group")
        logging.error(f"Account {account['iin']}: No available spots in section.")
        return

    if check_nginx_502_error(driver):
        try:
            wait = WebDriverWait(driver, 10)
            first_element_xpath = "//div[@class='vs__selected-options']/input[@placeholder='Выберите ребенка']"
            first_element = wait.until(EC.element_to_be_clickable((By.XPATH, first_element_xpath)))
            time.sleep(1.5)
            first_element.click()

            try:
                wait = WebDriverWait(driver, 0.3)
                element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'vs__no-options')))
                if element:
                    change_account_status(session, account['id'], "Finished")
                    logging.info(
                        f"Account {account['iin']}: No options in modal form, already registered or no children.")
                    return
            except:
                None

            options_xpath = "//ul[@id='vs2__listbox' and contains(@class, 'vs__dropdown-menu')]/li[@role='option']"
            options = wait.until(EC.presence_of_all_elements_located((By.XPATH, options_xpath)))

            child_name = None
            desired_value = account.get('child_name')

            for i, option in enumerate(options, start=1):
                if desired_value in option.text:
                    child_name = i
                    break

            if child_name is None:
                change_account_status(session, account['id'], "Incorrect Child Name")
                logging.error(f"Account {account['iin']}: Failed to enroll in group. No name matches for {child_name}.")
                return

            print(child_name)

            first_option_xpath = f"//ul[@id='vs2__listbox' and contains(@class, 'vs__dropdown-menu')]/li[@role='option'][{child_name}]"
            first_option = wait.until(EC.element_to_be_clickable((By.XPATH, first_option_xpath)))
            first_option.click()

            second_element_xpath = "//div[@class='vs__selected-options']/input[@placeholder='Выберите группу' and not(@disabled)]"
            second_element = wait.until(EC.element_to_be_clickable((By.XPATH, second_element_xpath)))
            second_element.click()

            try:
                wait = WebDriverWait(driver, 1)
                element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'vs__no-options')))
                if element:
                    change_account_status(session, account['id'], "Finished")
                    logging.info(
                        f"Account {account['iin']}: No options in modal form, already registered or no children.")
                    return
            except:
                pass

            second_first_option_xpath = f"//ul[@id='vs3__listbox' and contains(@class, 'vs__dropdown-menu')]/li[@role='option'][{selected_group}]"
            second_first_option = wait.until(EC.element_to_be_clickable((By.XPATH, second_first_option_xpath)))
            second_first_option.click()

            # checkbox_xpath = "//input[@type='checkbox' and @id='checkbox']"
            # checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, checkbox_xpath)))
            # checkbox.click()

            submit_button_xpath = "//button[contains(text(), 'Записаться')]"
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, submit_button_xpath)))
            submit_button.click()

            try:
                success_popup = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH,
                                                      "//div[contains(@class, 'swal2-popup') and contains(@class, 'swal2-icon-success') and contains(@class, 'swal2-show')]"))
                )
                success_message = success_popup.find_element(By.XPATH, "//div[@id='swal2-content']/h2")

                if "Успешно!" in success_message.text:
                    change_account_status(session, account['id'], "Finished")
                    logging.info(f"Account {account['iin']}: Successfully enrolled in group.")

            except Exception as e:
                change_account_status(session, account['id'], "No Spots In Current Group")
                logging.info(f"Account {account['iin']}: No spots in current group.")

        except Exception as e:
            logging.error(f"Account {account['iin']}: Error while filling form: {e}")
