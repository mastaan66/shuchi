# Architecture — SHUCHI

## Goal

Provide a check-post at the air gap for Maya OS networks. Dirty media never touches the clean side. Only a rebuilt clean copy crosses. Every action is logged in a record that cannot be changed.

## Threat model

* USB drive is assumed dirty. It may contain malware, macros, polyglot files, or wrong extensions.
* Network is air-gapped. No cloud, no internet on the kiosk.
* Attacker may use hidden code in PDF, Office macros, image metadata, or extension spoofing.
* Defence is deterministic rebuild, not just scan. Scan can miss, remaking removes.

Precedent is Agent.btz (2008) where one USB infected SIPRNet and JWICS.

## Workflow

```
Dirty USB
  |
  v
[1] Intake — USBGuard write-block, mount read-only
  |
  v
[2] Check true type — libmagic, extension vs content
  |  |
  |  +--> if not supported or mismatch --> Block, log, do not transfer
  |
  v
[3] Scan offline — ClamAV (offline db), YARA 300, oletools/mraptor
  |  |
  |  +--> result logged per file (clean / infected / suspicious)
  |
  v
[4] Rebuild (CDR) — make new file from content only
  |     qpdf for PDF, exiftool for metadata, Pillow for images,
  |     LibreOffice headless for DOCX/XLSX/PPTX
  |     as per ISO 32000 and OOXML
  |     Hindi and Office formatting kept
  |
  v
  | --- AIR GAP (only rebuilt file crosses) ---
  |
  v
[5] Handover — copy to Clean USB
      TPM 2.0 quote + hash-chain WORM log + PDF receipt per file
  |
  v
[6] Wipe — DoD 3-pass wipe of dirty drive
```

Principle: Original never crosses. Only the rebuilt file crosses. If type is not supported or rebuild fails, file is blocked.

## Dual-media

* Two USB ports: dirty port (read-only) and clean port (write). Hardware write-block on dirty port.
* Software block via USBGuard and udisks read-only mount.
* File never copied directly. It is read, checked, rebuilt in a temp dir, then written to clean USB.

## Components

### Intake
* USBGuard rules to deny write on dirty port.
* udisksctl mount -o ro.
* libmagic to check true type. Extension vs magic compared. Polyglot flagged.

### Scan
* ClamAV with offline CVD files. No freshclam to internet. Update via signed offline pack.
* YARA 300 rules covering Office macros, PDF exploits, script files.
* oletools: olevba, msodde, mraptor for macro risk score.

No cloud. All offline.

### Rebuild (CDR)
* PDF: qpdf --qdf --object-streams=disable then rebuild, exiftool to strip metadata.
* Image: Pillow to open and save as new image, metadata stripped.
* Office: LibreOffice headless to convert and save back (e.g., soffice --headless --convert-to). For DOCX, rebuild via python-docx content copy in later stage.
* If rebuild fails, file is blocked.

At TRL-4, 5 formats: PDF, DOCX, XLSX, PPTX, JPG/PNG. At TRL-6, 15 formats.

### Trust and audit
* TPM 2.0: tpm2_quote for boot and log integrity.
* WORM log: append-only file with hash chain (prev_hash + entry + TPM quote). Cannot be edited.
* PDF receipt per transfer: lists each file, type, scan result, rebuild status, hashes, operator, TPM signature.
* Receipt printer: USB thermal printer for paper copy.

## Hardware

* N100 mini-PC with TPM 2.0, 8GB RAM, 256GB SSD.
* Two USB-A ports with physical labels: DIRTY (red) and CLEAN (green).
* 3.5 inch display for Electron UI.
* USB thermal receipt printer.
* Cost about Rs. 35,000. Power 12V.

## Update without internet

Monthly signed pack: new ClamAV CVD + YARA rules packed as tar.gz, signed with maintainer key, verified on kiosk, then applied. No internet needed.

## Failure handling

* Unsupported type: block, log, receipt shows BLOCKED - TYPE NOT SUPPORTED.
* Scan infected: log as INFECTED, still rebuild, receipt shows INFECTED - REBUILT. Operator decides per SOP.
* Rebuild error: block, log as REBUILD FAILED.
* No silent pass. Every file has a per-file verdict.

## Security

* Maya OS base. No extra services.
* App runs as non-root, with AppArmor.
* Temp dir wiped after each session (DoD 3-pass for dirty copy).
* Reproducible build for DGQA.

## References

* Tier 1: ARBIT EAL7+, Boeing HardwareWall, Owl XD Bridge (NCDSMO Raise-the-Bar, NATO COSMIC TOP SECRET)
* Tier 2: OPSWAT MetaDefender Kiosk (Army TSMO, Navy CSTB)
* Tier 3: Glasswall CDR (NSA Raise-the-Bar, SE Labs 100% Oct 2023)
