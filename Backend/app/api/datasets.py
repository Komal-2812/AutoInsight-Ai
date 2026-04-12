from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Dataset, User
from app.schemas.dataset import DatasetResponse, RenameRequest
from app.api.auth import get_current_user
from app.utils.file_utils import save_upload, load_dataframe, get_file_size
from app.orchestrator.analysis_orchestrator import load_result
import os

router = APIRouter(prefix="/dataset", tags=["Dataset"])


@router.post("/upload", response_model=DatasetResponse, status_code=201)
def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        file_path, unique_name = save_upload(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        df = load_dataframe(file_path)
        row_count = str(len(df))
        col_count = str(len(df.columns))
    except Exception:
        row_count = "0"
        col_count = "0"

    dataset = Dataset(
        user_id=current_user.id,
        file_name=file.filename,
        original_name=file.filename,
        file_path=file_path,
        file_size=get_file_size(file_path),
        row_count=row_count,
        column_count=col_count
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


@router.get("/list", response_model=List[DatasetResponse])
def list_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Dataset)\
             .filter(Dataset.user_id == current_user.id)\
             .order_by(Dataset.created_at.desc())\
             .all()


@router.get("/{dataset_id}/summary")
def get_dataset_summary(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ds = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    result = load_result(dataset_id)
    if result:
        return {
            "dataset_id": dataset_id,
            "file_name": ds.file_name,
            "row_count": ds.row_count,
            "column_count": ds.column_count,
            "has_analysis": True,
            "summary": result.get("summary", ""),
            "kpi_count": len(result.get("kpis", [])),
            "chart_count": len(result.get("charts", [])),
            "status": result.get("status", "completed")
        }

    return {
        "dataset_id": dataset_id,
        "file_name": ds.file_name,
        "row_count": ds.row_count,
        "column_count": ds.column_count,
        "has_analysis": False,
        "status": "pending"
    }


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ds = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return ds


@router.put("/{dataset_id}/rename")
def rename_dataset(
    dataset_id: str,
    body: RenameRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ds = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    ds.file_name = body.file_name
    db.commit()
    return {"message": "Renamed successfully"}


@router.delete("/{dataset_id}")
def delete_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ds = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if os.path.exists(ds.file_path):
        os.remove(ds.file_path)

    # Also delete analysis file if exists
    analysis_path = f"data/analysis/{dataset_id}.json"
    if os.path.exists(analysis_path):
        os.remove(analysis_path)

    db.delete(ds)
    db.commit()
    return {"message": "Deleted successfully"}