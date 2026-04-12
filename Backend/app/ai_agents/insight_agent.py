from app.services.llm_service import call_gemini_json, prompt_insights

def run(eda_output: dict) -> dict:
    """Use Gemini to generate textual insights and recommendations."""
    eda = eda_output["eda"]
    columns = eda_output["columns"]

    try:
        result = call_gemini_json(
            prompt_insights(
                summary_stats=eda["summary_stats_str"],
                columns=columns,
                sample_rows=eda["sample_rows"]
            )
        )
        summary = result.get("summary", "Analysis complete.")
        insights = result.get("insights", [])
        insights += result.get("recommendations", [])
    except Exception as e:
        summary = f"Dataset has {eda_output['row_count']} rows and {eda_output['column_count']} columns."
        insights = [
            f"Dataset contains: {', '.join(columns[:5])}",
            f"Numeric columns: {', '.join(eda['numeric_cols'][:3])}",
            f"Categorical columns: {', '.join(eda['categorical_cols'][:3])}"
        ]

    return {**eda_output, "summary": summary, "insights": insights}