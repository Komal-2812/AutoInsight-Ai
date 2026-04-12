from pydantic import BaseModel
from typing import Any, List, Optional

class ChatRequest(BaseModel):
    dataset_id: str
    query: str

class ChatResponse(BaseModel):
    answer: str
    charts: Optional[List[dict]] = []
    tables: Optional[List[dict]] = []
    kpis: Optional[List[dict]] = []