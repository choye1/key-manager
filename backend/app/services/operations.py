from sqlmodel import Session

from app.crud import (
    create_key,
    create_operation,
    get_available_key_for_object,
    get_object_by_code,
    get_operations_by_object_id,
    get_issued_key_for_user_and_object,
    user_has_issued_key_for_object,
)
from app.models import (
    HistoryRecord,
    HistoryResponse,
    IssueKeyRequest,
    KeyCreate,
    KeyStatus,
    OperationResult,
    OperationType,
    ReturnDecisionResponse,
    ReturnKeyRequest,
    User,
)


def issue_key(
    session: Session,
    *,
    data: IssueKeyRequest,
    current_user: User,
) -> OperationResult:
    obj = get_object_by_code(session, data.object_code)
    if obj is None:
        raise ValueError("Object not found")

    if user_has_issued_key_for_object(
        session,
        user_id=current_user.id,
        object_id=obj.id,
    ):
        raise ValueError(
            "You already have an issued key for this object"
        )

    key = get_available_key_for_object(session, obj.id)
    if key is None:
        raise ValueError("No available keys for this object")

    key.status = KeyStatus.issued
    key.holder_user_id = current_user.id
    session.add(key)
    session.commit()
    session.refresh(key)

    operation = create_operation(
        session,
        key_id=key.id,
        object_id=obj.id,
        user_id=current_user.id,
        operation_type=OperationType.issue,
        fio=data.fio,
        organization=data.organization,
        phone=data.phone,
        photo_path=data.photo_path,
    )

    return OperationResult(
        message="Key issued successfully",
        operation_id=operation.id,
        key_id=key.id,
        object_id=obj.id,
        object_code=obj.code,
        status=key.status.value,
    )


def return_key(
    session: Session,
    *,
    data: ReturnKeyRequest,
    current_user: User,
) -> OperationResult:
    obj = get_object_by_code(session, data.object_code)
    if obj is None:
        raise ValueError(
            "Object not found. Verify the code before continuing."
        )

    key = get_issued_key_for_user_and_object(
        session,
        user_id=current_user.id,
        object_id=obj.id,
    )

    if key is None:
        if not data.create_new_key_if_no_issued:
            raise ValueError(
                "You do not have an issued key for this object"
            )

        key = create_key(
            session,
            KeyCreate(
                object_id=obj.id,
                status=KeyStatus.available,
            ),
        )
    else:
        key.status = KeyStatus.available
        key.holder_user_id = None
        session.add(key)
        session.commit()
        session.refresh(key)

    operation = create_operation(
        session,
        key_id=key.id,
        object_id=obj.id,
        user_id=current_user.id,
        operation_type=OperationType.return_,
        fio=data.fio,
        organization=data.organization,
        phone=data.phone,
        photo_path=data.photo_path,
    )

    return OperationResult(
        message="Key returned successfully",
        operation_id=operation.id,
        key_id=key.id,
        object_id=obj.id,
        object_code=obj.code,
        status=key.status.value,
    )


def preview_return(session: Session, *, object_code: str, current_user: User) -> ReturnDecisionResponse:
    obj = get_object_by_code(session, object_code)
    if obj is None:
        return ReturnDecisionResponse(
            object_code=object_code,
            object_exists=False,
            issued_keys_count=0,
            can_return_existing_key=False,
            can_create_new_key=False,
            message="Object not found. Verify the entered code before continuing.",
        )

    key = get_issued_key_for_user_and_object(
        session,
        user_id=current_user.id,
        object_id=obj.id,
    )

    return ReturnDecisionResponse(
        object_code=obj.code,
        object_exists=True,
        issued_keys_count=1 if key else 0,
        can_return_existing_key=key is not None,
        can_create_new_key=True,
        message=(
            "You have an issued key for this object."
            if key is not None
            else "You do not have an issued key for this object."
        ),
    )


def get_object_history(session: Session, *, object_code: str) -> HistoryResponse:
    obj = get_object_by_code(session, object_code)
    if obj is None:
        raise ValueError("Object not found")

    operations = get_operations_by_object_id(session, obj.id)

    data = [
        HistoryRecord(
            operation_id=operation.id,
            key_id=operation.key_id,
            object_id=operation.object_id,
            object_code=obj.code,
            type=operation.type.value,
            fio=operation.fio,
            organization=operation.organization,
            phone=operation.phone,
            photo_path=operation.photo_path,
            operation_time=operation.operation_time,
            created_at=operation.created_at,
            created_by_user_id=operation.user_id,
        )
        for operation in operations
    ]

    return HistoryResponse(
        object_code=obj.code,
        count=len(data),
        data=data,
    )