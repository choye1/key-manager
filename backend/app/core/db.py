from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app import models 
from app.core.config import settings

print("DB URL:", settings.SQLALCHEMY_DATABASE_URI)
# Создаём engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=True,  # можно выключить потом
)


# Dependency для FastAPI
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


# Инициализация БД (создание таблиц)
def init_db() -> None:
    SQLModel.metadata.create_all(engine)