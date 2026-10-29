"""Claude analyzer: one structured-output call that reads the inquiry plus the retrieved Cynbit context.

- Structured outputs (output_config.format = JSON schema) guarantee parseable JSON that matches ANALYSIS_SCHEMA.
- Retrieved services / case studies go in the prompt, and the prompt forbids citing anything else,
  so the reply never invents projects or prices (grounding).
- The stable instructions sit in the system prompt with cache_control, so repeated calls reuse the cache.
- Server-side refusal fallback is enabled; any API error falls back to the offline analyzer in pipeline.py.
"""
import json
import os

from .schema import ANALYSIS_SCHEMA

MODEL = os.environ.get("CYNBIT_MODEL", "claude-opus-5-5")
EFFORT = os.environ.get("CYNBIT_EFFORT", "low")          # triage is a short, well-specified task

SYSTEM = """You are the inquiry desk analyst for Cynbit Technologies, an AI automation and software company in Jaipur.
Every message that arrives through the website contact form, email or WhatsApp is passed to you.

Read the inquiry and fill every field of the JSON schema:
- intent: client_project (someone who may pay Cynbit for work or a product), internship (BitElevate / training),
  job_application, partnership (agencies, vendors, resellers), support (an existing client with a problem), spam.
- service_lines: every Cynbit offering the sender needs. Use the product ids when the need matches Revio
  (reviews / reputation), TenantEase (rent / tenants / PG) or Cynbit Studio (placement / student careers).
- budget_inr: the budget in rupees as an integer (convert lakh, crore, k, and USD at 84), 0 if not stated.
  budget_text: the words they used, "" if none.
- urgency: high if they need it within about 3 weeks or say urgent/ASAP, medium if within 3 months, else low.
- decision_maker: true only if they say they are a founder, owner, director, CXO or head of the function.
- language: the language the sender wrote in (Hinglish = Hindi in Latin script mixed with English).
- missing_info: what Cynbit still needs before a proposal (budget, timeline, scope, users, integrations, company).
- discovery_questions: at most 4 short questions that fill those gaps, in priority order.
- reply_draft: a short, warm reply from "Team Cynbit Technologies" in the sender's language, under 150 words.
  For client projects, mention at most one relevant case study or product from CONTEXT, invite them to a discovery
  call, and ask the discovery questions. Never quote prices or delivery dates and never mention a client, product or
  result that is not in CONTEXT. Internship -> point to cynbit.in/bitelevate. Job -> cynbit.in/careers.
  Spam -> empty string.
Use "" or [] when something is not stated. Do not guess company names."""


def available(api_key: str | None = None) -> bool:
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return bool(api_key or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))


def analyze(text: str, context: list[dict], api_key: str | None = None) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
    ctx = "\n".join(f"- [{d['type']}] {d['title']}: {d['text']}" for d in context)
    request = dict(
        model=MODEL,
        max_tokens=4000,
        system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
        output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": ANALYSIS_SCHEMA}},
        messages=[{"role": "user", "content": f"CONTEXT (Cynbit offerings relevant to this inquiry):\n{ctx}\n\n"
                                              f"INQUIRY:\n<<<\n{text}\n>>>"}],
    )
    try:   # server-side fallback: if the model declines, the API retries on a fallback model in the same call
        response = client.beta.messages.create(betas=["server-side-fallback-2026-07-01"], fallbacks="default", **request)
    except anthropic.BadRequestError:
        response = client.messages.create(**request)
    if response.stop_reason == "refusal":
        raise RuntimeError("model declined the request")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("response was cut off")
    text_out = next(b.text for b in response.content if b.type == "text")
    data = json.loads(text_out)
    data["_usage"] = {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens,
                      "model": response.model}
    return data
