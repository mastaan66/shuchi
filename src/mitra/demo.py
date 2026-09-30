"""CLI: python demo.py --query '...' --lang en|hi. Prints answer + citations."""
import argparse, json
from .assistant import MitraAssistant


def main():
    ap = argparse.ArgumentParser(description="MITRA-Edge offline demo")
    ap.add_argument("--query", required=True, help="user question")
    ap.add_argument("--lang", default="en", choices=["en", "hi"])
    a = ap.parse_args()
    res = MitraAssistant().answer(a.query, a.lang)
    print("Q:", a.query)
    print("A:", res["answer"])
    print("Citations:", json.dumps(res["citations"], ensure_ascii=False, indent=2))
    print("Declined:", res["declined"])


if __name__ == "__main__":
    main()
