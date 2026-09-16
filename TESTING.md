# Testing — SHUCHI

We are building and testing as per the 15-day plan. This is the test plan that will be run and shown in the 2-minute video.

## Corpus — 130 files

| Group | Count | What |
|-------|-------|------|
| Clean normal | 30 | 10 PDF, 10 DOCX, 5 XLSX, 5 PPTX — with Office formatting |
| Clean Hindi | 10 | 5 DOCX and 5 PDF with Hindi text |
| Infected | 30 | 10 EICAR, 10 Office macro samples (oletools), 10 YARA hits |
| Malformed | 30 | 10 polyglot, 10 wrong extension, 10 broken headers |
| Mixed | 30 | Random mix for stress |

Total 130. At TRL-4 we test 5 formats: PDF, DOCX, XLSX, PPTX, JPG/PNG. At TRL-6 we will cover 15 formats.

Corpus is in `tests/corpus/` (samples are not in git for safety; place them locally).

## Baseline — EICAR

EICAR is the standard test string, not real malware.

```bash
./scripts/eicar_test.sh
```

This must be flagged by ClamAV and YARA. If EICAR is not flagged, the rig is not correct.

## Tests

1. **True type.** Files with wrong extensions and polyglot files must be flagged by libmagic and blocked or logged.
2. **Scan.** All infected files must be logged as infected. Clean files must not be flagged. Target is less than 1% false positive on clean set.
3. **Rebuild.** Every file that is transferred must be a rebuilt file, not the original. Check hash of input vs output — they must differ. Hindi text and Office formatting must be kept.
4. **Fail safe.** Unsupported type or rebuild error must result in BLOCKED, not silent pass. Every file must have a per-file verdict on the receipt.
5. **Wipe.** After handover, dirty temp dir must be wiped. Check with `find /tmp/shuchi -type f` — must be empty.
6. **Log.** WORM log must have a hash chain. Edit test must fail verification.

## Run

```bash
# EICAR baseline
./scripts/eicar_test.sh

# Full corpus
python -m tests.run_corpus --corpus tests/corpus --clean /media/clean

# Check Hindi
python -m tests.check_hindi --corpus tests/corpus/hindi

# Check log
python src/audit/verify_log.py /var/log/shuchi/worm.log
```

## Expected result

* No silent pass.
* Hindi text kept after rebuild.
* Receipt printed per transfer with per-file verdict, hashes, TPM signature.

## Video

Day 10 to 11 we record the 2-minute video: insert dirty USB, show scan and rebuild, show clean USB and receipt, show log, show Hindi file kept.

We will complete this by 28 September with guidance.
