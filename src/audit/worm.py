"""
SHUCHI Audit — TPM 2.0 quote + hash-chain WORM log + signed receipt.
"""

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone

WORM_LOG_PATH = "./var/log/shuchi/worm.log"
RECEIPT_KEY_PATH = "./var/log/shuchi/tpm_receipt_key.pem"


def init_worm():
    os.makedirs("./var/log/shuchi", exist_ok=True)
    if not os.path.exists(WORM_LOG_PATH):
        with open(WORM_LOG_PATH, "w") as f:
            json.dump({"prev_hash": "0" * 64, "entries": []}, f, indent=2)


def append_log(entry):
    init_worm()
    with open(WORM_LOG_PATH, "r") as f:
        log = json.load(f)

    entry_data = json.dumps(entry, sort_keys=True)
    new_hash = hashlib.sha256((log["prev_hash"] + entry_data).encode()).hexdigest()

    log["entries"].append(
        {
            "index": len(log["entries"]),
            "entry": entry,
            "hash": new_hash,
            "prev_hash": log["prev_hash"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    log["prev_hash"] = new_hash

    with open(WORM_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

    return new_hash


def verify_log():
    if not os.path.exists(WORM_LOG_PATH):
        return True
    with open(WORM_LOG_PATH, "r") as f:
        log = json.load(f)
    prev = "0" * 64
    for e in log["entries"]:
        expected = hashlib.sha256(
            (prev + json.dumps(e["entry"], sort_keys=True)).encode()
        ).hexdigest()
        if e["hash"] != expected:
            return False
        if e["prev_hash"] != prev:
            return False
        prev = e["hash"]
    return True


def tpm_quote(data):
    try:
        result = subprocess.run(
            [
                "tpm2_quote",
                "--hash-alg",
                "sha256",
                "--qualification",
                "0000000000",
                "-o",
                "-",
                "0x81000001",
            ],
            input=data.encode(),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return {"tpm_quote": result.stdout, "status": "SIGNED"}
        return {"tpm_quote": None, "status": "NO_TPM", "detail": result.stderr.strip()}
    except FileNotFoundError:
        return {
            "tpm_quote": None,
            "status": "NO_TPM",
            "detail": "tpm2-tools not installed",
        }
    except Exception as e:
        return {"tpm_quote": None, "status": "ERROR", "detail": str(e)}


def sign_receipt(receipt_data):
    data_str = json.dumps(receipt_data, sort_keys=True)
    tpm_result = tpm_quote(data_str)
    entry_hash = append_log(
        {
            "type": "receipt",
            "data_hash": hashlib.sha256(data_str.encode()).hexdigest(),
            "tpm_status": tpm_result["status"],
        }
    )
    return {
        "receipt": receipt_data,
        "worm_entry_hash": entry_hash,
        "tpm_quote": tpm_result,
        "verified": verify_log(),
    }


def get_receipt(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        return json.load(f)
