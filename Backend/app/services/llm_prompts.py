def prompt_query(query: str, schema: str, sample: str, stats: str) -> str:
    return f"""You are a precise data analyst. Answer ONLY using the dataset provided.
DO NOT hallucinate. DO NOT give generic answers. If unsure, say "Not found in dataset."

Schema: {schema}

Statistics:
{stats}

Sample rows:
{sample}

Question: {query}

Give a specific, concise answer based strictly on the data above."""

def prompt_insights(columns: list, stats: str, sample: str) -> str:
    return f"""You are a senior data analyst. Analyze ONLY this dataset.
DO NOT make up data. Generate insights from actual values.

Columns: {columns}
Statistics:
{stats}

Sample:
{sample}

Return JSON:
{{
  "summary": "2-3 sentence factual summary",
  "insights": ["insight 1", "insight 2", "insight 3", "insight 4", "insight 5"],
  "recommendations": ["action 1", "action 2", "action 3"]
}}"""

def prompt_kpis(columns: list, stats: str, sample: str) -> str:
    return f"""Extract KPIs from this dataset ONLY. Use real numbers.

Columns: {columns}
Statistics:
{stats}
Sample:
{sample}

Return JSON array:
[
  {{"label": "Total Records", "value": 150, "unit": "rows", "trend": "stable"}},
  {{"label": "Average Sales", "value": 4500.50, "unit": "USD", "trend": "up"}}
]
Generate 4-6 KPIs. Use ONLY real numbers from the statistics above."""

def prompt_visualization(columns: list, dtypes: dict, stats: str) -> str:
    return f"""Design charts for this exact dataset. Use ONLY these columns: {columns}

Data types: {dtypes}
Statistics: {stats}

Return JSON array (max 4 charts):
[
  {{
    "id": "chart_1",
    "title": "Descriptive title",
    "type": "bar",
    "x_column": "exact_column_name",
    "y_column": "exact_column_name"
  }}
]
Allowed types: bar, line, pie, scatter, histogram
CRITICAL: x_column and y_column must be from {columns}"""

def prompt_questions(columns: list, summary: str, insights: list) -> str:
    return f"""Generate 5 insightful questions a user might ask about this dataset.

Columns: {columns}
Summary: {summary}
Key insights: {insights[:3]}

Return JSON array of 5 question strings:
["question 1", "question 2", "question 3", "question 4", "question 5"]
Make questions specific to the actual column names above."""