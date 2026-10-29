"""REST API so the copilot can sit behind the website form, a Gmail hook or a WhatsApp webhook.

  uvicorn api:app --reload        then POST /triage {"text": "..."}   (docs at /docs)
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field

from copilot import pipeline

app = FastAPI(title="Cynbit Inquiry Copilot", version="0.1.0")


class Inquiry(BaseModel):
    text: str = Field(..., min_length=3, max_length=8000)
    channel: str = "contact_form"          # contact_form | email | whatsapp
    use_llm: bool | None = None            # None = Claude if a key is configured


@app.post("/triage")
def triage(q: Inquiry) -> dict:
    return dict(pipeline.run(q.text, use_llm=q.use_llm), channel=q.channel)


@app.get("/health")
def health() -> dict:
    return {"ok": True}
