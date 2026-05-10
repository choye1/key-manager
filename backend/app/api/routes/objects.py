from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core.db import get_session
from app.crud import (
    create_object,
    get_issued_keys_for_object,
    get_object_by_code,
    get_objects,
)
from app.models import (
    IssuedKeyPublic,
    IssuedKeysResponse,
    ObjectCreate,
    ObjectPublic,
    ObjectsPublic,
    User,
    UserRole,
)

router = APIRouter(prefix="/objects", tags=["objects"])


@router.post("", response_model=ObjectPublic)
def create_new_object(
    object_in: ObjectCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.operator, UserRole.admin}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    existing_object = get_object_by_code(session, object_in.code)
    if existing_object is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Object with this code already exists",
        )

    return create_object(session, object_in)


@router.get("", response_model=ObjectsPublic)
def read_objects(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    objects = get_objects(session)
    return ObjectsPublic(data=objects, count=len(objects))


@router.get("/{code}", response_model=ObjectPublic)
def read_object_by_code(
    code: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    obj = get_object_by_code(session, code)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Object not found",
        )

    return obj

@router.get("/{code}/issued-keys", response_model=IssuedKeysResponse)
def read_issued_keys_for_object(
    code: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    obj = get_object_by_code(session, code)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Object not found",
        )

    issued_keys = get_issued_keys_for_object(session, obj.id)

    return IssuedKeysResponse(
        object_code=obj.code,
        count=len(issued_keys),
        data=issued_keys,
    )