import pandas as pd

def run(loader_output: dict) -> dict:
    """Clean dataset: handle nulls, duplicates, type inference."""
    df: pd.DataFrame = loader_output["dataframe"].copy()
    issues = []

    # Remove full duplicates
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    if removed:
        issues.append(f"Removed {removed} duplicate rows")

    # Fill missing values
    for col in df.columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            if df[col].dtype in ["float64", "int64"]:
                df[col].fillna(df[col].median(), inplace=True)
                issues.append(f"Filled {null_count} nulls in '{col}' with median")
            else:
                df[col].fillna("Unknown", inplace=True)
                issues.append(f"Filled {null_count} nulls in '{col}' with 'Unknown'")

    # Infer better types
    for col in df.select_dtypes(include="object").columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            pass

    return {
        **loader_output,
        "dataframe": df,
        "cleaning_issues": issues,
        "cleaned": True
    }