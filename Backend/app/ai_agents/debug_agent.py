"""Diagnoses issues in analysis pipeline."""
def run(error: Exception, stage: str) -> dict:
    return {
        "stage": stage,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "suggestion": _suggest(error, stage)
    }

def _suggest(error: Exception, stage: str) -> str:
    msg = str(error).lower()
    if "memory" in msg:
        return "Dataset may be too large. Consider sampling."
    if "column" in msg or "keyerror" in msg:
        return "Column name mismatch. Verify column names in dataset."
    if "gemini" in msg or "api" in msg:
        return "LLM service error. Check GEMINI_API_KEY in .env."
    if "file" in msg:
        return "File not found. Re-upload the dataset."
    return f"Unexpected error in {stage}. Check server logs."