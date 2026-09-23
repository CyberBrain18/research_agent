from langgraph.graph import StateGraph, START, END

from state import ResearchState
from nodes import (
    planner_node,
    researcher_node,
    critic_node,
    writer_node,
    report_critic_node,
    should_revise,
    fan_out_to_researchers
)
from tools import save_report_as_html
from langgraph.types import Send

graph = StateGraph(ResearchState)

graph.add_node("planner", planner_node)
graph.add_node("researcher", researcher_node)
graph.add_node("critic", critic_node)
graph.add_node("writer", writer_node)
graph.add_node("report_critic", report_critic_node)

graph.add_edge(START, "planner")
graph.add_conditional_edges("planner", fan_out_to_researchers, ["researcher"])
graph.add_edge("researcher", "critic")
graph.add_edge("critic", "writer")
graph.add_edge("writer", "report_critic")

graph.add_conditional_edges(
    "report_critic",
    should_revise,
    {"revise": "writer", "end": END}
)

app = graph.compile()

if __name__ == "__main__":
    initial_state: ResearchState = {
        "question": "Should a seed-stage startup use AWS, GCP, or Azure for its infrastructure?",
        "sub_questions": [],
        "findings": [],
        "critique": "",
        "report": "",
        "report_critique": "",
        "revision_count": 0
    }

    final_state = app.invoke(initial_state)
    save_report_as_html(final_state)
