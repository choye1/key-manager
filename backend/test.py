from sqlmodel import Session

from app.core.db import engine
from app.crud import create_user, get_user_by_email
from app.models import UserCreate, UserRole

with Session(engine) as session:
    existing_user = get_user_by_email(session, "admin@example.com")
    if existing_user:
        print("User already exists:", existing_user.email)
    else:
        user = create_user(
            session,
            UserCreate(
                email="admin@example.com",
                password="12345678",
                full_name="Admin",
                role=UserRole.admin,
                is_active=True,
            ),
        )
        print("Created user:", user.email, user.id)