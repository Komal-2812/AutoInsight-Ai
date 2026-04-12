from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
import shutil
import os
import uuid

from app.database import get_db, SessionLocal
from app.models import Dataset, User, Analysis
from app.api.auth import get_current_user

from app.orchestrator.analysis_orchestrator import run_pipeline, load_result

from app.utils.file_utils import get_file_size, load_dataframe
from app.utils.history_utils import add_analysis_record
from app.config import settings


router = APIRouter(prefix="/analysis", tags=["Analysis"])

# ── Running tracker ───────────────────────────────────────────────────────────
_running: set[str] = set()


# ── Upload + analyze ──────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_and_analyze(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in {".csv", ".xlsx", ".xls"}:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Metadata
    try:
        df = load_dataframe(file_path)
        n_rows = str(len(df))
        n_cols = str(len(df.columns))
    except Exception:
        n_rows = n_cols = "0"

    dataset = Dataset(
        user_id=current_user.id,
        file_name=file.filename,
        original_name=file.filename,
        file_path=file_path,
        file_size=get_file_size(file_path),
        row_count=n_rows,
        column_count=n_cols,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # Analysis record
    record = Analysis(
        dataset_id=dataset.id,
        user_id=current_user.id,
        status="running",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    _running.add(dataset.id)

    add_analysis_record(dataset.id, dataset.file_name, current_user.id, "running")

    background_tasks.add_task(
        _run_pipeline_bg,
        record.id,
        dataset.id,
        file_path
    )

    return {
        "dataset_id": dataset.id,
        "file_name": file.filename,
        "status": "running",
        "message": "Analysis started",
    }


# ── Start analysis (existing dataset) ─────────────────────────────────────────

@router.post("/start/{dataset_id}")
async def start_analysis(
    dataset_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ds = _get_dataset_or_404(dataset_id, current_user.id, db)

    if dataset_id in _running:
        return {
            "dataset_id": dataset_id,
            "status": "running",
            "message": "Already running"
        }

    record = Analysis(
        dataset_id=dataset_id,
        user_id=current_user.id,
        status="running",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    _running.add(dataset_id)

    add_analysis_record(dataset_id, ds.file_name, current_user.id, "running")

    background_tasks.add_task(
        _run_pipeline_bg,
        record.id,
        dataset_id,
        ds.file_path
    )

    return {
        "dataset_id": dataset_id,
        "status": "running",
        "message": "Analysis started"
    }


# ── Get full analysis ─────────────────────────────────────────────────────────

@router.get("/{dataset_id}")
async def get_analysis(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_dataset_or_404(dataset_id, current_user.id, db)

    if dataset_id in _running:
        return {"status": "running", "message": "Analysis in progress"}

    result = load_result(dataset_id)

    if result:
        return _format_response(result)

    return {"status": "pending", "message": "Analysis not started"}


# ── Status endpoint ───────────────────────────────────────────────────────────

@router.get("/status/{dataset_id}")
async def get_status(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_dataset_or_404(dataset_id, current_user.id, db)

    if dataset_id in _running:
        return {"status": "running", "dataset_id": dataset_id}

    result = load_result(dataset_id)

    if result:
        return {
            "status": result.get("status", "completed"),
            "dataset_id": dataset_id
        }

    return {"status": "pending", "dataset_id": dataset_id}


# ── Background runner ─────────────────────────────────────────────────────────

def _run_pipeline_bg(record_id: str, dataset_id: str, file_path: str):
    db = SessionLocal()

    try:
        result = run_pipeline(dataset_id, file_path)
        status = result.get("status", "completed")

        record = db.query(Analysis).filter(Analysis.id == record_id).first()

        if record:
            record.status = status
            record.result_path = f"data/analysis/{dataset_id}.json"
            record.updated_at = datetime.utcnow()

            if status == "failed":
                record.error = result.get("error", "Unknown")

            db.commit()

        add_analysis_record(dataset_id, "", record.user_id if record else "", status)

    except Exception as e:
        record = db.query(Analysis).filter(Analysis.id == record_id).first()

        if record:
            record.status = "failed"
            record.error = str(e)
            record.updated_at = datetime.utcnow()
            db.commit()

        print(f"[Pipeline BG] Error: {e}")

    finally:
        _running.discard(dataset_id)
        db.close()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_dataset_or_404(dataset_id: str, user_id: str, db: Session) -> Dataset:
    ds = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == user_id
    ).first()

    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return ds


def _format_response(result: dict) -> dict:
    return {
        "status": result.get("status", "completed"),
        "dataset_id": result.get("dataset_id", ""),
        "summary": result.get("summary", ""),
        "kpis": _format_kpis(result.get("kpis", [])),
        "charts": _format_charts(result.get("charts", [])),
        "tables": result.get("tables", []),
        "insights": result.get("insights", []),
        "suggested_questions": result.get("suggested_questions", []),
        "columns": result.get("columns", []),
        "row_count": result.get("row_count", 0),
        "column_count": result.get("column_count", 0),
        "cleaning_log": result.get("cleaning_log", []),
    }


def _format_kpis(kpis: list) -> list:
    return [
        {
            "title": k.get("label", k.get("title", "")),
            "value": k.get("value", ""),
            "unit": k.get("unit", ""),
            "trend": k.get("trend", "stable"),
        }
        for k in kpis
    ]


def _format_charts(charts: list) -> list:
    formatted = []

    for chart in charts:
        pj = chart.get("plotly_json", {})

        formatted.append({
            "id": chart.get("id", ""),
            "title": chart.get("title", ""),
            "type": chart.get("type", "bar"),
            "data": pj.get("data", []),
            "layout": {
                **pj.get("layout", {}),
                "template": "plotly_white",
                "margin": {"l": 20, "r": 20, "t": 40, "b": 20},
            },
        })

    return formatted