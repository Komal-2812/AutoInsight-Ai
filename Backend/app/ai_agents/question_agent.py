"""Suggests follow-up questions based on dataset analysis."""
from app.services.llm_service import call_gemini_json

def run(columns: list, insights: list, summary: str) -> list:
    prompt = f"""Based on this dataset analysis, suggest 5 insightful questions a user might ask.

Summary: {summary}
Key columns: {columns[:10]}
Insights: {insights[:3]}

Return a JSON array of question strings: ["question 1", "question 2", ...]"""
    try:
        questions = call_gemini_json(prompt)
        return questions if isinstance(questions, list) else []
    except Exception:
        return [
            "What are the top performing categories?",
            "Show me the trend over time",
            "Which values are outliers?",
            "What is the correlation between key metrics?",
            "Summarize the main findings"
        ]