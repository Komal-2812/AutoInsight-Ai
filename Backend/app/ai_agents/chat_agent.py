import json
import pandas as pd
from app.services.llm_service import call_gemini_json, prompt_chat
from app.ai_agents.visualization_agent import _build_chart

def run(df: pd.DataFrame, query: str, analysis_context: dict) -> dict:
    """Answer a user question about their dataset."""
    # Build context string
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    dataset_context = df.head(20).to_string(index=False)
    if numeric_cols:
        dataset_context += "\n\nStats:\n" + df[numeric_cols].describe().to_string()

    schema = {col: str(dtype) for col, dtype in df.dtypes.items()}

    try:
        result = call_gemini_json(prompt_chat(query, dataset_context, str(schema)))
    except Exception as e:
        return {
            "answer": f"I encountered an error analyzing your data: {e}",
            "charts": [], "tables": [], "kpis": []
        }

    answer = result.get("answer", "I couldn't find an answer in the dataset.")
    charts = []
    tables = []
    kpis = result.get("kpis", [])

    # Optionally generate a chart
    if result.get("generate_chart") and result.get("chart_description"):
        chart_desc = result["chart_description"]
        # Auto-pick columns based on description
        cat_cols = df.select_dtypes(include="object").columns.tolist()
        spec = {
            "id": "chat_chart",
            "title": chart_desc,
            "type": "bar",
            "x_column": cat_cols[0] if cat_cols else (numeric_cols[0] if numeric_cols else None),
            "y_column": numeric_cols[0] if numeric_cols else None
        }
        chart = _build_chart(df, spec)
        if chart:
            charts.append(chart)

    # Optionally generate a table
    if result.get("generate_table"):
        sample = df.head(10)
        tables.append({
            "title": "Data Sample",
            "headers": sample.columns.tolist(),
            "rows": sample.values.tolist()
        })

    return {"answer": answer, "charts": charts, "tables": tables, "kpis": kpis}