from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Dataset, User
from app.api.auth import get_current_user
from app.orchestrator.workflow import run_query_graph
from app.utils.history_utils import add_chat_record

router = APIRouter(prefix="/query", tags=["Query"])

class QueryRequest(BaseModel):
    dataset_id: str
    query:      str

@router.post("")
async def run_query(
    body: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    ds = db.query(Dataset).filter(
        Dataset.id      == body.dataset_id,
        Dataset.user_id == current_user.id,
    ).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    result = run_query_graph(
        dataset_id=body.dataset_id,
        file_path=ds.file_path,
        query=body.query,
    )

    add_chat_record(body.dataset_id, body.query, current_user.id)

    return {
        "query":        body.query,
        "query_result": result.get("query_result", "No result"),
        "query_engine": result.get("query_engine", "unknown"),
        "dataset_id":   body.dataset_id,
        "status":       result.get("status", "completed"),
    }