from typing import TypedDict, List, Annotated
import operator

class ResearchState(TypedDict):
    question: str
    sub_questions: List[str]
    findings: Annotated[List[str], operator.add]
    critique: str
    report: str
    report_critique: str
    revision_count: int