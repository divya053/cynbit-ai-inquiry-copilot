"""The one structure every analyzer (Claude or offline rules) must return."""

INTENTS = ["client_project", "internship", "job_application", "partnership", "support", "spam"]
SERVICE_LINES = ["ai_automation", "software_dev", "cloud", "digital_marketing",
                 "product_revio", "product_tenantease", "product_studio"]

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string", "enum": INTENTS},
        "service_lines": {"type": "array", "items": {"type": "string", "enum": SERVICE_LINES}},
        "summary": {"type": "string"},
        "company": {"type": "string"},
        "industry": {"type": "string"},
        "requirements": {"type": "array", "items": {"type": "string"}},
        "budget_text": {"type": "string"},
        "budget_inr": {"type": "integer"},
        "timeline": {"type": "string"},
        "urgency": {"type": "string", "enum": ["low", "medium", "high"]},
        "decision_maker": {"type": "boolean"},
        "language": {"type": "string", "enum": ["english", "hindi", "hinglish"]},
        "missing_info": {"type": "array", "items": {"type": "string"}},
        "discovery_questions": {"type": "array", "items": {"type": "string"}},
        "reply_draft": {"type": "string"},
    },
    "required": ["intent", "service_lines", "summary", "company", "industry", "requirements", "budget_text",
                 "budget_inr", "timeline", "urgency", "decision_maker", "language", "missing_info",
                 "discovery_questions", "reply_draft"],
    "additionalProperties": False,
}

LABELS = {
    "client_project": "New client project", "internship": "Internship / BitElevate", "job_application": "Job application",
    "partnership": "Partnership / vendor", "support": "Existing client support", "spam": "Spam / irrelevant",
    "ai_automation": "AI automation", "software_dev": "Software development", "cloud": "Cloud & migration",
    "digital_marketing": "Digital marketing", "product_revio": "Revio", "product_tenantease": "TenantEase",
    "product_studio": "Cynbit Studio",
}
