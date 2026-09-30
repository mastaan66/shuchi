"""SHUCHI corpus runner — walks tests/corpus, calls process_file, prints verdicts.

Usage: venv/bin/python tests/run_corpus.py [--corpus tests/corpus] [--out /tmp/shuchi_clean]
Asserts: every file gets a verdict (no silent pass).
"""

import os
import sys
import argparse
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.pipeline.main import process_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="tests/corpus")
    ap.add_argument("--out", default="/tmp/shuchi_clean")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument(
        "--sample", type=int, default=0, help="run only first N files (0=all)"
    )
    args = ap.parse_args()

    corpus = Path(args.corpus)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    files = sorted(
        [p for p in corpus.rglob("*") if p.is_file() and p.name != "README.md"]
    )
    if not files:
        print("No corpus files found!")
        sys.exit(2)
    if args.sample:
        files = files[: args.sample]
        print(f"(sample mode: first {len(files)} files)")

    counts = Counter()
    errors = []

    def _run_one(item):
        i, f = item
        out = outdir / f"clean_{f.parent.name}_{f.name}"
        try:
            res = process_file(str(f), str(out))
        except Exception as e:
            return (str(f.relative_to(corpus)), None, f"EXCEPTION: {e}")
        return (str(f.relative_to(corpus)), res.get("verdict"), None)

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for rel, verdict, err in ex.map(_run_one, enumerate(files)):
            if err or not verdict:
                msg = err or "MISSING VERDICT (silent pass)"
                errors.append((rel, msg))
                counts["EXCEPTION" if err else "MISSING_VERDICT"] += 1
                print(
                    f"[{'EXCEPTION' if err else 'MISSING_VERDICT'}] {rel} -> {msg}",
                    flush=True,
                )
                continue
            counts[verdict] += 1
            print(f"[{verdict}] {rel}", flush=True)

    print("\n=== CORPUS SUMMARY ===")
    print(f"Total files: {len(files)}")
    for k, v in counts.most_common():
        print(f"  {k}: {v}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for f, e in errors[:20]:
            print(f"  {f}: {e}")

    # No silent pass: every file must have a verdict
    assert sum(counts.values()) == len(files), "Some files had no verdict!"
    assert "MISSING_VERDICT" not in counts and "EXCEPTION" not in counts, (
        f"Silent pass / exceptions detected: {errors[:5]}"
    )
    print("\nPASS: every file has a verdict (no silent pass).")


if __name__ == "__main__":
    main()
