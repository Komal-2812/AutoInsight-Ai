from app.services.llm_service import call_gemini_json, prompt_kpis
import pandas as pd

def run(insight_output: dict) -> dict:
    """Extract KPIs from data using Gemini."""
    df: pd.DataFrame = insight_output["dataframe"]
    eda = insight_output["eda"]
    columns = insight_output["columns"]

    # Always include these baseline KPIs
    base_kpis = [
        {"label": "Total Records", "value": len(df), "unit": "rows", "trend": "stable"},
        {"label": "Total Columns", "value": len(df.columns), "unit": "cols", "trend": "stable"},
    ]

    try:
        ai_kpis = call_gemini_json(
            prompt_kpis(
                summary_stats=eda["summary_stats_str"],
                columns=columns
            )
        )
        if isinstance(ai_kpis, list):
            base_kpis.extend(ai_kpis[:4])
    except Exception:
        # Fallback: compute basic numeric KPIs
        for col in eda["numeric_cols"][:3]:
            base_kpis.append({
                "label": f"Avg {col}",
                "value": round(df[col].mean(), 2),
                "unit": "",
                "trend": "stable"
            })

    return {**insight_output, "kpis": base_kpis}