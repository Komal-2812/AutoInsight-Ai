import pandas as pd
from app.utils.file_utils import load_dataframe

def run(file_path: str) -> dict:
    """Load dataset and return metadata + dataframe."""
    df = load_dataframe(file_path)
    return {
        "dataframe": df,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "file_path": file_path
    }