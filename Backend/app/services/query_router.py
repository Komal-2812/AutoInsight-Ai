import pandas as pd
from enum import Enum

from app.services.pandas_service import run_pandas_query
from app.services.pandasai_service import run_pandasai_query
from app.services.llm_service import call_llm
from app.services.llm_prompts import prompt_query


# ── Query Engine Enum ─────────────────────────────────────────────────────────

class QueryEngine(str, Enum):
    PANDAS = "pandas"
    PANDASAI = "pandasai"
    GROQ = "groq"


# ── Query Routing Logic ───────────────────────────────────────────────────────

def route_query(query: str) -> QueryEngine:
    q = query.lower().strip()

    # Simple → Pandas
    pandas_keywords = [
        "how many", "count", "total", "sum", "average", "mean",
        "max", "min", "top", "bottom", "list", "show",
        "first", "last", "rows", "columns", "shape", "describe"
    ]

    if any(kw in q for kw in pandas_keywords) and len(q.split()) < 12:
        return QueryEngine.PANDAS

    # Complex → Groq
    groq_keywords = [
        "why", "explain", "recommend", "suggest", "forecast",
        "predict", "compare", "analyze", "insight", "pattern",
        "trend", "correlation", "cause", "reason"
    ]

    if any(kw in q for kw in groq_keywords):
        return QueryEngine.GROQ

    # Default → PandasAI
    return QueryEngine.PANDASAI


# ── Main Execution Router ─────────────────────────────────────────────────────

def execute_query(query: str, df: pd.DataFrame) -> dict:
    engine = route_query(query)
    result = ""

    print(f"[QueryRouter] '{query[:50]}' → engine: {engine}")

    try:
        # ── SIMPLE: Pandas ──
        if engine == QueryEngine.PANDAS:
            result = run_pandas_query(query, df)

        # ── MEDIUM: PandasAI ──
        elif engine == QueryEngine.PANDASAI:
            result = run_pandasai_query(query, df)

        # ── COMPLEX: Groq LLM ──
        elif engine == QueryEngine.GROQ:
            sample = df.head(20).to_string(index=False)

            schema = {
                col: str(dtype)
                for col, dtype in df.dtypes.items()
            }

            stats = (
                df.select_dtypes(include="number")
                .describe()
                .round(2)
                .to_string()
            )

            prompt = prompt_query(query, str(schema), sample, stats)
            result = call_llm(prompt)

    except Exception as e:
        print(f"[QueryRouter] {engine} failed: {e} → fallback")
        engine = QueryEngine.PANDAS
        result = _pandas_fallback(query, df)

    return {
        "query_result": str(result),
        "query_engine": engine.value,
    }


# ── Fallback ──────────────────────────────────────────────────────────────────

def _pandas_fallback(query: str, df: pd.DataFrame) -> str:
    try:
        return str(run_pandas_query(query, df))
    except Exception:
        return (
            f"Could not process query on dataset "
            f"({df.shape[0]} rows × {df.shape[1]} columns). "
            f"Try a simpler query."
        )