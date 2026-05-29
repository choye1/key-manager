from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def ensure_upload_dir() -> Path:
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


async def save_upload_file(file: UploadFile, prefix: str) -> str:
    upload_dir = ensure_upload_dir()

    original_name = file.filename or "file"
    ext = Path(original_name).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .jpg, .jpeg and .png files are allowed",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is too large",
        )

    safe_name = f"{prefix}_{uuid4().hex}{ext}"
    destination = upload_dir / safe_name

    destination.write_bytes(content)

    return f"uploads/{safe_name}"
