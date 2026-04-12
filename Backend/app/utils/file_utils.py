import os
import uuid
import pandas as pd
from fastapi import UploadFile
from app.config import settings

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

def save_upload(file: UploadFile) -> tuple[str, str]:
    """Save file, return (saved_path, unique_filename)."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    unique_name = f"{uuid.uuid4()}{ext}"
    save_path = os.path.join(settings.UPLOAD_DIR, unique_name)
    content = file.file.read()
    with open(save_path, "wb") as f:
        f.write(content)
    return save_path, unique_name

def load_dataframe(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)
    raise ValueError(f"Unsupported format: {ext}")

def get_file_size(path: str) -> str:
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} B"
    elif size < 1024**2:
        return f"{size/1024:.1f} KB"
    return f"{size/1024**2:.1f} MB"