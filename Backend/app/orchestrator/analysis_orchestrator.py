import json
import os
import time
from app.config import settings
from app.ai_agents import (
    data_loader_agent,
    cleaning_agent,
    eda_agent,
    visualization_agent,
    insight_agent,
    kpi_agent,
    question_agent
)
from app.ai_agents import debug_agent

def run_pipeline(dataset_id: str, file_path: str) -> dict:
    state = {}

    # Step 1 — Load (no Gemini)
    try:
        print(f"[Pipeline] Step 1: Loading data...")
        state = data_loader_agent.run(file_path)
    except Exception as e:
        return _failed(dataset_id, e, "data_loader")

    # Step 2 — Clean (no Gemini)
    try:
        print(f"[Pipeline] Step 2: Cleaning data...")
        state = cleaning_agent.run(state)
    except Exception as e:
        return _failed(dataset_id, e, "cleaning")

    # Step 3 — EDA (no Gemini)
    try:
        print(f"[Pipeline] Step 3: Running EDA...")
        state = eda_agent.run(state)
    except Exception as e:
        return _failed(dataset_id, e, "eda")

    # Step 4 — Visualization (uses Gemini)
    try:
        print(f"[Pipeline] Step 4: Building charts...")
        state = visualization_agent.run(state)
        time.sleep(5)  # wait between Gemini calls
    except Exception as e:
        print(f"[Pipeline] Visualization failed: {e} — continuing with fallback")
        state["charts"] = []

    # Step 5 — Insights (uses Gemini)
    try:
        print(f"[Pipeline] Step 5: Generating insights...")
        state = insight_agent.run(state)
        time.sleep(5)  # wait between Gemini calls
    except Exception as e:
        print(f"[Pipeline] Insights failed: {e} — using fallback")
        state["summary"] = f"Dataset has {state['row_count']} rows and {state['column_count']} columns."
        state["insights"] = [f"Columns: {', '.join(state['columns'][:5])}"]

    # Step 6 — KPIs (uses Gemini)
    try:
        print(f"[Pipeline] Step 6: Extracting KPIs...")
        state = kpi_agent.run(state)
        time.sleep(3)
    except Exception as e:
        print(f"[Pipeline] KPI failed: {e} — using fallback")
        state["kpis"] = [
            {"label": "Total Records", "value": state["row_count"], "unit": "rows", "trend": "stable"},
            {"label": "Total Columns", "value": state["column_count"], "unit": "cols", "trend": "stable"}
        ]

    # Step 7 — Suggested questions (uses Gemini)
    suggested_questions = []
    try:
        print(f"[Pipeline] Step 7: Generating suggested questions...")
        suggested_questions = question_agent.run(
            columns=state["columns"],
            insights=state.get("insights", []),
            summary=state.get("summary", "")
        )
    except Exception as e:
        print(f"[Pipeline] Questions failed: {e}")

    # Build tables
    tables = _build_tables(state)

    result = {
        "dataset_id": dataset_id,
        "status": "completed",
        "summary": state.get("summary", ""),
        "kpis": state.get("kpis", []),
        "charts": state.get("charts", []),
        "tables": tables,
        "insights": state.get("insights", []),
        "suggested_questions": suggested_questions,
        "cleaning_log": state.get("cleaning_issues", []),
        "columns": state["columns"],
        "row_count": state["row_count"],
        "column_count": state["column_count"]
    }

    _save_result(dataset_id, result)
    print(f"[Pipeline] Complete! Status: completed")
    return result

def _failed(dataset_id: str, error: Exception, stage: str) -> dict:
    debug_info = debug_agent.run(error, stage)
    return {
        "dataset_id": dataset_id,
        "status": "failed",
        "error": debug_info,
        "summary": f"Pipeline failed at {stage}",
        "kpis": [], "charts": [], "tables": [], "insights": []
    }

def _build_tables(state: dict) -> list:
    tables = []
    df = state["dataframe"]
    eda = state["eda"]

    sample = df.head(10)
    tables.append({
        "title": "Data Preview",
        "headers": sample.columns.tolist(),
        "rows": _safe_rows(sample)
    })

    for col in eda["categorical_cols"][:2]:
        vc = df[col].value_counts().head(10).reset_index()
        vc.columns = [col, "Count"]
        tables.append({
            "title": f"Top values — {col}",
            "headers": vc.columns.tolist(),
            "rows": _safe_rows(vc)
        })

    return tables

def _safe_rows(df) -> list:
    return [
        [str(v) if not isinstance(v, (int, float, str)) else v for v in row]
        for row in df.values.tolist()
    ]

def _save_result(dataset_id: str, result: dict):
    path = os.path.join(settings.ANALYSIS_DIR, f"{dataset_id}.json")
    serializable = {k: v for k, v in result.items() if k != "dataframe"}
    with open(path, "w") as f:
        json.dump(serializable, f, default=str)

def load_result(dataset_id: str) -> dict | None:
    path = os.path.join(settings.ANALYSIS_DIR, f"{dataset_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)