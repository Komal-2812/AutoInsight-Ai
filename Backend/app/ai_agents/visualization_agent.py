import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import uuid
from app.services.llm_service import call_gemini_json, prompt_visualization

def run(eda_output: dict) -> dict:
    """Generate Plotly charts based on EDA and Gemini suggestions."""
    df: pd.DataFrame = eda_output["dataframe"]
    eda = eda_output["eda"]
    columns = eda_output["columns"]
    dtypes = eda_output["dtypes"]

    # Ask Gemini what charts to make
    chart_specs = []
    try:
        chart_specs = call_gemini_json(
            prompt_visualization(
                columns=columns,
                dtypes=dtypes,
                sample=eda["sample_rows"],
                analysis_summary=eda["summary_stats_str"]
            )
        )
        if not isinstance(chart_specs, list):
            chart_specs = []
    except Exception:
        chart_specs = []

    # Fallback: auto-generate basic charts
    if not chart_specs:
        chart_specs = _auto_chart_specs(df, eda)

    charts = []
    for spec in chart_specs[:4]:
        chart = _build_chart(df, spec)
        if chart:
            charts.append(chart)

    return {**eda_output, "charts": charts}

def _auto_chart_specs(df: pd.DataFrame, eda: dict) -> list:
    specs = []
    num_cols = eda["numeric_cols"]
    cat_cols = eda["categorical_cols"]

    if num_cols:
        specs.append({"id": "chart_hist", "title": f"Distribution of {num_cols[0]}",
                       "type": "histogram", "x_column": num_cols[0], "y_column": None})
    if cat_cols and num_cols:
        specs.append({"id": "chart_bar", "title": f"{cat_cols[0]} by {num_cols[0]}",
                       "type": "bar", "x_column": cat_cols[0], "y_column": num_cols[0]})
    if len(num_cols) >= 2:
        specs.append({"id": "chart_scatter", "title": f"{num_cols[0]} vs {num_cols[1]}",
                       "type": "scatter", "x_column": num_cols[0], "y_column": num_cols[1]})
    if cat_cols:
        specs.append({"id": "chart_pie", "title": f"Share by {cat_cols[0]}",
                       "type": "pie", "x_column": cat_cols[0], "y_column": None})
    return specs

def _build_chart(df: pd.DataFrame, spec: dict) -> dict | None:
    try:
        chart_type = spec.get("type", "bar")
        x_col = spec.get("x_column")
        y_col = spec.get("y_column")
        title = spec.get("title", "Chart")
        chart_id = spec.get("id", str(uuid.uuid4())[:8])

        if x_col not in df.columns:
            return None

        if chart_type == "bar":
            if y_col and y_col in df.columns:
                plot_df = df.groupby(x_col)[y_col].mean().reset_index().head(20)
                fig = px.bar(plot_df, x=x_col, y=y_col, title=title)
            else:
                counts = df[x_col].value_counts().head(15).reset_index()
                counts.columns = [x_col, "count"]
                fig = px.bar(counts, x=x_col, y="count", title=title)
        elif chart_type == "line":
            if y_col and y_col in df.columns:
                fig = px.line(df.head(100), x=x_col, y=y_col, title=title)
            else:
                return None
        elif chart_type == "pie":
            counts = df[x_col].value_counts().head(10).reset_index()
            counts.columns = [x_col, "count"]
            fig = px.pie(counts, names=x_col, values="count", title=title)
        elif chart_type == "scatter":
            if not y_col or y_col not in df.columns:
                return None
            fig = px.scatter(df.head(500), x=x_col, y=y_col, title=title)
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x_col, title=title)
        else:
            return None

        fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
        return {"id": chart_id, "title": title, "type": chart_type,
                "plotly_json": fig.to_dict()}
    except Exception:
        return None