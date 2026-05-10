from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models import (
    Key,
    KeyCreate,
    KeyStatus,
    Object,
    ObjectCreate,
    Operation,
    OperationType,
    User,
    UserCreate,
    
)

import uuid

def get_users(session: Session) -> list[User]:
    statement = select(User).order_by(User.created_at.desc())
    return list(session.exec(statement).all())

def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create_user(session: Session, user_create: UserCreate) -> User:
    db_user = User(
        email=user_create.email,
        full_name=user_create.full_name,
        role=user_create.role,
        is_active=user_create.is_active,
        phone=user_create.phone,
        organization=user_create.organization,
        hashed_password=get_password_hash(user_create.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def create_object(session: Session, object_in: ObjectCreate) -> Object:
    db_object = Object(
        code=object_in.code,
        type=object_in.type,
        is_active=object_in.is_active,
    )
    session.add(db_object)
    session.commit()
    session.refresh(db_object)
    return db_object


def get_object_by_code(session: Session, code: str) -> Object | None:
    statement = select(Object).where(Object.code == code.upper())
    return session.exec(statement).first()


def get_object_by_id(session: Session, object_id) -> Object | None:
    return session.get(Object, object_id)


def get_objects(session: Session) -> list[Object]:
    statement = select(Object).order_by(Object.created_at.desc())
    return list(session.exec(statement).all())


def create_key(session: Session, key_in: KeyCreate) -> Key:
    db_key = Key(
        object_id=key_in.object_id,
        status=key_in.status,
        holder_user_id=None,
    )
    session.add(db_key)
    session.commit()
    session.refresh(db_key)
    return db_key

def get_key_by_id(session: Session, key_id) -> Key | None:
    return session.get(Key, key_id)


def get_keys(session: Session) -> list[Key]:
    statement = select(Key).order_by(Key.created_at.desc())
    return list(session.exec(statement).all())

def get_available_key_for_object(session: Session, object_id) -> Key | None:
    statement = (
        select(Key)
        .where(Key.object_id == object_id)
        .where(Key.status == KeyStatus.available)
        .order_by(Key.created_at.asc())
    )
    return session.exec(statement).first()


def create_operation(
    session: Session,
    *,
    key_id,
    object_id,
    user_id,
    operation_type: OperationType,
    fio: str | None,
    organization: str | None,
    phone: str | None,
    photo_path: str | None,
) -> Operation:
    operation = Operation(
        key_id=key_id,
        object_id=object_id,
        user_id=user_id,
        type=operation_type,
        fio=fio,
        organization=organization,
        phone=phone,
        photo_path=photo_path,
    )
    session.add(operation)
    session.commit()
    session.refresh(operation)
    return operation

def get_issued_keys_for_object(session: Session, object_id) -> list[Key]:
    statement = (
        select(Key)
        .where(Key.object_id == object_id)
        .where(Key.status == KeyStatus.issued)
        .order_by(Key.created_at.asc())
    )
    return list(session.exec(statement).all())


def get_first_issued_key_for_object(session: Session, object_id) -> Key | None:
    statement = (
        select(Key)
        .where(Key.object_id == object_id)
        .where(Key.status == KeyStatus.issued)
        .order_by(Key.created_at.asc())
    )
    return session.exec(statement).first()


def get_operations_by_object_id(session: Session, object_id) -> list[Operation]:
    statement = (
        select(Operation)
        .where(Operation.object_id == object_id)
        .order_by(Operation.operation_time.desc(), Operation.created_at.desc())
    )
    return list(session.exec(statement).all())

def get_keys_filtered(
    session: Session,
    *,
    object_id=None,
    status: KeyStatus | None = None,
) -> list[Key]:
    statement = select(Key)

    if object_id is not None:
        statement = statement.where(Key.object_id == object_id)

    if status is not None:
        statement = statement.where(Key.status == status)

    statement = statement.order_by(Key.created_at.desc())
    return list(session.exec(statement).all())

def get_issued_key_for_user_and_object(session: Session, *, user_id, object_id) -> Key | None:
    statement = (
        select(Key)
        .where(Key.object_id == object_id)
        .where(Key.holder_user_id == user_id)
        .where(Key.status == KeyStatus.issued)
    )
    return session.exec(statement).first()


def user_has_issued_key_for_object(session: Session, *, user_id, object_id) -> bool:
    return get_issued_key_for_user_and_object(
        session,
        user_id=user_id,
        object_id=object_id,
    ) is not None

def get_my_issued_keys(session: Session, *, user_id: uuid.UUID):
    statement = (
        select(Key, Object.code)
        .join(Object, Key.object_id == Object.id)
        .where(Key.holder_user_id == user_id)
        .where(Key.status == KeyStatus.issued)
        .order_by(Key.created_at.desc())
    )

    results = session.exec(statement).all()

    return [
        {
            "id": key.id,
            "object_id": key.object_id,
            "object_code": object_code,
            "holder_user_id": key.holder_user_id,
            "status": key.status,
            "created_at": key.created_at,
            "updated_at": key.updated_at,
        }
        for key, object_code in results
    ]