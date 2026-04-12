import pandas as pd
import json

def run(cleaner_output: dict) -> dict:
    """Generate EDA statistics."""
    df: pd.DataFrame = cleaner_output["dataframe"]

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    summary_stats = {}
    if numeric_cols:
        desc = df[numeric_cols].describe().to_dict()
        summary_stats["numeric"] = desc

    categorical_summary = {}
    for col in categorical_cols[:5]:  # limit to 5 cols
        categorical_summary[col] = df[col].value_counts().head(10).to_dict()

    correlations = {}
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr().round(3)
        correlations = corr.to_dict()

    sample_rows = df.head(5).to_string(index=False)

    return {
        **cleaner_output,
        "eda": {
            "summary_stats": summary_stats,
            "categorical_summary": categorical_summary,
            "correlations": correlations,
            "numeric_cols": numeric_cols,
            "categorical_cols": categorical_cols,
            "null_counts": df.isnull().sum().to_dict(),
            "sample_rows": sample_rows,
            "summary_stats_str": df[numeric_cols].describe().to_string() if numeric_cols else "No numeric columns"
        }
    }