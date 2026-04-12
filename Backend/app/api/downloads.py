from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Dataset, User
from app.api.auth import get_current_user
from app.orchestrator.analysis_orchestrator import load_result
from app.services.report_service import generate_pdf_report
from app.config import settings
import os
import pandas as pd
import plotly.io as pio

router = APIRouter(prefix="/download", tags=["Downloads"])

@router.get("/report/{dataset_id}")
def download_report(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _assert_owner(dataset_id, current_user, db)
    analysis = load_result(dataset_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found. Run analysis first.")
    pdf_path = generate_pdf_report(dataset_id, analysis)
    return FileResponse(pdf_path, media_type="application/pdf",
                        filename=f"report_{dataset_id}.pdf")

@router.get("/data/{dataset_id}")
def download_data(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ds = _assert_owner(dataset_id, current_user, db)
    csv_path = os.path.join(settings.REPORT_DIR, f"data_{dataset_id}.csv")
    df = pd.read_csv(ds.file_path) if ds.file_path.endswith(".csv") else pd.read_excel(ds.file_path)
    df.to_csv(csv_path, index=False)
    return FileResponse(csv_path, media_type="text/csv", filename=f"data_{dataset_id}.csv")

@router.get("/chart/{dataset_id}/{chart_index}")
def download_chart(
    dataset_id: str,
    chart_index: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _assert_owner(dataset_id, current_user, db)
    analysis = load_result(dataset_id)
    if not analysis or not analysis.get("charts"):
        raise HTTPException(status_code=404, detail="No charts found")
    charts = analysis["charts"]
    if chart_index >= len(charts):
        raise HTTPException(status_code=404, detail="Chart index out of range")
    import plotly.graph_objects as go
    chart_data = charts[chart_index]
    fig = go.Figure(chart_data["plotly_json"])
    img_path = os.path.join(settings.REPORT_DIR, f"chart_{dataset_id}_{chart_index}.png")
    fig.write_image(img_path, width=1200, height=700)
    return FileResponse(img_path, media_type="image/png",
                        filename=f"chart_{chart_index}.png")

def _assert_owner(dataset_id: str, current_user: User, db: Session) -> Dataset:
    ds = db.query(Dataset).filter(
        Dataset.id == dataset_id, Dataset.user_id == current_user.id
    ).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return ds