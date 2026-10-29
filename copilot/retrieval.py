"""Small BM25 search over Cynbit's public knowledge base (services, products, case studies).

BM25 needs no API key, no GPU and no vector database, and with ~30 short documents it is as good as
embeddings. The interface (search(text, k) -> docs) stays the same if it is later swapped for
embeddings in Pinecone/pgvector, which Cynbit already lists in its stack.
"""
import json
import math
import re
from collections import Counter
from pathlib import Path

KB_PATH = Path(__file__).resolve().parent.parent / "data" / "cynbit_kb.json"
STOP = set("a an and are as at be but by can do for from has have i in is it me my of on or our so that the this to "
           "us we what with you your want need would like please hi hello sir madam team looking".split())


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w[:-1] if len(w) > 4 and w.endswith("s") else w for w in words if w not in STOP]


class KnowledgeBase:
    def __init__(self, path: Path = KB_PATH, k1: float = 1.5, b: float = 0.75):
        data = json.loads(path.read_text(encoding="utf-8"))
        self.company = data["company"]
        self.docs = data["docs"]
        self.k1, self.b = k1, b
        self.tokens = [tokenize(f"{d['title']} {d['title']} {d['text']}") for d in self.docs]
        self.avg_len = sum(map(len, self.tokens)) / len(self.tokens)
        df = Counter(t for toks in self.tokens for t in set(toks))
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self.tf = [Counter(toks) for toks in self.tokens]

    def search(self, text: str, k: int = 4, types: tuple[str, ...] | None = None) -> list[dict]:
        q = set(tokenize(text))
        scored = []
        for doc, tf, toks in zip(self.docs, self.tf, self.tokens):
            if types and doc["type"] not in types:
                continue
            s = 0.0
            for t in q & tf.keys():
                f = tf[t]
                s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * len(toks) / self.avg_len))
            if s > 0:
                scored.append((s, doc))
        scored.sort(key=lambda x: -x[0])
        return [dict(d, score=round(s, 2)) for s, d in scored[:k]]
