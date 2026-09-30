"""SLM stub: template answer grounded in retrieved context. Offline only."""
from .retriever import Retriever

THRESHOLD = 0.15
DECLINE = "I don't have a source \u2013 declining. \u092e\u0947\u0930\u0947 \u092a\u093e\u0938 \u0938\u094d\u0930\u094b\u0924 \u0928\u0939\u0940\u0902 \u0939\u0948"


class MitraAssistant:
    def __init__(self, docs_dir=None, threshold=THRESHOLD):
        self.retriever = Retriever(docs_dir)
        self.threshold = threshold

    def answer(self, query, lang="en"):
        hits = self.retriever.query(query)
        if not hits or hits[0]["score"] < self.threshold:
            return {"answer": DECLINE, "citations": [], "declined": True,
                    "scores": [h["score"] for h in hits]}
        top = hits[0]
        if lang == "hi":
            text = (f"[{top['doc_id']}:{top['line']}] \u0915\u0947 \u0905\u0928\u0941\u0938\u093e\u0930: "
                    f"{top['snippet']}\n\u0938\u0932\u093e\u0939: \u0932\u0949\u0917 \u092c\u0941\u0915 \u092e\u0947\u0902 \u0926\u0930\u094d\u091c \u0915\u0930\u0947\u0902\u0964")
        else:
            text = (f"Per {top['doc_id']} (line {top['line']}): {top['snippet']}\n"
                    f"Action: follow SOP steps in cited doc; log and escalate if fault repeats.")
        cites = [{"doc_id": h["doc_id"], "line": h["line"],
                  "score": round(h["score"], 3)} for h in hits]
        return {"answer": text, "citations": cites, "declined": False,
                "scores": [h["score"] for h in hits]}
