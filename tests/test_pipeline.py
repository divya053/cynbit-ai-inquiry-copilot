"""python -m unittest discover tests"""
import json
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from copilot import llm, offline, pipeline  # noqa: E402
from copilot.schema import ANALYSIS_SCHEMA  # noqa: E402


class Offline(unittest.TestCase):
    def test_budget_parsing(self):
        self.assertEqual(offline.parse_budget("budget Rs 4 lakh")[1], 400000)
        self.assertEqual(offline.parse_budget("3-5 lakh")[1], 300000)
        self.assertEqual(offline.parse_budget("60 hazaar tak")[1], 60000)
        self.assertEqual(offline.parse_budget("$8k")[1], 672000)
        self.assertEqual(offline.parse_budget("our team enters 300 invoices")[1], 0)

    def test_timeline(self):
        self.assertEqual(offline.parse_timeline("live in 3 weeks")[1], "high")
        self.assertEqual(offline.parse_timeline("1 mahine me")[1], "medium")
        self.assertEqual(offline.parse_timeline("no rush")[1], "low")

    def test_routing_and_score(self):
        r = pipeline.run("I am the founder. Need an AI chatbot for our clinic, budget 6 lakh, in 2 weeks.", use_llm=False)
        self.assertEqual(r["analysis"]["intent"], "client_project")
        self.assertGreaterEqual(r["lead_score"], 70)
        self.assertTrue(r["priority"].startswith("P1"))
        spam = pipeline.run("You have won a lottery, send bank details", use_llm=False)
        self.assertEqual(spam["lead_score"], 0)
        self.assertEqual(spam["analysis"]["reply_draft"], "")

    def test_offline_output_matches_schema_keys(self):
        a = offline.analyze("hi i want website", pipeline.kb())
        self.assertEqual(set(ANALYSIS_SCHEMA["required"]), set(a))


def fake_response(payload):
    return types.SimpleNamespace(stop_reason="end_turn", model="claude-opus-5-5",
                                 usage=types.SimpleNamespace(input_tokens=900, output_tokens=300),
                                 content=[types.SimpleNamespace(type="thinking"),
                                          types.SimpleNamespace(type="text", text=json.dumps(payload))])


class LLMPath(unittest.TestCase):
    """Claude is mocked: these check the wiring (request shape, parsing, fallback), not model quality."""

    def setUp(self):
        self.payload = offline.analyze("Need a Revio setup for our 6 hotels, budget 2 lakh", pipeline.kb())
        self.payload["intent"] = "client_project"

    def test_request_and_parse(self):
        client = mock.MagicMock()
        client.beta.messages.create.return_value = fake_response(self.payload)
        with mock.patch("anthropic.Anthropic", return_value=client):
            r = pipeline.run("Need a Revio setup for our 6 hotels", use_llm=True, api_key="test")
        kwargs = client.beta.messages.create.call_args.kwargs
        self.assertEqual(kwargs["model"], llm.MODEL)
        self.assertEqual(kwargs["output_config"]["format"]["schema"], ANALYSIS_SCHEMA)
        self.assertEqual(kwargs["fallbacks"], "default")
        self.assertIn("CONTEXT", kwargs["messages"][0]["content"])
        self.assertTrue(r["engine"].startswith("Claude"))
        self.assertIsNone(r["error"])

    def test_api_failure_falls_back_to_rules(self):
        client = mock.MagicMock()
        client.beta.messages.create.side_effect = RuntimeError("network down")
        with mock.patch("anthropic.Anthropic", return_value=client):
            r = pipeline.run("Need a website for my shop", use_llm=True, api_key="test")
        self.assertEqual(r["engine"], "offline rules")
        self.assertIn("network down", r["error"])


if __name__ == "__main__":
    unittest.main()
