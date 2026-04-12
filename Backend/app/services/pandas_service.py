import pandas as pd
from typing import Any

def run_pandas_query(query: str, df: pd.DataFrame) -> str:
    q      = query.lower().strip()
    result = _dispatch(q, df)
    return str(result) if result is not None else _fallback(df)

def _dispatch(q: str, df: pd.DataFrame) -> Any:
    numeric_cols     = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    # count / how many
    if "how many" in q or "count" in q:
        col = _find_column(q, df.columns)
        if col:
            return f"{col} has {df[col].count()} non-null values"
        return f"Dataset has {len(df)} rows"

    # sum / total
    if "sum" in q or "total" in q:
        col = _find_column(q, numeric_cols)
        if col:
            return f"Total {col}: {df[col].sum():,.2f}"
        return {c: round(df[c].sum(), 2) for c in numeric_cols[:5]}

    # average / mean
    if "average" in q or "mean" in q:
        col = _find_column(q, numeric_cols)
        if col:
            return f"Average {col}: {df[col].mean():,.2f}"
        return {c: round(df[c].mean(), 2) for c in numeric_cols[:5]}

    # max / maximum
    if "max" in q or "maximum" in q or "highest" in q or "largest" in q:
        col = _find_column(q, numeric_cols)
        if col:
            return f"Maximum {col}: {df[col].max():,.2f}"
        return {c: round(df[c].max(), 2) for c in numeric_cols[:5]}

    # min / minimum
    if "min" in q or "minimum" in q or "lowest" in q or "smallest" in q:
        col = _find_column(q, numeric_cols)
        if col:
            return f"Minimum {col}: {df[col].min():,.2f}"
        return {c: round(df[c].min(), 2) for c in numeric_cols[:5]}

    # top N
    if "top" in q or "first" in q:
        n   = _extract_number(q) or 5
        col = _find_column(q, numeric_cols)
        if col:
            return df.nlargest(n, col)[[col] + categorical_cols[:2]].to_string(index=False)
        return df.head(n).to_string(index=False)

    # bottom N
    if "bottom" in q or "last" in q or "lowest" in q:
        n   = _extract_number(q) or 5
        col = _find_column(q, numeric_cols)
        if col:
            return df.nsmallest(n, col)[[col] + categorical_cols[:2]].to_string(index=False)
        return df.tail(n).to_string(index=False)

    # null / missing
    if "null" in q or "missing" in q or "nan" in q:
        nulls = df.isnull().sum()
        nulls = nulls[nulls > 0]
        return nulls.to_string() if len(nulls) else "No missing values found"

    # unique / distinct
    if "unique" in q or "distinct" in q:
        col = _find_column(q, categorical_cols)
        if col:
            vals = df[col].unique()[:20]
            return f"Unique {col}: {list(vals)}"
        return {c: df[c].nunique() for c in categorical_cols[:5]}

    # shape / rows / columns
    if "shape" in q or "rows" in q or "columns" in q or "size" in q:
        return f"Dataset shape: {df.shape[0]} rows × {df.shape[1]} columns"

    # describe
    if "describe" in q or "summary" in q or "statistics" in q or "stats" in q:
        return df.describe().round(2).to_string()

    return None

def _find_column(query: str, columns: list) -> str | None:
    q = query.lower()
    for col in columns:
        if col.lower() in q:
            return col
    return None

def _extract_number(query: str) -> int | None:
    import re
    match = re.search(r'\b(\d+)\b', query)
    return int(match.group(1)) if match else None

def _fallback(df: pd.DataFrame) -> str:
    return f"Dataset: {df.shape[0]} rows, {df.shape[1]} columns. Columns: {df.columns.tolist()}"