from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Определяем базу для моделей
Base = declarative_base()


# Определяем модель (сущность) для аккаунтов
class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Уникальный идентификатор
    iin = Column(String, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    target_url = Column(String, nullable=False)
    child_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default='Not Started')
