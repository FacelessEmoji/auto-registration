def parse_accounts_from_txt(file_path):
    accounts = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                iin, password, phone_number, target_url, child_name, status = line.split(';')
                account = {
                    "iin": iin,
                    "password": password,
                    "phone_number": phone_number,
                    "target_url": target_url,
                    "child_name": child_name,
                    "status": status
                }
                accounts.append(account)
    return accounts


def load_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file]
    return proxies


# Функция для сохранения данных в TXT
# def save_accounts_to_txt(file_path, accounts):
#     try:
#         with open(file_path, mode='w', encoding='utf-8') as file:
#             for account in accounts:
#                 file.write(
#                     f"{account['iin']};{account['password']};{account['phone_number']};{account['target_url']};{account['child_name']};{account['status']}\n")
#     except Exception as e:
#         print(f"Error saving accounts to TXT: {e}")


# Функция для изменения статуса аккаунта
# def change_account_status(accounts, account, new_status, txt_file_path):
#     account['status'] = new_status
#     update_account_in_list(accounts, account)
#     # deprecated
#     save_accounts_to_txt(txt_file_path, accounts)
# Функция для обновления аккаунта в списке
# def update_account_in_list(accounts, updated_account):
#     for i, acc in enumerate(accounts):
#         if acc['iin'] == updated_account['iin'] and acc['child_name'] == updated_account['child_name']:
#             accounts[i] = updated_account
#             break
