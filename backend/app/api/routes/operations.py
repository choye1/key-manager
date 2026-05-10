from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core.db import get_session
from app.models import (
    HistoryResponse,
    IssueKeyRequest,
    OperationResult,
    ReturnDecisionResponse,
    ReturnKeyRequest,
    User,
    UserRole,
)
from app.services.files import save_upload_file
from app.services.operations import (
    get_object_history,
    issue_key,
    preview_return,
    return_key,
)

router = APIRouter(tags=["operations"])


@router.post("/keys/issue", response_model=OperationResult)
async def issue_key_endpoint(
    object_code: str = Form(...),
    fio: str = Form(...),
    organization: str | None = Form(default=None),
    phone: str | None = Form(default=None),
    photo: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.operator, UserRole.admin}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    photo_path = await save_upload_file(photo, prefix=f"{object_code.lower()}_issue")

    data = IssueKeyRequest(
        object_code=object_code,
        fio=fio,
        organization=organization,
        phone=phone,
        photo_path=photo_path,
    )

    try:
        return issue_key(session, data=data, current_user=current_user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/keys/return", response_model=OperationResult)
async def return_key_endpoint(
    object_code: str = Form(...),
    fio: str = Form(...),
    organization: str | None = Form(default=None),
    phone: str | None = Form(default=None),
    create_new_key_if_no_issued: bool = Form(default=False),
    photo: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.operator, UserRole.admin}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    photo_path = await save_upload_file(photo, prefix=f"{object_code.lower()}_return")

    data = ReturnKeyRequest(
        object_code=object_code,
        fio=fio,
        organization=organization,
        phone=phone,
        photo_path=photo_path,
        create_new_key_if_no_issued=create_new_key_if_no_issued,
    )

    try:
        return return_key(session, data=data, current_user=current_user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/keys/return/preview/{object_code}", response_model=ReturnDecisionResponse)
def preview_return_endpoint(
    object_code: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return preview_return(
        session,
        object_code=object_code.upper().strip(),
        current_user=current_user,
    )


@router.get("/history/{object_code}", response_model=HistoryResponse)
def read_object_history(
    object_code: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_object_history(session, object_code=object_code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
