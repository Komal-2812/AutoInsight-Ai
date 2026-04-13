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

    # ✅ FIX 1: Rename ALL nodes to avoid state conflict
    g.add_node("load_node", node_load)
    g.add_node("clean_node", node_clean)
    g.add_node("eda_node", node_eda)
    g.add_node("insights_node", node_insights)
    g.add_node("charts_node", node_charts)
    g.add_node("kpis_node", node_kpis)
    g.add_node("finalize_node", node_finalize)

    # Entry
    g.set_entry_point("load_node")

    # Conditional edge
    g.add_conditional_edges(
        "load_node",
        _should_continue,
        {
            "next": "clean_node",
            END: END
        }
    )

    # ✅ FIX 2: Correct all edges (match node names)
    g.add_edge("clean_node", "eda_node")
    g.add_edge("eda_node", "insights_node")
    g.add_edge("insights_node", "charts_node")
    g.add_edge("charts_node", "kpis_node")
    g.add_edge("kpis_node", "finalize_node")
    g.add_edge("finalize_node", END)

    return g.compile()


# ── QUERY GRAPH ───────────────────────────────────────────────────────────────
def build_query_graph():
    g = StateGraph(GraphState)

    # ✅ Also fix here for consistency
    g.add_node("load_node", node_load)
    g.add_node("query_node", node_query)

    g.set_entry_point("load_node")

    g.add_conditional_edges(
        "load_node",
        _should_continue,
        {
            "next": "query_node",
            END: END
        }
    )

    g.add_edge("query_node", END)

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
        "eda": {},            # ✅ SAFE (node is eda_node)
        "insights": [],       # ✅ SAFE (node is insights_node)
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