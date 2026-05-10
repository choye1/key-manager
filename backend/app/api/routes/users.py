from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core.db import get_session
from app.crud import create_user, get_user_by_email, get_users
from app.models import User, UserCreate, UserPublic, UsersPublic, UserRole

router = APIRouter(prefix="/users", tags=["users"])


def require_admin(current_user: User) -> None:
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required",
        )


@router.get("", response_model=UsersPublic)
def read_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    users = get_users(session)
    return UsersPublic(data=users, count=len(users))


@router.post("", response_model=UserPublic)
def create_new_user(
    user_in: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    existing_user = get_user_by_email(session, user_in.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    return create_user(session, user_in)