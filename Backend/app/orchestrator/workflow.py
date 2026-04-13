from langgraph.graph import StateGraph, END
from app.orchestrator.graph_state import GraphState

# ── Node imports ──────────────────────────────────────────────────────────────
from app.orchestrator.nodes import (
    node_load,
    node_clean,
    node_eda,
    node_insights,
    node_charts,
    node_kpis,
    node_finalize,
    node_query,
)

# ── Condition helper ──────────────────────────────────────────────────────────

def _should_continue(state: GraphState) -> str:
    return END if state.get("status") == "failed" else "next"


# ── FULL ANALYSIS GRAPH ───────────────────────────────────────────────────────

def build_analysis_graph():
    g = StateGraph(GraphState)

    # Nodes
    g.add_node("load", node_load)
    g.add_node("clean", node_clean)
    g.add_node("eda_node", node_eda)   
    g.add_node("insights", node_insights)
    g.add_node("charts", node_charts)
    g.add_node("kpis", node_kpis)
    g.add_node("finalize", node_finalize)

    # Entry
    g.set_entry_point("load")

    # Conditional edge ONLY (important fix)
    g.add_conditional_edges(
        "load",
        _should_continue,
        {
            "next": "clean",
            END: END
        }
    )

    # Pipeline
    g.add_edge("clean", "eda")
    g.add_edge("eda_node", "insights")
    g.add_edge("insights", "charts")
    g.add_edge("charts", "kpis")
    g.add_edge("kpis", "finalize")
    g.add_edge("finalize", END)

    return g.compile()


# ── QUERY GRAPH (FIXED) ───────────────────────────────────────────────────────

def build_query_graph():
    g = StateGraph(GraphState)

    g.add_node("load", node_load)
    g.add_node("query", node_query)

    g.set_entry_point("load")

    # Correct conditional routing
    g.add_conditional_edges(
        "load",
        _should_continue,
        {
            "next": "query",
            END: END
        }
    )

    g.add_edge("query", END)

    return g.compile()


# ── SINGLETONS ────────────────────────────────────────────────────────────────

analysis_graph = build_analysis_graph()
query_graph = build_query_graph()


# ── INITIAL STATE ─────────────────────────────────────────────────────────────

def _initial_state(dataset_id: str, file_path: str, query: str = None) -> GraphState:
    return {
        "dataset_id": dataset_id,
        "file_path": file_path,
        "user_query": query,

        "dataframe": None,
        "row_count": 0,
        "column_count": 0,
        "columns": [],
        "dtypes": {},

        "cleaning_log": [],
        "eda": {},
        "insights": [],
        "summary": "",

        "kpis": [],
        "charts": [],
        "tables": [],

        "query_result": "",
        "query_engine": "",

        "status": "running",
        "error": None,
        "suggested_questions": [],
    }


# ── RUNNERS ───────────────────────────────────────────────────────────────────

def run_analysis_graph(dataset_id: str, file_path: str) -> dict:
    state = analysis_graph.invoke(_initial_state(dataset_id, file_path))
    return _serialize(state)


def run_query_graph(dataset_id: str, file_path: str, query: str) -> dict:
    state = query_graph.invoke(_initial_state(dataset_id, file_path, query))

    return {
        "query_result": state.get("query_result", ""),
        "query_engine": state.get("query_engine", ""),
        "status": state.get("status", "completed"),
    }


# ── SERIALIZER ────────────────────────────────────────────────────────────────

def _serialize(state: dict) -> dict:
    return {k: v for k, v in state.items() if k != "dataframe"}