"""
SHUCHI Audit — PDF receipt generator (TRL-4).

Reads the JSON receipt at var/log/shuchi/receipt.json (written by
src.pipeline.main.run_pipeline / src.audit.worm.sign_receipt) and renders
a printable PDF listing per-file verdict, hashes and TPM status.

Uses reportlab when available; otherwise falls back to writing a
print-ready HTML file with a .pdf.html suffix path returned alongside.

Usage:
    from src.audit.receipt_pdf import generate_receipt_pdf
    pdf_path = generate_receipt_pdf()  # defaults in/out

    python -m src.audit.receipt_pdf \
        --receipt var/log/shuchi/receipt.json \
        --out var/log/shuchi/receipt.pdf
"""

import html as _html
import json
import os
from datetime import datetime, timezone

DEFAULT_RECEIPT_JSON = "./var/log/shuchi/receipt.json"
DEFAULT_RECEIPT_PDF = "./var/log/shuchi/receipt.pdf"


def load_receipt(receipt_path=DEFAULT_RECEIPT_JSON):
    """Load receipt JSON; return dict with 'files' list (empty if missing)."""
    if not os.path.exists(receipt_path):
        return {"files": [], "timestamp": None, "note": f"not found: {receipt_path}"}
    with open(receipt_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and isinstance(data.get("files"), list):
        return data
    # tolerate a bare list or single-file dict
    if isinstance(data, list):
        return {"files": data, "timestamp": None}
    return {"files": [data], "timestamp": data.get("timestamp")}


def _file_rows(receipt):
    rows = []
    for fe in receipt.get("files", []):
        scans = fe.get("scan_results", [])
        if isinstance(scans, list):
            scan_txt = (
                "; ".join(
                    f"{s.get('engine', '?')}: {s.get('status', '?')}" for s in scans
                )
                or "—"
            )
        else:
            scan_txt = str(scans) if scans else "—"
        rows.append(
            {
                "input": fe.get("input", "—"),
                "type": fe.get("mime_type") or fe.get("true_extension") or "—",
                "verdict": fe.get("verdict", "—"),
                "rebuild": fe.get("rebuild_status", "—"),
                "scan": scan_txt,
                "in_hash": fe.get("input_hash") or "—",
                "out_hash": fe.get("output_hash") or "—",
                "tpm": fe.get("tpm_status", "—"),
                "worm": str(fe.get("worm_verified", "—")),
            }
        )
    return rows


def _render_with_reportlab(receipt, out_path):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
    )
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )
    story = [
        Paragraph("SHUCHI — Transfer Receipt", styles["Title"]),
        Paragraph(
            f"Generated: {datetime.now(timezone.utc).isoformat()}<br/>"
            f"Receipt timestamp: {receipt.get('timestamp') or '—'}<br/>"
            f"Files: {len(receipt.get('files', []))} &nbsp;|&nbsp; "
            f"YARA: 30 rules (TRL-4 freeze) &nbsp;|&nbsp; "
            f"Formats: PDF, DOCX, XLSX, PPTX, JPG/PNG",
            styles["Normal"],
        ),
        Spacer(1, 6 * mm),
    ]
    header = ["File", "Type", "Scan", "Rebuild / Verdict", "Hashes", "TPM / WORM"]
    body: list = [header]
    for r in _file_rows(receipt):
        body.append(
            [
                Paragraph(_html.escape(str(r["input"]))[:160], styles["Normal"]),
                Paragraph(_html.escape(str(r["type"]))[:60], styles["Normal"]),
                Paragraph(_html.escape(f"{r['scan']}")[:220], styles["Normal"]),
                Paragraph(
                    _html.escape(f"{r['rebuild']} / {r['verdict']}")[:120],
                    styles["Normal"],
                ),
                Paragraph(
                    _html.escape(
                        f"in: {r['in_hash']}"[:80] + f"<br/>out: {r['out_hash']}"[:80]
                    ),
                    styles["Normal"],
                ),
                Paragraph(_html.escape(f"{r['tpm']} / {r['worm']}"), styles["Normal"]),
            ]
        )
    if len(body) == 1:
        story.append(Paragraph("No files in receipt.", styles["Normal"]))
    else:
        t = Table(body, repeatRows=1)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                ]
            )
        )
        story.append(t)
    story += [
        Spacer(1, 6 * mm),
        Paragraph(
            "Operator: ____________________ &nbsp;&nbsp; "
            "Signature: ____________________ &nbsp;&nbsp; "
            "Date: __________",
            styles["Normal"],
        ),
        Paragraph(
            "परीक्षण: हिंदी पाठ संरक्षण — यह रसीद पुनर्निर्मित फ़ाइलों की सूची है।",
            styles["Normal"],
        ),
    ]
    doc.build(story)
    return out_path


def _render_html_fallback(receipt, out_path):
    """Fallback when reportlab is missing: write print-ready HTML next to out_path."""
    fallback_path = out_path + ".html" if not out_path.endswith(".html") else out_path
    parts = []
    for r in _file_rows(receipt):
        parts.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{} / {}</td>"
            "<td>in: {}<br>out: {}</td><td>{} / {}</td></tr>".format(
                _html.escape(str(r["input"])),
                _html.escape(str(r["type"])),
                _html.escape(str(r["scan"])),
                _html.escape(str(r["rebuild"])),
                _html.escape(str(r["verdict"])),
                _html.escape(str(r["in_hash"])),
                _html.escape(str(r["out_hash"])),
                _html.escape(str(r["tpm"])),
                _html.escape(str(r["worm"])),
            )
        )
    rows = "".join(parts)
    page = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>SHUCHI Receipt</title></head><body>
<h1>SHUCHI — Transfer Receipt</h1>
<p>Generated: {_html.escape(datetime.now(timezone.utc).isoformat())} |
Receipt: {_html.escape(str(receipt.get("timestamp") or "—"))} |
Files: {len(receipt.get("files", []))}</p>
<table border="1" cellpadding="4">
<tr><th>File</th><th>Type</th><th>Scan</th><th>Rebuild/Verdict</th>
<th>Hashes</th><th>TPM/WORM</th></tr>
{rows or '<tr><td colspan="6">No files in receipt.</td></tr>'}
</table>
<p>परीक्षण: हिंदी पाठ संरक्षण — यह रसीद पुनर्निर्मित फ़ाइलों की सूची है।</p>
</body></html>"""
    with open(fallback_path, "w", encoding="utf-8") as f:
        f.write(page)
    return fallback_path


def generate_receipt_pdf(
    receipt_path=DEFAULT_RECEIPT_JSON, out_path=DEFAULT_RECEIPT_PDF
):
    """Generate a PDF receipt from receipt JSON. Returns the output path."""
    receipt = load_receipt(receipt_path)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    try:
        import reportlab  # noqa: F401
    except ImportError:
        return _render_html_fallback(receipt, out_path)
    return _render_with_reportlab(receipt, out_path)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="SHUCHI PDF receipt generator (TRL-4)")
    ap.add_argument("--receipt", default=DEFAULT_RECEIPT_JSON)
    ap.add_argument("--out", default=DEFAULT_RECEIPT_PDF)
    args = ap.parse_args()
    print(generate_receipt_pdf(args.receipt, args.out))
