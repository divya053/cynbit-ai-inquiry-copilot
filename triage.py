"""Command line: python triage.py "message text"   (or pipe a message in)"""
import json
import sys

from copilot import pipeline

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) or sys.stdin.read()
    print(json.dumps(pipeline.run(text), indent=2, ensure_ascii=False))
