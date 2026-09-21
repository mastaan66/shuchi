"""
SHUCHI Pipeline — Real implementation
Dirty USB (read-only) -> verify -> scan -> rebuild -> clean USB + receipt
"""

import sys
import os
import json
import hashlib
import subprocess
import shutil
from datetime import datetime, timezone

from src.cdr.rebuild import rebuild_pdf, rebuild_image, rebuild_office
from src.audit.worm import sign_receipt, verify_log
from src.cdr.intake import check_true_type, is_supported

SUPPORTED_TYPES = {
    "application/pdf": ["pdf"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ["docx"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ["xlsx"],
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": [
        "pptx"
    ],
    "image/jpeg": ["jpg", "jpeg"],
    "image/png": ["png"],
}

YARA_RULES = "rules/yara/index.yar"


def scan_clamav(filepath):
    try:
        result = subprocess.run(
            ["clamscan", "--no-summary", filepath],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if "FOUND" in result.stdout or result.returncode == 1:
            return {
                "engine": "ClamAV",
                "status": "INFECTED",
                "detail": result.stdout.strip(),
            }
        return {"engine": "ClamAV", "status": "CLEAN", "detail": "no threats"}
    except Exception as e:
        return {"engine": "ClamAV", "status": "ERROR", "detail": str(e)}


def scan_yara(filepath):
    try:
        import yara

        rules = yara.compile(filepath=YARA_RULES)
        matches = rules.match(filepath)
        if matches:
            return {
                "engine": "YARA",
                "status": "SUSPICIOUS",
                "detail": [m.rule for m in matches],
            }
        return {"engine": "YARA", "status": "CLEAN", "detail": "no matches"}
    except Exception as e:
        return {"engine": "YARA", "status": "ERROR", "detail": str(e)}


def scan_oletools(filepath):
    try:
        from oletools.olevba import VBA_Parser

        vba = VBA_Parser(filepath)
        vba.close()
        return {
            "engine": "oletools",
            "status": "SUSPICIOUS",
            "detail": "VBA macro detected",
        }
    except Exception:
        return {"engine": "oletools", "status": "CLEAN", "detail": "no macros detected"}


def scan_file(filepath):
    results = []
    results.append(scan_clamav(filepath))
    results.append(scan_yara(filepath))
    if filepath.lower().endswith((".docx", ".xlsx", ".pptx", ".doc", ".xls", ".ppt")):
        results.append(scan_oletools(filepath))
    return results


def rebuild_file(in_path, out_path, file_type):
    ext = file_type.split("/")[-1]
    if ext == "pdf":
        rebuild_pdf(in_path, out_path)
    elif ext in ("jpg", "jpeg", "png"):
        rebuild_image(in_path, out_path)
    elif ext in ("docx", "xlsx", "pptx"):
        rebuild_office(in_path, out_path, ext)
    else:
        raise ValueError(f"Unsupported rebuild type: {file_type}")


def process_file(in_path, out_path, dirty=False):
    file_result = {
        "input": in_path,
        "output": out_path,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verdict": "PASSED",
        "scan_results": [],
        "rebuild_status": "REBUILT",
    }

    mime = check_true_type(in_path)
    file_result["mime_type"] = mime
    file_result["true_extension"] = SUPPORTED_TYPES.get(mime, [None])[0]

    if not is_supported(mime):
        file_result["verdict"] = "BLOCKED"
        file_result["reason"] = "TYPE NOT SUPPORTED"
        return file_result

    scans = scan_file(in_path)
    file_result["scan_results"] = scans

    infected = any(s["status"] in ("INFECTED", "SUSPICIOUS") for s in scans)
    if infected:
        file_result["verdict"] = "INFECTED_REBUILT"
    else:
        file_result["verdict"] = "CLEAN_REBUILT"

    try:
        rebuild_file(in_path, out_path, mime)
        if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
            file_result["rebuild_status"] = "REBUILD FAILED"
            file_result["verdict"] = "BLOCKED"
    except Exception as e:
        file_result["rebuild_status"] = f"REBUILD FAILED: {e}"
        file_result["verdict"] = "BLOCKED"

    input_hash = hashlib.sha256(open(in_path, "rb").read()).hexdigest()
    try:
        output_hash = hashlib.sha256(open(out_path, "rb").read()).hexdigest()
    except:
        output_hash = None
    file_result["input_hash"] = input_hash
    file_result["output_hash"] = output_hash

    if file_result["verdict"] != "BLOCKED":
        from src.audit.worm import sign_receipt

        signed = sign_receipt(file_result)
        file_result["tpm_status"] = signed["tpm_quote"]["status"]
        file_result["worm_verified"] = signed["verified"]

    if dirty:
        wipe_path(in_path)

    return file_result


def wipe_path(path, passes=3):
    if os.path.isfile(path):
        size = os.path.getsize(path)
        with open(path, "ba") as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(size))
        os.remove(path)


def run_pipeline(dirty_dir, clean_dir, receipt_path="./var/log/shuchi/receipt.json"):
    os.makedirs(clean_dir, exist_ok=True)
    os.makedirs("./var/log/shuchi", exist_ok=True)
    from src.audit.worm import init_worm

    init_worm()

    receipt = {"files": [], "timestamp": datetime.now(timezone.utc).isoformat()}

    for fname in os.listdir(dirty_dir):
        in_path = os.path.join(dirty_dir, fname)
        if not os.path.isfile(in_path):
            continue
        out_name = f"clean_{fname}"
        out_path = os.path.join(clean_dir, out_name)
        result = process_file(in_path, out_path, dirty=True)
        receipt["files"].append(result)
        print(f"[{result['verdict']}] {fname} -> {out_name}")

    with open(receipt_path, "w") as f:
        json.dump(receipt, f, indent=2)

    return receipt


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py --dirty <dir> --clean <dir>")
        sys.exit(1)

    dirty_dir = (
        sys.argv[sys.argv.index("--dirty") + 1] if "--dirty" in sys.argv else None
    )
    clean_dir = (
        sys.argv[sys.argv.index("--clean") + 1] if "--clean" in sys.argv else None
    )

    if dirty_dir and clean_dir:
        receipt = run_pipeline(dirty_dir, clean_dir)
        print(f"\nPipeline complete. {len(receipt['files'])} files processed.")
    else:
        print("SHUCHI Pipeline — run with --dirty and --clean directories")
        sys.exit(1)
