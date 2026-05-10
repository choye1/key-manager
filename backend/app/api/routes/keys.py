from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core.db import get_session
from app.crud import (
    create_key,
    get_keys_filtered,
    get_object_by_code,
    get_object_by_id,
    get_my_issued_keys,
)
from app.models import KeyCreate, KeyPublic, KeysPublic, KeyStatus, User, UserRole, IssuedKeysResponse


router = APIRouter(prefix="/keys", tags=["keys"])


@router.get("/my-issued", response_model=IssuedKeysResponse)
def read_my_keys(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    keys = get_my_issued_keys(session, user_id=current_user.id)

    return IssuedKeysResponse(
        object_code="multiple",
        count=len(keys),
        data=keys,
    )

@router.post("", response_model=KeyPublic)
def create_new_key(
    key_in: KeyCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.operator, UserRole.admin}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    obj = get_object_by_id(session, key_in.object_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Object not found",
        )

    return create_key(session, key_in)


@router.get("", response_model=KeysPublic)
def read_keys(
    object_code: str | None = Query(default=None),
    status: KeyStatus | None = Query(default=None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    object_id = None

    if object_code is not None:
        obj = get_object_by_code(session, object_code)
        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Object not found",
            )
        object_id = obj.id

    keys = get_keys_filtered(session, object_id=object_id, status=status)
    return KeysPublic(data=keys, count=len(keys))
