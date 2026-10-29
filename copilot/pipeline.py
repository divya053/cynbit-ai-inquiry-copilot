"""Inquiry -> retrieve context -> analyze (Claude or rules) -> score -> route -> reply draft.

The lead score and routing are plain code, not LLM output. That keeps them explainable ("why is this 82?"),
cheap to change, and testable. The LLM only does what rules do badly: understanding free text.
"""
import time

from . import llm, offline
from .retrieval import KnowledgeBase

_KB = None

ROUTES = {
    "client_project": ("Sales / solutions team", "Reply within 4 working hours"),
    "support": ("Delivery / project manager", "Reply within 2 working hours"),
    "internship": ("BitElevate admissions", "Auto-reply, no human needed"),
    "job_application": ("HR / talent", "Auto-reply, add to the careers pipeline"),
    "partnership": ("Founders' office", "Reply within 2 working days"),
    "spam": ("Archive", "No reply"),
}
SERVICE_OWNER = {
    "ai_automation": "AI solutions", "software_dev": "Engineering", "cloud": "Cloud & DevOps",
    "digital_marketing": "Growth & marketing", "product_revio": "Revio product", "product_tenantease": "TenantEase product",
    "product_studio": "Cynbit Studio product",
}


def kb() -> KnowledgeBase:
    global _KB
    if _KB is None:
        _KB = KnowledgeBase()
    return _KB


def lead_score(a: dict) -> tuple[int, list[str]]:
    """0-100 with the reasons, so a salesperson can see why."""
    if a["intent"] != "client_project":
        return 0, [f"not a sales lead ({a['intent']})"]
    score, why = 30, ["new client project: +30"]
    b = a.get("budget_inr") or 0
    if b >= 500000:
        score, why = score + 25, why + ["budget Rs 5 lakh or more: +25"]
    elif b >= 100000:
        score, why = score + 18, why + ["budget Rs 1-5 lakh: +18"]
    elif b > 0:
        score, why = score + 8, why + ["small budget stated: +8"]
    if a.get("urgency") == "high":
        score, why = score + 12, why + ["needs it soon: +12"]
    elif a.get("urgency") == "medium":
        score, why = score + 8, why + ["timeline within ~3 months: +8"]
    if a.get("decision_maker"):
        score, why = score + 10, why + ["writes as a decision maker: +10"]
    if a.get("company"):
        score, why = score + 5, why + ["company named: +5"]
    n = len(a.get("requirements") or [])
    if n:
        score, why = score + min(10, 4 * n), why + [f"{n} concrete requirement(s): +{min(10, 4 * n)}"]
    if any(s in a.get("service_lines", []) for s in ("ai_automation", "product_revio", "product_tenantease", "product_studio")):
        score, why = score + 8, why + ["fits Cynbit's AI / product focus: +8"]
    return min(score, 100), why


def run(text: str, use_llm: bool | None = None, api_key: str | None = None) -> dict:
    t0 = time.perf_counter()
    context = kb().search(text, k=5)
    engine, error = "offline rules", None
    if use_llm is None:
        use_llm = llm.available(api_key)
    if use_llm:
        try:
            analysis = llm.analyze(text, context, api_key)
            engine = f"Claude ({analysis.get('_usage', {}).get('model', llm.MODEL)})"
        except Exception as ex:                                  # never lose an inquiry because the API failed
            analysis, error = offline.analyze(text, kb()), f"LLM failed, used rules instead: {ex}"
    else:
        analysis = offline.analyze(text, kb())
    score, reasons = lead_score(analysis)
    team, sla = ROUTES[analysis["intent"]]
    if analysis["intent"] == "client_project" and analysis["service_lines"]:
        team += " + " + ", ".join(SERVICE_OWNER[s] for s in analysis["service_lines"])
    priority = "P1 - hot" if score >= 70 else "P2 - warm" if score >= 45 else "P3 - nurture" if score > 0 else "-"
    return dict(analysis=analysis, lead_score=score, score_reasons=reasons, priority=priority, route_to=team, sla=sla,
                context=[{k: d[k] for k in ("id", "type", "title", "score")} for d in context],
                engine=engine, error=error, latency_ms=int((time.perf_counter() - t0) * 1000))
