"""Rule-based analyzer: the no-API-key baseline and the fallback when the LLM call fails.

It is deliberately simple (regex + keyword lists + BM25). It gives the evaluation a baseline to beat
and keeps the inbox working if the LLM is down.
"""
import re

from .schema import LABELS

INTENT_RULES = [  # checked in order, first match wins
    ("spam", r"backlink|guest post|crypto|bitcoin|lottery|casino|seo package for you|rank your website|"
             r"we (?:can|will) increase your|loan offer|dear sir/madam, we are a leading"),
    ("support", r"existing (?:client|customer|project)|our (?:current )?project with you|not working|is down|bug in|"
                r"issue (?:with|in) (?:the|our)|invoice|ticket|login (?:issue|problem)|already (?:working|signed) with"),
    ("internship", r"internship|\bintern\b|bitelevate|summer training|training program|certificate course|"
                   r"college credit|noc\b|\bfresher\b.*(?:learn|training)"),
    ("job_application", r"\bjob\b|resume|\bcv\b|vacancy|opening|hiring|position|apply(?:ing)? for|years? of experience as|"
                        r"looking for (?:a )?(?:role|job|opportunity)|naukri"),
    ("partnership", r"partner(?:ship)?|collaborat|white[- ]label|reseller|refer(?:ral)? (?:clients|projects)|"
                    r"outsourc|subcontract|we are an? (?:agency|vendor)|our services to you"),
]
SERVICE_RULES = {
    "ai_automation": r"\bai\b|chatbot|chat bot|\bbot\b|agent|automat|llm|gpt|openai|machine learning|\bml\b|voice|"
                     r"whatsapp bot|ocr|document processing|data entry|rag|predict|recommend",
    "software_dev": r"website|web ?app|mobile app|\bapp\b|android|ios|portal|dashboard|e-?commerce|online store|"
                    r"marketplace|\bmvp\b|platform|software|\bapi\b|booking system|crm system|erp",
    "cloud": r"cloud|aws|azure|server|hosting|devops|docker|kubernetes|migrat|legacy|downtime|backup",
    "digital_marketing": r"\bseo\b|google ads|meta ads|facebook ads|instagram|marketing|leads? generation|more leads|"
                        r"ranking|landing page|campaign|social media|funnel",
    "product_revio": r"review|reputation|rating|google my business|gmb",
    "product_tenantease": r"tenant|rent|\bpg\b|paying guest|landlord|propert|co-?living|flats",
    "product_studio": r"placement|campus|students? (?:skill|career)|mock interview|resume builder|tpo|university",
}
INDUSTRIES = {
    "healthcare": r"hospital|clinic|doctor|patient|health|pharma|diagnos|dental",
    "education": r"school|college|universit|coaching|institute|students|edtech|lms",
    "retail / e-commerce": r"shop|store|retail|e-?commerce|fashion|clothing|boutique|jewel",
    "real estate": r"real estate|propert|builder|tenant|rent|\bpg\b|hostel",
    "hospitality": r"hotel|restaurant|cafe|resort|travel|tour",
    "manufacturing": r"manufactur|factory|textile|export|industr|inventory",
    "finance": r"fintech|bank|loan|insurance|payment|ca firm|accounting",
    "logistics": r"logistic|transport|fleet|courier|delivery",
}
HINGLISH = r"\b(?:hai|hain|chahiye|karna|karni|krna|hum|humein|mujhe|kya|ke liye|banwana|bana do|bataiye|kitna|apka|aapka)\b"
DECISION = r"\b(?:founder|co-?founder|owner|ceo|cto|director|\bmd\b|proprietor|partner at|head of)\b"


def parse_budget(text: str) -> tuple[str, int]:
    t = text.lower().replace(",", "")
    t = re.sub(r"(\d+)\s*(?:-|to)\s*\d+(\s*(?:lakhs?|lacs?|k\b|cr|crore|hazaa?r|thousand))", r"\1\2", t)  # ranges: lower bound
    t = re.sub(r"(\d)\s*(?:hazaa?r|thousand)", r"\1k", t)
    m = re.search(r"(?:₹|\brs\.?|\binr)\s*(\d+(?:\.\d+)?)\s*(lakhs?|lacs?|l\b|k\b|cr|crore)?|"
                  r"(\d+(?:\.\d+)?)\s*(lakhs?|lacs?|k\b|cr|crore)\b|\$\s*(\d+(?:\.\d+)?)\s*(k\b)?", t)
    if not m:
        return "", 0
    if m.group(5):                                            # dollars
        usd = float(m.group(5)) * (1000 if m.group(6) else 1)
        return m.group(0).strip(), int(usd * 84)
    num = float(m.group(1) or m.group(3))
    unit = (m.group(2) or m.group(4) or "").strip()
    mult = 100000 if unit.startswith(("lakh", "lac", "l")) else 10000000 if unit.startswith("cr") else 1000 if unit == "k" else 1
    return m.group(0).strip(), int(num * mult)


def parse_timeline(text: str) -> tuple[str, str]:
    t = text.lower()
    if re.search(r"asap|urgent|immediately|right away|this week|jaldi|turant", t):
        return re.search(r"asap|urgent\w*|immediately|right away|this week|jaldi|turant", t).group(0), "high"
    m = (re.search(r"(?:in|within|next|timeline(?: of)?)\s+(\d+|a|one|two|three)\s*(day|week|month)s?", t)
         or re.search(r"(\d+)\s*(din|hafte|mahine|mahina)", t))
    if m:
        n = {"a": 1, "one": 1, "two": 2, "three": 3}.get(m.group(1), None) or int(m.group(1))
        unit = {"din": "day", "hafte": "week", "mahine": "month", "mahina": "month"}.get(m.group(2), m.group(2))
        days = n * {"day": 1, "week": 7, "month": 30}[unit]
        return m.group(0), "high" if days <= 21 else "medium" if days <= 90 else "low"
    m = re.search(r"(?:by|before)\s+(?:end of\s+)?(january|february|march|april|may|june|july|august|september|october|"
                  r"november|december|diwali|holi|next month|q[1-4])", t)
    if m:
        return m.group(0), "medium"
    return "", "low"


def company_of(text: str) -> str:
    m = re.search(r"(?:from|at|of|we are|i am .{0,30}? (?:of|at))\s+([A-Z][\w&.-]*(?:\s+(?:[A-Z][\w&.-]*|&))"
                  r"{0,3}\s*(?:Pvt\.? Ltd\.?|Ltd\.?|LLP|Hospital|Clinic|School|Group|Foods|Labs|Studio|Store|Industries)?)", text)
    return m.group(1).strip(" .,") if m else ""


def analyze(text: str, kb) -> dict:
    low = text.lower()
    intent = next((name for name, rx in INTENT_RULES if re.search(rx, low)), "client_project")
    services = [s for s, rx in SERVICE_RULES.items() if re.search(rx, low)]
    hits = kb.search(text, k=3)
    if intent == "client_project" and not services and hits and hits[0]["service_line"] in SERVICE_RULES:
        services = [hits[0]["service_line"]]
    budget_text, budget = parse_budget(text)
    timeline, urgency = parse_timeline(text)
    company = company_of(text)
    industry = next((name for name, rx in INDUSTRIES.items() if re.search(rx, low)), "")
    language = "hindi" if re.search(r"[ऀ-ॿ]", text) else "hinglish" if re.search(HINGLISH, low) else "english"
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.split()) >= 4]
    reqs = [s for s in sentences if re.search(r"need|want|looking|require|should|must|chahiye|build|create|automat|integrat", s, re.I)][:5]

    missing = []
    if intent == "client_project":
        if not budget:
            missing.append("budget range")
        if not timeline:
            missing.append("timeline / launch date")
        if not company:
            missing.append("company name and website")
        if len(text.split()) < 40:
            missing.append("detailed scope (users, features, integrations)")
    questions = {
        "budget range": "What budget range have you set aside for this project?",
        "timeline / launch date": "When would you like this to be live, and is there a fixed deadline?",
        "company name and website": "Could you share your company name and current website, if any?",
        "detailed scope (users, features, integrations)": "Who will use it, and which tools or systems should it connect to?",
    }
    result = dict(intent=intent, service_lines=services if intent in ("client_project", "support") else services[:1],
                  summary=(sentences[0] if sentences else text.strip())[:160], company=company, industry=industry,
                  requirements=reqs, budget_text=budget_text, budget_inr=budget, timeline=timeline, urgency=urgency,
                  decision_maker=bool(re.search(DECISION, low)), language=language, missing_info=missing,
                  discovery_questions=[questions[m] for m in missing][:4])
    result["reply_draft"] = template_reply(result, hits, kb.company)
    return result


def template_reply(r: dict, hits: list[dict], company: dict) -> str:
    hello = "Hi,\n\n"
    sign = "\n\nBest regards,\nTeam Cynbit Technologies\nopportunities@cynbit.in"
    if r["intent"] == "spam":
        return ""
    if r["intent"] == "internship":
        return (hello + "Thank you for your interest in learning with Cynbit. Our BitElevate programme is a 60-day remote "
                "internship where you build real projects and ship one pull request a day across six tracks. "
                "You can see the tracks and enrol at cynbit.in/bitelevate. Tell us which track interests you and we will "
                "guide you." + sign)
    if r["intent"] == "job_application":
        return (hello + "Thank you for your interest in working with Cynbit. Please apply for the open role on cynbit.in/careers "
                "so our team can review your profile and share the next step." + sign)
    if r["intent"] == "partnership":
        return (hello + "Thanks for reaching out about working together. Could you share a short note on your company, "
                "the kind of projects you have in mind and how you see the partnership working? We will set up a call "
                "with the right person." + sign)
    if r["intent"] == "support":
        return (hello + "Thanks for letting us know. We have passed this to your project team, who will get back to you "
                "shortly. If it is blocking your users, reply with 'urgent' and a phone number." + sign)
    names = ", ".join(LABELS[s] for s in r["service_lines"]) or "your project"
    proof = next((h for h in hits if h["type"] == "case_study"), None)
    proof_line = f" We have done similar work before, for example {proof['title']}." if proof else ""
    asks = "".join(f"\n- {q}" for q in r["discovery_questions"])
    return (hello + f"Thank you for reaching out to Cynbit about {names}.{proof_line} "
            f"The next step is a short discovery call to understand your requirements."
            + (f" To make that call useful, it would help to know:{asks}" if asks else "")
            + "\n\nPlease reply with two time slots that suit you." + sign)
