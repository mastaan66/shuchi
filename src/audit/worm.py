"""
WORM log with hash chain and TPM quote — placeholder
"""

import hashlib


def append_log(entry, prev_hash):
    data = prev_hash + entry
    return hashlib.sha256(data.encode()).hexdigest()
