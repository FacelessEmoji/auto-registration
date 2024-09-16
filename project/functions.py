# Функция для парсинга данных из TXT
def parse_accounts_from_txt(file_path):
    accounts = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                # Разделяем строку по символу `;`
                iin, password, target_url, child_in_order, status = line.split(';')
                account = {
                    "iin": iin,
                    "password": password,
                    "target_url": target_url,
                    "child_in_order": child_in_order,
                    "status": status
                }
                accounts.append(account)
    return accounts


# Функция для загрузки прокси из TXT файла
def load_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file]
    return proxies


# Функция для сохранения данных в TXT
def save_accounts_to_txt(file_path, accounts):
    try:
        with open(file_path, mode='w', encoding='utf-8') as file:
            for account in accounts:
                file.write(
                    f"{account['iin']};{account['password']};{account['target_url']};{account['child_in_order']};{account['status']}\n")
        print(f"Accounts saved to {file_path}")
    except Exception as e:
        print(f"Error saving accounts to TXT: {e}")


# Функция для изменения статуса аккаунта
def change_account_status(accounts, account, new_status, txt_file_path):
    account['status'] = new_status
    update_account_in_list(accounts, account)
    save_accounts_to_txt(txt_file_path, accounts)


# Функция для обновления аккаунта в списке
def update_account_in_list(accounts, updated_account):
    for i, acc in enumerate(accounts):
        if acc['iin'] == updated_account['iin']:
            accounts[i] = updated_account
            break


def format_account_text(account):
    return f"IIN: {account['iin']}, Password: {account['password']}, URL: {account['target_url']}, Status: {account['status']}"
