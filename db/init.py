import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, Account

engine = create_engine('sqlite:///accounts.db')


def create_database(db_path):
    engine = create_engine(f"sqlite:///{db_path}")  # Создаем соединение с базой данных

    if not os.path.exists(db_path):
        Base.metadata.create_all(engine)  # Создание таблицы
        print("База данных и таблицы созданы.")
    else:
        print("База данных уже существует.")

    return engine


def load_accounts_from_txt_to_db(file_path, db_path):
    engine = create_engine(f"sqlite:///{db_path}")
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
    print("Данные успешно загружены в базу данных.")
