from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Dataset, User
from app.schemas.chat import ChatRequest, ChatResponse
from app.api.auth import get_current_user

from app.utils.file_utils import load_dataframe
from app.utils.history_utils import add_chat_record

from app.orchestrator.analysis_orchestrator import load_result
from app.orchestrator.workflow import run_query_graph

# fallback (your old system)
from app.ai_agents import chat_agent


router = APIRouter(prefix="/chat", tags=["Chat"])


# ── CHAT ENDPOINT ─────────────────────────────────────────────────────────────

@router.post("", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ── Validate dataset ──
    ds = db.query(Dataset).filter(
        Dataset.id == body.dataset_id,
        Dataset.user_id == current_user.id
    ).first()

    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # ── Try NEW LangGraph query system ──
    try:
        result = run_query_graph(
            dataset_id=body.dataset_id,
            file_path=ds.file_path,
            query=body.query
        )

        answer = result.get("query_result", "No answer found.")

        response = {
            "answer": answer,
            "charts": [],
            "tables": [],
            "kpis": []
        }

    except Exception as e:
        print(f"[Chat] LangGraph failed: {e} → fallback to chat_agent")

        # ── FALLBACK: Old system (important safety) ──
        try:
            df = load_dataframe(ds.file_path)
            analysis_context = load_result(body.dataset_id) or {}

            response = chat_agent.run(df, body.query, analysis_context)

        except Exception as fallback_error:
            raise HTTPException(
                status_code=500,
                detail=f"Chat system failed: {fallback_error}"
            )

    # ── Save chat history ──
    add_chat_record(body.dataset_id, body.query, current_user.id)

    return response


# ── SUGGESTED QUESTIONS ───────────────────────────────────────────────────────

@router.get("/suggested/{dataset_id}")
def get_suggested_questions(
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

    # ── Load analysis result ──
    result = load_result(dataset_id)

    if result and result.get("suggested_questions"):
        return {"questions": result["suggested_questions"]}

    # ── Default fallback questions ──
    return {
        "questions": [
            "What are the main trends in this dataset?",
            "Show me the top 10 records",
            "What is the average value of numeric columns?",
            "Are there any outliers?",
            "Summarize this dataset in 3 key points"
        ]
    }