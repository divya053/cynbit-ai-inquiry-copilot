"""Streamlit demo: streamlit run app.py"""
import json
import os
from pathlib import Path

import streamlit as st

from copilot import llm, pipeline
from copilot.schema import LABELS

ROOT = Path(__file__).resolve().parent
SAMPLES = [json.loads(x) for x in (ROOT / "data" / "eval_inquiries.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]

st.set_page_config(page_title="Cynbit Inquiry Copilot", page_icon="📨", layout="wide")

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Engine")
    key = ""
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        pass
    key = key or os.environ.get("ANTHROPIC_API_KEY", "")
    typed = st.text_input("Anthropic API key (optional)", type="password",
                          help="Used only for this browser session, never stored. Without a key the app uses the offline rules.")
    key = typed or key
    use_llm = st.toggle("Use Claude", value=llm.available(key), disabled=not llm.available(key))
    st.caption(f"Model: `{llm.MODEL}` · effort `{llm.EFFORT}`" if use_llm else "Running on offline rules (no key).")
    st.divider()
    st.markdown("**What this is**\n\nA proof of concept for Cynbit: every message from the contact form, email or "
                "WhatsApp is read, classified, scored, routed to the right team and given a ready reply draft, "
                "so the 24-hour response promise becomes minutes.")
    st.caption("Knowledge base: public pages of cynbit.in (Oct 2026).")

st.title("📨 Cynbit Inquiry Copilot")
st.caption("Triage → lead score → routing → grounded reply draft, for every inbound inquiry.")

tab1, tab2, tab3 = st.tabs(["Triage an inquiry", "Inbox view (30 samples)", "Evaluation"])


def show(result: dict):
    a = result["analysis"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Intent", {"client_project": "Client lead", "internship": "Internship", "job_application": "Job seeker",
                         "partnership": "Partner", "support": "Support", "spam": "Spam"}[a["intent"]])
    c2.metric("Lead score", result["lead_score"])
    c3.metric("Priority", result["priority"])
    c4.metric("Urgency", a["urgency"].title())
    st.info(f"**Route to:** {result['route_to']}  ·  **SLA:** {result['sla']}")
    if result.get("error"):
        st.warning(result["error"])

    left, right = st.columns([1, 1])
    with left:
        st.subheader("What they need")
        st.write(a["summary"])
        st.markdown("**Services:** " + (", ".join(LABELS[s] for s in a["service_lines"]) or "—"))
        rows = {"Company": a["company"] or "—", "Industry": a["industry"] or "—",
                "Budget": f"{a['budget_text']} (≈ Rs {a['budget_inr']:,})" if a["budget_inr"] else "not stated",
                "Timeline": a["timeline"] or "not stated", "Decision maker": "yes" if a["decision_maker"] else "not stated",
                "Language": a["language"].title()}
        st.table({"Field": list(rows), "Value": list(rows.values())})
        if a["requirements"]:
            st.markdown("**Requirements**\n" + "\n".join(f"- {x}" for x in a["requirements"]))
        if a["missing_info"]:
            st.markdown("**Missing before a proposal:** " + ", ".join(a["missing_info"]))
        with st.expander("Why this lead score?"):
            st.markdown("\n".join(f"- {r}" for r in result["score_reasons"]))
    with right:
        st.subheader("Reply draft")
        if a["reply_draft"]:
            st.text_area("Edit before sending", a["reply_draft"], height=300, key=f"reply_{hash(a['reply_draft'])}")
        else:
            st.write("No reply (spam).")
        if a["discovery_questions"]:
            st.markdown("**Discovery-call questions**\n" + "\n".join(f"{i}. {q}" for i, q in enumerate(a["discovery_questions"], 1)))
        with st.expander("Cynbit context used (retrieval)"):
            for d in result["context"]:
                st.markdown(f"- `{d['type']}` {d['title']} (BM25 {d['score']})")
    with st.expander("Raw JSON"):
        st.json(result)
    st.caption(f"Engine: {result['engine']} · {result['latency_ms']} ms")


with tab1:
    qs = st.query_params.get("sample", "")                       # ?sample=4 opens with sample 4 analysed
    start = int(qs) if qs.isdigit() and 1 <= int(qs) <= len(SAMPLES) else 0
    pick = st.selectbox("Try a sample", ["(write your own)"] + [f"#{s['id']} {s['text'][:90]}…" for s in SAMPLES], index=start)
    default = "" if pick.startswith("(") else SAMPLES[int(pick[1:pick.index(' ')]) - 1]["text"]
    text = st.text_area("Inquiry (English, Hindi or Hinglish)", default, height=150,
                        placeholder="Paste a message from the contact form, email or WhatsApp…")
    auto = start and not st.session_state.get("auto_done")
    if st.button("Analyze", type="primary", disabled=not text.strip()) or auto:
        st.session_state["auto_done"] = True
        with st.spinner("Reading the inquiry…"):
            st.session_state["result"] = pipeline.run(text, use_llm=use_llm, api_key=key or None)
    if "result" in st.session_state:
        show(st.session_state["result"])

with tab2:
    st.write("Runs all 30 sample inquiries the way a morning inbox would arrive, then sorts them so the hottest leads are on top.")
    if st.button("Process inbox"):
        bar = st.progress(0.0)
        out = []
        for i, s in enumerate(SAMPLES):
            r = pipeline.run(s["text"], use_llm=use_llm, api_key=key or None)
            a = r["analysis"]
            out.append({"#": s["id"], "Score": r["lead_score"], "Priority": r["priority"],
                        "Intent": LABELS[a["intent"]], "Services": ", ".join(LABELS[x] for x in a["service_lines"]),
                        "Budget (Rs)": a["budget_inr"] or None, "Urgency": a["urgency"], "Route to": r["route_to"],
                        "Message": s["text"][:120]})
            bar.progress((i + 1) / len(SAMPLES))
        out.sort(key=lambda x: (-x["Score"], x["#"]))
        st.session_state["inbox"] = out
    if "inbox" in st.session_state:
        rows = st.session_state["inbox"]
        hot = sum(r["Priority"].startswith("P1") for r in rows)
        auto = sum(r["Intent"] in ("Internship / BitElevate", "Job application", "Spam / irrelevant") for r in rows)
        c1, c2, c3 = st.columns(3)
        c1.metric("Inquiries", len(rows))
        c2.metric("Hot leads (P1)", hot)
        c3.metric("Handled without sales time", auto)
        st.dataframe(rows, use_container_width=True, hide_index=True)

with tab3:
    st.write("Labelled test set: `data/eval_inquiries.jsonl` (30 inquiries, 6 intents, English + Hinglish). "
             "Run `python evaluate.py` (rules) or `python evaluate.py --llm` (Claude).")
    for name in ("offline", "llm"):
        f = ROOT / "results" / f"eval_{name}.json"
        if f.exists():
            data = json.loads(f.read_text(encoding="utf-8"))
            st.subheader(data["metrics"]["engine"])
            st.json(data["metrics"])
            if data["mistakes"]:
                with st.expander(f"{len(data['mistakes'])} inquiries with a mistake"):
                    st.markdown("\n".join(f"- {m}" for m in data["mistakes"]))
