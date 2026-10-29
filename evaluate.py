"""Scores the analyzer on the labelled inquiries in data/eval_inquiries.jsonl.

  python evaluate.py          offline rules (no key needed)
  python evaluate.py --llm    Claude (needs ANTHROPIC_API_KEY)

Writes results/eval_<engine>.json and prints the metrics plus every mistake.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

from copilot import pipeline
from copilot.schema import INTENTS

ROOT = Path(__file__).resolve().parent


def f1(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return 2 * p * r / (p + r) if p + r else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", action="store_true")
    a = ap.parse_args()
    rows = [json.loads(x) for x in (ROOT / "data" / "eval_inquiries.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    per_intent = {i: Counter() for i in INTENTS}
    svc = Counter()
    ok = Counter()
    mistakes, outputs, latency = [], [], []
    for r in rows:
        out = pipeline.run(r["text"], use_llm=a.llm)
        p = out["analysis"]
        latency.append(out["latency_ms"])
        outputs.append({"id": r["id"], "result": out})
        ok["intent"] += p["intent"] == r["intent"]
        for i in INTENTS:
            per_intent[i]["tp"] += p["intent"] == i and r["intent"] == i
            per_intent[i]["fp"] += p["intent"] == i and r["intent"] != i
            per_intent[i]["fn"] += p["intent"] != i and r["intent"] == i
        if r["intent"] in ("client_project", "support"):
            gold, pred = set(r["service_lines"]), set(p["service_lines"])
            svc["tp"] += len(gold & pred)
            svc["fp"] += len(pred - gold)
            svc["fn"] += len(gold - pred)
        if r["intent"] == "client_project":
            ok["leads"] += 1
            ok["urgency"] += p["urgency"] == r["urgency"]
            gb, pb = r["budget_inr"], p["budget_inr"] or 0
            ok["budget"] += (gb == 0 and pb == 0) or (gb > 0 and abs(pb - gb) <= 0.1 * gb)
        wrong = []
        if p["intent"] != r["intent"]:
            wrong.append(f"intent {p['intent']} (expected {r['intent']})")
        if r["intent"] in ("client_project", "support") and set(p["service_lines"]) != set(r["service_lines"]):
            wrong.append(f"services {p['service_lines']} (expected {r['service_lines']})")
        if r["intent"] == "client_project" and p["urgency"] != r["urgency"]:
            wrong.append(f"urgency {p['urgency']} (expected {r['urgency']})")
        if r["intent"] == "client_project" and not ((r["budget_inr"] == 0 and not p["budget_inr"]) or
                                                    (r["budget_inr"] and abs((p["budget_inr"] or 0) - r["budget_inr"]) <= 0.1 * r["budget_inr"])):
            wrong.append(f"budget {p['budget_inr']} (expected {r['budget_inr']})")
        if wrong:
            mistakes.append(f"#{r['id']}: " + "; ".join(wrong))

    n = len(rows)
    metrics = {
        "engine": outputs[0]["result"]["engine"] if outputs else "",
        "inquiries": n,
        "intent_accuracy": round(ok["intent"] / n, 3),
        "intent_macro_f1": round(sum(f1(c["tp"], c["fp"], c["fn"]) for c in per_intent.values()) / len(INTENTS), 3),
        "service_line_micro_f1": round(f1(svc["tp"], svc["fp"], svc["fn"]), 3),
        "urgency_accuracy_on_leads": round(ok["urgency"] / ok["leads"], 3),
        "budget_accuracy_on_leads": round(ok["budget"] / ok["leads"], 3),
        "spam_f1": round(f1(**{k: per_intent["spam"][k] for k in ("tp", "fp", "fn")}), 3),
        "median_latency_ms": sorted(latency)[n // 2],
    }
    print(json.dumps(metrics, indent=2))
    print(f"\n{len(mistakes)} inquiries with at least one mistake:")
    print("\n".join(mistakes) or "none")
    out_dir = ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    name = "llm" if a.llm else "offline"
    (out_dir / f"eval_{name}.json").write_text(json.dumps({"metrics": metrics, "mistakes": mistakes, "outputs": outputs},
                                                         indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
