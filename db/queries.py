from sqlalchemy.orm import Session
from models import Account


def change_account_status(session: Session, account_id: int, new_status: str):
    """Изменяет статус аккаунта по id."""
    # Находим аккаунт по id
    account = session.query(Account).filter(Account.id == account_id).first()

    if account:
        account.status = new_status  # Обновляем статус
        session.commit()  # Сохраняем изменения
        print(f"Статус аккаунта с ID {account_id} изменен на '{new_status}'.")
    else:
        print(f"Аккаунт с ID {account_id} не найден.")


# Функция для получения аккаунта по ID
def get_account_by_id(session: Session, account_id: int):
    return session.query(Account).filter(Account.id == account_id).first()
