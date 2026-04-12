import json
import time
from functools import lru_cache
from app.config import settings


# ── Provider implementations ──────────────────────────────────────────────────

def _call_groq(prompt: str, model: str) -> str:
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2048,
    )

    return response.choices[0].message.content.strip()


def _call_openai(prompt: str, model: str) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"OpenAI error: {e}")


def _call_anthropic(prompt: str, model: str) -> str:
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        response = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()

    except Exception as e:
        raise RuntimeError(f"Anthropic error: {e}")


def _call_local(prompt: str, model: str) -> str:
    import requests

    res = requests.post(
        settings.LOCAL_LLM_URL,
        json={"model": model, "prompt": prompt}
    )

    return res.json().get("response", "").strip()


# ── Provider registry ─────────────────────────────────────────────────────────

PROVIDERS = {
    "groq": _call_groq,
    "openai": _call_openai,
    "anthropic": _call_anthropic,
    "local": _call_local,
}


# ── Core LLM Call (with retry + cache) ─────────────────────────────────────────

@lru_cache(maxsize=100)
def call_llm(
    prompt: str,
    model: str = None,
    provider: str = None,
    retries: int = 3
) -> str:
    provider = (provider or settings.LLM_PROVIDER).lower()
    model = model or settings.LLM_MODEL

    fn = PROVIDERS.get(provider)

    if not fn:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    for attempt in range(retries):
        try:
            return fn(prompt, model)

        except Exception as e:
            err = str(e).lower()

            # Rate limit handling
            if "429" in err or "rate" in err:
                wait = 10 * (attempt + 1)
                print(f"[LLM] Rate limited. Waiting {wait}s...")
                time.sleep(wait)

            elif attempt < retries - 1:
                wait = 2 ** attempt
                print(f"[LLM] Error: {e} | Retry in {wait}s")
                time.sleep(wait)

            else:
                print(f"[LLM] Failed after {retries} attempts: {e}")
                return "LLM unavailable. Try simpler query."

    return "LLM unavailable."


# ── JSON Response Handler (ROBUST) ────────────────────────────────────────────

def call_llm_json(prompt: str) -> dict:
    """
    Ensures structured JSON output from LLM.
    """
    full_prompt = (
        prompt
        + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown. No explanation."
    )

    text = call_llm(full_prompt).strip()

    # Remove markdown fences
    if text.startswith("```"):
        lines = [
            l for l in text.split("\n")
            if not l.strip().startswith("```")
        ]
        text = "\n".join(lines).strip()

    # Try parsing JSON
    try:
        return json.loads(text)

    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON from LLM",
            "raw": text[:500]
        }


# ── BACKWARD COMPATIBILITY (VERY IMPORTANT) ───────────────────────────────────

def call_gemini_json(prompt: str) -> dict:
    """
    Temporary wrapper so old agents don't break.
    REMOVE later after full migration.
    """
    return call_llm_json(prompt)


# ── Prompt Templates (UNCHANGED) ──────────────────────────────────────────────

def prompt_insights(summary_stats: str, columns: list, sample_rows: str) -> str:
    return f"""You are a senior data analyst. Analyze this dataset.

Columns: {columns}
Summary statistics:
{summary_stats}

Sample rows:
{sample_rows}

Return JSON:
{{
  "summary": "2-3 sentence summary",
  "insights": ["insight 1", "insight 2", "insight 3", "insight 4"],
  "recommendations": ["action 1", "action 2", "action 3"]
}}"""


def prompt_kpis(summary_stats: str, columns: list) -> str:
    return f"""Extract KPIs from dataset.

Columns: {columns}
Stats: {summary_stats}

Return JSON array:
[
  {{"label": "Metric", "value": 100, "unit": "units", "trend": "up"}}
]

Generate 4-6 KPIs using real values."""


def prompt_chat(query: str, dataset_context: str, schema: str) -> str:
    return f"""You are a data analyst.

Schema: {schema}
Context:
{dataset_context}

Question: {query}

Return JSON:
{{
  "answer": "clear answer",
  "generate_chart": false,
  "chart_description": "",
  "generate_table": false,
  "table_description": "",
  "kpis": []
}}"""


def prompt_visualization(columns: list, dtypes: dict, summary: str) -> str:
    return f"""Suggest charts.

Columns: {columns}
Types: {dtypes}
Summary: {summary}

Return JSON array:
[
  {{
    "id": "chart_1",
    "title": "Title",
    "type": "bar",
    "x_column": "column",
    "y_column": "column",
    "description": "reason"
  }}
]

Allowed types: bar, line, pie, scatter, histogram"""