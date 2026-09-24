import json
import traceback
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
import markdown

from graph import app as research_graph

app = FastAPI()

INDEX_PATH = Path(__file__).parent / "static" / "index.html"


class ResearchRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


def initial_state(question: str) -> dict:
    return {
        "question": question,
        "sub_questions": [],
        "findings": [],
        "critique": "",
        "report": "",
        "report_critique": "",
        "revision_count": 0,
    }


def to_html(text: str) -> str:
    return markdown.markdown(text or "", extensions=["tables", "fenced_code"])


def build_result(state: dict) -> dict:
    return {
        "report_md": state["report"],
        "report_html": to_html(state["report"]),
        "critique_html": to_html(state["report_critique"]),
        "findings_html": [to_html(f) for f in state["findings"]],
        "revision_count": state["revision_count"],
    }


@app.get("/")
async def home():
    return FileResponse(INDEX_PATH)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/research")
async def research(req: ResearchRequest):
    final_state = await research_graph.ainvoke(initial_state(req.question))
    return build_result(final_state)


@app.post("/research/stream")
async def research_stream(req: ResearchRequest):
    """Runs the graph and streams one JSON event per line as each node finishes."""

    async def events():
        state = initial_state(req.question)
        try:
            async for chunk in research_graph.astream(state, stream_mode="updates"):
                for node, update in chunk.items():
                    update = update or {}
                    for key, value in update.items():
                        if key == "findings":
                            state["findings"] = state["findings"] + value
                        else:
                            state[key] = value
                    event = {"type": "node", "node": node}
                    if node == "planner":
                        event["sub_questions"] = state["sub_questions"]
                    elif node == "report_critic":
                        event["revision_count"] = state["revision_count"]
                        event["passed"] = "NO ISSUES FOUND" in state["report_critique"]
                    yield json.dumps(event) + "\n"
            yield json.dumps({"type": "done", **build_result(state)}) + "\n"
        except Exception as e:
            traceback.print_exc()
            yield json.dumps({"type": "error", "message": f"{type(e).__name__}: {e}"}) + "\n"

    return StreamingResponse(events(), media_type="application/x-ndjson")
