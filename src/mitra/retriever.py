"""Offline TF-IDF retriever over local docs/. No network calls."""
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Retriever:
    def __init__(self, docs_dir=None, top_k=3):
        self.docs_dir = Path(docs_dir or Path(__file__).parent / "docs")
        self.top_k = top_k
        self.doc_ids, self.texts, self.lines = [], [], []
        for p in sorted(self.docs_dir.glob("*.md")) + sorted(self.docs_dir.glob("*.txt")):
            txt = p.read_text(encoding="utf-8")
            self.doc_ids.append(p.name)
            self.texts.append(txt)
            self.lines.append(txt.splitlines())
        self.vec = TfidfVectorizer()
        self.matrix = self.vec.fit_transform(self.texts)

    def _best_line(self, doc_idx, query):
        qtokens = set(query.lower().split())
        best_no, best_hit = 1, -1
        for i, ln in enumerate(self.lines[doc_idx], 1):
            hit = len(qtokens & set(ln.lower().split()))
            if hit > best_hit:
                best_hit, best_no = hit, i
        return best_no

    def query(self, text, top_k=None):
        k = top_k or self.top_k
        q = self.vec.transform([text])
        scores = cosine_similarity(q, self.matrix)[0]
        ranked = sorted(range(len(self.doc_ids)), key=lambda i: scores[i], reverse=True)[:k]
        out = []
        for i in ranked:
            ln = self._best_line(i, text)
            snippet = (self.lines[i][ln - 1].strip() if self.lines[i] else "")[:200]
            out.append({"doc_id": self.doc_ids[i], "score": float(scores[i]),
                        "line": ln, "snippet": snippet})
        return out
