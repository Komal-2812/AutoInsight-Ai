from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
import pandas as pd

class GraphState(TypedDict):
    # Input
    dataset_id:    str
    file_path:     str
    user_query:    Optional[str]

    # Data
    dataframe:     Optional[Any]      # pd.DataFrame (Any avoids serialization issues)
    row_count:     int
    column_count:  int
    columns:       List[str]
    dtypes:        Dict[str, str]

    # Pipeline outputs
    cleaning_log:  List[str]
    eda:           Dict[str, Any]
    insights:      List[str]
    summary:       str
    kpis:          List[Dict[str, Any]]
    charts:        List[Dict[str, Any]]
    tables:        List[Dict[str, Any]]

    # Chat / query
    query_result:  str
    query_engine:  str               # "pandas" | "pandasai" | "groq"

    # Meta
    status:        str               # "running" | "completed" | "failed"
    error:         Optional[str]
    suggested_questions: List[str]