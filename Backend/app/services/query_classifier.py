from enum import Enum

class QueryType(str, Enum):
    SIMPLE  = "simple"
    MEDIUM  = "medium"
    COMPLEX = "complex"

SIMPLE_KEYWORDS = [
    "how many", "count", "total", "sum", "average", "mean", "max", "min",
    "maximum", "minimum", "top", "bottom", "first", "last", "list", "show",
    "rows", "columns", "shape", "null", "missing", "unique", "distinct"
]

COMPLEX_KEYWORDS = [
    "why", "explain", "recommend", "suggest", "forecast", "predict",
    "compare", "analyze", "analyse", "insight", "pattern", "trend",
    "correlation", "cause", "reason", "should", "could", "would",
    "strategy", "improve", "opportunity", "risk", "anomaly"
]

def classify_query(query: str) -> QueryType:
    q     = query.lower().strip()
    words = q.split()

    if any(kw in q for kw in COMPLEX_KEYWORDS):
        return QueryType.COMPLEX

    if any(kw in q for kw in SIMPLE_KEYWORDS) and len(words) <= 15:
        return QueryType.SIMPLE

    return QueryType.MEDIUM