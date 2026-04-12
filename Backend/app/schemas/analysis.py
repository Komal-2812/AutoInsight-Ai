from pydantic import BaseModel
from typing import Any, List, Optional

class KPI(BaseModel):
    label: str
    value: Any
    unit: Optional[str] = None
    trend: Optional[str] = None

class ChartData(BaseModel):
    id: str
    title: str
    type: str
    plotly_json: dict

class TableData(BaseModel):
    title: str
    headers: List[str]
    rows: List[List[Any]]

class AnalysisResult(BaseModel):
    dataset_id: str
    summary: str
    kpis: List[KPI]
    charts: List[ChartData]
    tables: List[TableData]
    insights: List[str]
    status: str = "completed"