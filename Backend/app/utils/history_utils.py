import json
import os
from datetime import datetime
from app.config import settings

def _load() -> list:
    if not os.path.exists(settings.HISTORY_FILE):
        return []
    with open(settings.HISTORY_FILE) as f:
        return json.load(f)

def _save(data: list):
    with open(settings.HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

def add_analysis_record(dataset_id: str, dataset_name: str, user_id: str, status: str):
    history = _load()
    history.append({
        "type": "analysis",
        "dataset_id": dataset_id,
        "dataset_name": dataset_name,
        "user_id": user_id,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    })
    _save(history)

def add_chat_record(dataset_id: str, query: str, user_id: str):
    history = _load()
    history.append({
        "type": "chat",
        "dataset_id": dataset_id,
        "query": query,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    })
    _save(history)

def get_history(user_id: str = None) -> list:
    history = _load()
    if user_id:
        history = [h for h in history if h.get("user_id") == user_id]
    return sorted(history, key=lambda x: x["timestamp"], reverse=True)