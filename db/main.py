import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Account

engine = create_engine('sqlite:///accounts.db')


# Создаем таблицы в базе данных
def create_database():
    if not os.path.exists('accounts.db'):
        Base.metadata.create_all(engine)  # Создание таблицы
        print("База данных и таблицы созданы.")
    else:
        print("База данных уже существует.")


# Функция для загрузки аккаунтов из текстового файла
def load_accounts_from_txt_to_db(file_path):
    session = sessionmaker(bind=engine)()

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                iin, password, phone_number, target_url, child_name, status = line.strip().split(';')

                # Создаем новый объект Account
                new_account = Account(
                    iin=iin,
                    password=password,
                    phone_number=phone_number,
                    target_url=target_url,
                    child_name=child_name,
                    status=status
                )

                # Добавляем объект в сессию
                session.add(new_account)

            except ValueError as e:
                print(f"Ошибка при обработке строки: {line}. Ошибка: {e}")

    session.commit()  # Сохраняем изменения
    session.close()  # Закрываем сессию

# # Функция для тестирования изменения статуса аккаунтов
# def test_change_account_status():
#     Session = sessionmaker(bind=engine)
#     session = Session()
#
#     # Получаем аккаунты с ID 1 и 2
#     account_1 = get_account_by_id(session, 1)
#     account_2 = get_account_by_id(session, 2)
#
#     if account_1:
#         print(f"Исходный статус аккаунта 1: {account_1.status}")
#         change_account_status(session, account_1.id, 'Not')
#         print(f"Новый статус аккаунта 1: {account_1.status}")
#
#     if account_2:
#         print(f"Исходный статус аккаунта 2: {account_2.status}")
#         change_account_status(session, account_2.id, 'Started')
#         print(f"Новый статус аккаунта 2: {account_2.status}")
#
#     session.close()  # Закрываем сессию


# Запускаем тест для изменения статуса аккаунтов
if __name__ == "__main__":
    create_database()
    load_accounts_from_txt_to_db("accounts.txt")

