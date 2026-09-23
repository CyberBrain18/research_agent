import os
from dotenv import load_dotenv
from tavily import TavilyClient
import markdown
import webbrowser
from datetime import datetime

from state import ResearchState

load_dotenv()

tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def save_report_as_html(state: ResearchState, filename="report.html"):
    report_html = markdown.markdown(state["report"], extensions=["tables"])
    critique_html = markdown.markdown(state["report_critique"], extensions=["tables"])

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Research Report</title>
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        max-width: 800px;
        margin: 40px auto;
        padding: 0 20px;
        line-height: 1.6;
        color: #1a1a1a;
    }}
    h1 {{ border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
    .meta {{ color: #666; font-size: 0.9em; margin-bottom: 30px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
    th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
    th {{ background: #f5f5f5; }}
    .critique {{ background: #fff8e1; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
    .critique table {{ background: white; }}
</style>
</head>
<body>
<h1>Research Report</h1>
<div class="meta">
    Question: {state['question']}<br>
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Revisions: {state['revision_count']}
</div>
{report_html}

<h2>Final Quality Check</h2>
<div class="critique">
{critique_html}
</div>
</body>
</html>"""

    with open(filename, "w") as f:
        f.write(html)

    webbrowser.open(f"file://{os.path.abspath(filename)}")

def web_search(query: str) -> str:
    """Searches the web and returns a summarised set of results"""
    results = tavily.search(query=query, search_depth="basic", max_results=3)

    formatted = []
    for r in results["results"]:
        formatted.append(f"Source: {r["title"]} ({r['url']})\n{r['content']}")

    return "\n\n".join(formatted)
