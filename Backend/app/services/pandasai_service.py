import pandas as pd
from app.config import settings

def run_pandasai_query(query: str, df: pd.DataFrame) -> str:
    try:
        from pandasai import Agent
        from pandasai.llm.langchain import LangchainLLM
        from langchain_groq import ChatGroq

        groq_llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.LLM_MODEL,
            temperature=0.1,
        )
        llm   = LangchainLLM(groq_llm)
        agent = Agent([df], config={"llm": llm, "verbose": False, "enable_cache": False})
        result = agent.chat(query)
        return str(result) if result is not None else "No result from PandasAI"

    except ImportError:
        return _groq_fallback(query, df)
    except Exception as e:
        print(f"[PandasAI] Failed: {e} — falling back to Groq")
        return _groq_fallback(query, df)

def _groq_fallback(query: str, df: pd.DataFrame) -> str:
    from app.services.llm_service import call_llm
    from app.services.llm_prompts import prompt_query

    sample = df.head(15).to_string(index=False)
    schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
    stats  = df.select_dtypes(include="number").describe().round(2).to_string()

    return call_llm(prompt_query(query, str(schema), sample, stats))