from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from .models import Account


def change_account_status(session, account_id: int, new_status: str):

    engine = create_engine('sqlite:///db/accounts.db')
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    """Изменяет статус аккаунта по id."""
    # Находим аккаунт по id
    account = session.query(Account).filter(Account.id == account_id).first()

    if account:
        account.status = new_status  # Обновляем статус
        session.commit()  # Сохраняем изменения
        print(f"Статус аккаунта с ID {account_id} изменен на '{new_status}'.")
    else:
        print(f"Аккаунт с ID {account_id} не найден.")
    session.close()


# Функция для получения аккаунта по ID
def get_account_by_id(session, account_id: int):

    engine = create_engine('sqlite:///db/accounts.db')
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    account = session.query(Account).filter(Account.id == account_id).first()
    session.close()
    return account


def load_accounts_from_db(session):

    engine = create_engine('sqlite:///db/accounts.db')
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    accounts = session.query(Account).all()

    # Преобразуем данные в список словарей
    account_list = []
    for acc in accounts:
        account = {
            "id": acc.id,  # Добавляем id
            "iin": acc.iin,
            "password": acc.password,
            "phone_number": acc.phone_number,
            "target_url": acc.target_url,
            "child_name": acc.child_name,
            "status": acc.status
        }
        account_list.append(account)
    session.close()
    return account_list  # Возвращаем список аккаунтов
