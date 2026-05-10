import re
import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import EmailStr, field_validator
from sqlalchemy import DateTime, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    viewer = "viewer"
    operator = "operator"
    admin = "admin"


class ObjectType(str, Enum):
    indoor = "indoor"
    outdoor = "outdoor"


class KeyStatus(str, Enum):
    available = "available"
    issued = "issued"
    archived = "archived"
    lost = "lost"


class OperationType(str, Enum):
    issue = "issue"
    return_ = "return"


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)

    phone: str | None = Field(default=None, max_length=50)
    organization: str | None = Field(default=None, max_length=255)

    role: UserRole = Field(
        default=UserRole.viewer,
        sa_type=SAEnum(UserRole, name="user_role"),
    )
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole | None = Field(
        default=None,
        sa_type=SAEnum(UserRole, name="user_role"),
    )
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
    )

    operations: list["Operation"] = Relationship(back_populates="user")


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class ObjectBase(SQLModel):
    code: str = Field(index=True, unique=True, max_length=6)
    type: ObjectType = Field(
        sa_type=SAEnum(ObjectType, name="object_type"),
    )
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        value = value.upper().strip()
        if not re.fullmatch(r"(CH|CO|UF)\d{4}", value):
            raise ValueError("Object code must match ZZXXXX where ZZ is CH, CO or UF")
        return value


class ObjectCreate(ObjectBase):
    pass


class ObjectUpdate(SQLModel):
    code: str | None = Field(default=None, max_length=6)
    type: ObjectType | None = Field(
        default=None,
        sa_type=SAEnum(ObjectType, name="object_type"),
    )
    is_active: bool | None = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.upper().strip()
        if not re.fullmatch(r"(CH|CO|UF)\d{4}", value):
            raise ValueError("Object code must match ZZXXXX where ZZ is CH, CO or UF")
        return value


class Object(ObjectBase, table=True):
    __tablename__ = "objects"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
    )

    keys: list["Key"] = Relationship(back_populates="object")
    operations: list["Operation"] = Relationship(back_populates="object")


class ObjectPublic(ObjectBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ObjectsPublic(SQLModel):
    data: list[ObjectPublic]
    count: int


class KeyBase(SQLModel):
    status: KeyStatus = Field(
        default=KeyStatus.available,
        sa_type=SAEnum(KeyStatus, name="key_status"),
    )


class KeyCreate(SQLModel):
    object_id: uuid.UUID
    status: KeyStatus = Field(
        default=KeyStatus.available,
        sa_type=SAEnum(KeyStatus, name="key_status"),
    )


class KeyUpdate(SQLModel):
    status: KeyStatus | None = Field(
        default=None,
        sa_type=SAEnum(KeyStatus, name="key_status"),
    )


class Key(KeyBase, table=True):
    __tablename__ = "keys"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    object_id: uuid.UUID = Field(
        foreign_key="objects.id",
        nullable=False,
        ondelete="CASCADE",
    )
    holder_user_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="users.id",
        nullable=True,
        ondelete="SET NULL",
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
    )

    object: "Object" = Relationship(back_populates="keys")
    operations: list["Operation"] = Relationship(back_populates="key")


class KeyPublic(KeyBase):
    id: uuid.UUID
    object_id: uuid.UUID
    holder_user_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class KeysPublic(SQLModel):
    data: list[KeyPublic]
    count: int


class OperationBase(SQLModel):
    type: OperationType = Field(
        sa_type=SAEnum(OperationType, name="operation_type"),
    )
    fio: str | None = Field(default=None, max_length=255)
    organization: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    photo_path: str | None = None
    operation_time: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
    )


class OperationCreate(OperationBase):
    key_id: uuid.UUID
    object_id: uuid.UUID
    user_id: uuid.UUID


class OperationUpdate(SQLModel):
    fio: str | None = Field(default=None, max_length=255)
    organization: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    photo_path: str | None = None
    operation_time: datetime | None = None


class Operation(OperationBase, table=True):
    __tablename__ = "operations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    key_id: uuid.UUID = Field(
        foreign_key="keys.id",
        nullable=False,
        ondelete="CASCADE",
    )
    object_id: uuid.UUID = Field(
        foreign_key="objects.id",
        nullable=False,
        ondelete="CASCADE",
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        ondelete="RESTRICT",
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
    )

    key: "Key" = Relationship(back_populates="operations")
    object: "Object" = Relationship(back_populates="operations")
    user: "User" = Relationship(back_populates="operations")


class OperationPublic(OperationBase):
    id: uuid.UUID
    key_id: uuid.UUID
    object_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime


class OperationsPublic(SQLModel):
    data: list[OperationPublic]
    count: int


class LoginRequest(SQLModel):
    email: EmailStr
    password: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class Message(SQLModel):
    message: str


class IssueKeyRequest(SQLModel):
    object_code: str = Field(max_length=6)
    fio: str = Field(max_length=255)
    organization: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    photo_path: str | None = None

    @field_validator("object_code")
    @classmethod
    def validate_object_code(cls, value: str) -> str:
        value = value.upper().strip()
        if not re.fullmatch(r"(CH|CO|UF)\d{4}", value):
            raise ValueError("Object code must match ZZXXXX where ZZ is CH, CO or UF")
        return value


class OperationResult(SQLModel):
    message: str
    operation_id: uuid.UUID
    key_id: uuid.UUID
    object_id: uuid.UUID
    object_code: str
    status: str


class ReturnKeyRequest(SQLModel):
    object_code: str = Field(max_length=6)
    fio: str = Field(max_length=255)
    organization: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    photo_path: str | None = None
    create_new_key_if_no_issued: bool = False

    @field_validator("object_code")
    @classmethod
    def validate_object_code(cls, value: str) -> str:
        value = value.upper().strip()
        if not re.fullmatch(r"(CH|CO|UF)\d{4}", value):
            raise ValueError("Object code must match ZZXXXX where ZZ is CH, CO or UF")
        return value


class HistoryRecord(SQLModel):
    operation_id: uuid.UUID
    key_id: uuid.UUID
    object_id: uuid.UUID
    object_code: str
    type: str
    fio: str | None
    organization: str | None
    phone: str | None
    photo_path: str | None
    operation_time: datetime
    created_at: datetime
    created_by_user_id: uuid.UUID


class HistoryResponse(SQLModel):
    object_code: str
    count: int
    data: list[HistoryRecord]


class IssuedKeyPublic(SQLModel):
    id: uuid.UUID
    object_id: uuid.UUID
    object_code: str
    holder_user_id: uuid.UUID | None
    status: KeyStatus
    created_at: datetime
    updated_at: datetime


class IssuedKeysResponse(SQLModel):
    object_code: str
    count: int
    data: list[IssuedKeyPublic]


class ReturnDecisionResponse(SQLModel):
    object_code: str
    object_exists: bool
    issued_keys_count: int
    can_return_existing_key: bool
    can_create_new_key: bool
    message: str