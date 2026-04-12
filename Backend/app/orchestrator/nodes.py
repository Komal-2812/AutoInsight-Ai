import traceback
import pandas as pd
from app.orchestrator.graph_state import GraphState
from app.utils.file_utils         import load_dataframe
from app.services.llm_service     import call_llm_json
from app.services.llm_prompts     import (
    prompt_insights, prompt_kpis,
    prompt_visualization, prompt_questions
)
from app.services.query_router    import execute_query
from app.ai_agents.visualization_agent import _build_chart

# ── Node 1 — Load ─────────────────────────────────────────────────────────────

def node_load(state: GraphState) -> GraphState:
    try:
        df = load_dataframe(state["file_path"])
        return {
            **state,
            "dataframe":    df,
            "row_count":    len(df),
            "column_count": len(df.columns),
            "columns":      df.columns.tolist(),
            "dtypes":       {c: str(t) for c, t in df.dtypes.items()},
            "status":       "running",
        }
    except Exception as e:
        return {**state, "status": "failed", "error": f"Load failed: {e}"}

# ── Node 2 — Clean ────────────────────────────────────────────────────────────

def node_clean(state: GraphState) -> GraphState:
    if state.get("status") == "failed":
        return state
    try:
        df: pd.DataFrame = state["dataframe"].copy()
        log = []

        before = len(df)
        df     = df.drop_duplicates()
        if len(df) < before:
            log.append(f"Removed {before - len(df)} duplicate rows")

        for col in df.columns:
            n = df[col].isnull().sum()
            if n:
                if df[col].dtype in ["float64", "int64"]:
                    df[col].fillna(df[col].median(), inplace=True)
                    log.append(f"Filled {n} nulls in '{col}' with median")
                else:
                    df[col].fillna("Unknown", inplace=True)
                    log.append(f"Filled {n} nulls in '{col}' with 'Unknown'")

        return {**state, "dataframe": df, "cleaning_log": log}
    except Exception as e:
        return {**state, "status": "failed", "error": f"Clean failed: {e}"}

# ── Node 3 — EDA ──────────────────────────────────────────────────────────────

def node_eda(state: GraphState) -> GraphState:
    if state.get("status") == "failed":
        return state
    try:
        df: pd.DataFrame   = state["dataframe"]
        numeric_cols       = df.select_dtypes(include="number").columns.tolist()
        categorical_cols   = df.select_dtypes(include="object").columns.tolist()

        eda = {
            "numeric_cols":       numeric_cols,
            "categorical_cols":   categorical_cols,
            "null_counts":        df.isnull().sum().to_dict(),
            "summary_stats":      df[numeric_cols].describe().round(3).to_dict() if numeric_cols else {},
            "categorical_counts": {
                c: df[c].value_counts().head(10).to_dict()
                for c in categorical_cols[:5]
            },
            "correlations":       (
                df[numeric_cols].corr().round(3).to_dict()
                if len(numeric_cols) > 1 else {}
            ),
            "sample_rows":        df.head(10).to_string(index=False),
            "stats_str":          df[numeric_cols].describe().round(2).to_string() if numeric_cols else "",
        }
        return {**state, "eda": eda}
    except Exception as e:
        return {**state, "status": "failed", "error": f"EDA failed: {e}"}

# ── Node 4 — Insights ─────────────────────────────────────────────────────────

def node_insights(state: GraphState) -> GraphState:
    if state.get("status") == "failed":
        return state
    try:
        eda  = state["eda"]
        cols = state["columns"]

        result = call_llm_json(
            prompt_insights(
                columns=cols,
                stats=eda.get("stats_str", ""),
                sample=eda.get("sample_rows", "")
            )
        )
        summary  = result.get("summary", "")
        insights = result.get("insights", []) + result.get("recommendations", [])
        return {**state, "summary": summary, "insights": insights}

    except Exception as e:
        print(f"[node_insights] Failed: {e}")
        df = state["dataframe"]
        return {
            **state,
            "summary":  f"Dataset has {state['row_count']} rows and {state['column_count']} columns.",
            "insights": [f"Columns: {', '.join(state['columns'][:8])}"],
        }

# ── Node 5 — Charts ───────────────────────────────────────────────────────────

def node_charts(state: GraphState) -> GraphState:
    if state.get("status") == "failed":
        return state
    try:
        df:  pd.DataFrame = state["dataframe"]
        eda: dict         = state["eda"]

        specs  = call_llm_json(
            prompt_visualization(
                columns=state["columns"],
                dtypes=state["dtypes"],
                stats=eda.get("stats_str", "")
            )
        )
        charts = []
        if isinstance(specs, list):
            for spec in specs[:4]:
                chart = _build_chart(df, spec)
                if chart:
                    charts.append(chart)

        if not charts:
            charts = _fallback_charts(df, eda)

        # Build tables
        tables = _build_tables(df, eda)

        return {**state, "charts": charts, "tables": tables}

    except Exception as e:
        print(f"[node_charts] Failed: {e}")
        df  = state["dataframe"]
        eda = state["eda"]
        return {**state, "charts": _fallback_charts(df, eda), "tables": _build_tables(df, eda)}

def _fallback_charts(df: pd.DataFrame, eda: dict) -> list:
    charts = []
    nc = eda.get("numeric_cols", [])
    cc = eda.get("categorical_cols", [])

    if nc:
        c = _build_chart(df, {"id": "c1", "title": f"Distribution of {nc[0]}", "type": "histogram", "x_column": nc[0], "y_column": None})
        if c: charts.append(c)
    if cc and nc:
        c = _build_chart(df, {"id": "c2", "title": f"{cc[0]} by {nc[0]}", "type": "bar", "x_column": cc[0], "y_column": nc[0]})
        if c: charts.append(c)
    if len(nc) >= 2:
        c = _build_chart(df, {"id": "c3", "title": f"{nc[0]} vs {nc[1]}", "type": "scatter", "x_column": nc[0], "y_column": nc[1]})
        if c: charts.append(c)
    return charts

def _build_tables(df: pd.DataFrame, eda: dict) -> list:
    tables = []
    sample = df.head(10)
    tables.append({
        "title":   "Data Preview",
        "headers": sample.columns.tolist(),
        "rows":    [[str(v) if not isinstance(v, (int, float, str)) else v for v in row]
                    for row in sample.values.tolist()]
    })
    for col in eda.get("categorical_cols", [])[:2]:
        vc = df[col].value_counts().head(10).reset_index()
        vc.columns = [col, "Count"]
        tables.append({
            "title":   f"Top values — {col}",
            "headers": vc.columns.tolist(),
            "rows":    [[str(v) for v in row] for row in vc.values.tolist()]
        })
    return tables

# ── Node 6 — KPIs ─────────────────────────────────────────────────────────────

def node_kpis(state: GraphState) -> GraphState:
    if state.get("status") == "failed":
        return state
    try:
        df  = state["dataframe"]
        eda = state["eda"]

        ai_kpis = call_llm_json(
            prompt_kpis(
                columns=state["columns"],
                stats=eda.get("stats_str", ""),
                sample=eda.get("sample_rows", "")
            )
        )
        kpis = [
            {"label": "Total Records", "value": state["row_count"],    "unit": "rows", "trend": "stable"},
            {"label": "Total Columns", "value": state["column_count"], "unit": "cols", "trend": "stable"},
        ]
        if isinstance(ai_kpis, list):
            kpis.extend(ai_kpis[:4])

        return {**state, "kpis": kpis}

    except Exception as e:
        print(f"[node_kpis] Failed: {e}")
        df = state["dataframe"]
        nc = state["eda"].get("numeric_cols", [])
        return {
            **state,
            "kpis": [
                {"label": "Total Records", "value": state["row_count"],    "unit": "rows", "trend": "stable"},
                {"label": "Total Columns", "value": state["column_count"], "unit": "cols", "trend": "stable"},
            ] + [
                {"label": f"Avg {c}", "value": round(df[c].mean(), 2), "unit": "", "trend": "stable"}
                for c in nc[:3]
            ]
        }

# ── Node 7 — Finalize ─────────────────────────────────────────────────────────

def node_finalize(state: GraphState) -> GraphState:
    if state.get("status") == "failed":
        return state
    try:
        suggested = call_llm_json(
            prompt_questions(
                columns=state["columns"],
                summary=state.get("summary", ""),
                insights=state.get("insights", [])
            )
        )
        if not isinstance(suggested, list):
            suggested = []
    except Exception:
        cols = state["columns"]
        suggested = [
            "What are the main trends in this dataset?",
            f"Show the distribution of {cols[0]}" if cols else "Summarize the dataset",
            "Are there any outliers?",
            "What are the top 10 records?",
            "Which columns are most correlated?"
        ]

    return {
        **state,
        "status":              "completed",
        "suggested_questions": suggested,
    }

# ── Node 8 — Query ────────────────────────────────────────────────────────────

def node_query(state: GraphState) -> GraphState:
    query = state.get("user_query", "")
    df    = state.get("dataframe")

    if not query:
        return {**state, "query_result": "", "query_engine": "none"}

    if df is None or (hasattr(df, 'empty') and df.empty):
        return {
            **state,
            "query_result": "No dataset loaded. Please upload a dataset first.",
            "query_engine": "none"
        }

    result = execute_query(query, df)
    return {**state, **result}