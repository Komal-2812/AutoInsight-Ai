"""Generates Python analysis code for reproducibility."""
from app.services.llm_service import call_gemini

def run(columns: list, dtypes: dict, file_path: str) -> str:
    prompt = f"""Generate clean Python code to analyze a dataset with these columns: {columns}
Data types: {dtypes}
File: {file_path}

Include: loading data, basic EDA, visualization with matplotlib/seaborn.
Return only the Python code, no explanation."""
    try:
        return call_gemini(prompt)
    except Exception:
        return f"# Auto-generated analysis\nimport pandas as pd\ndf = pd.read_csv('{file_path}')\nprint(df.describe())"