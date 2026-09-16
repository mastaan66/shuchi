# SHUCHI — Sanitiser Hub for Clean Information

**Advanced Open-Source Framework Sanitisation Tool for Multiple Air-Gapped Networks**

Maya OS native. Fully offline. DGQA auditable.

Author: Sk Mastan, Independent Contributor, Hyderabad — mastaanshaik37@gmail.com — github.com/mastaan66

Status: Work in progress. Building demo as per 15-day plan. Seeking T-Hub guidance for DGQA and user trial. For iDEX Open Challenge 19.

---

## 1. What problem it solves

Defence networks run on Maya OS on air-gapped MoDNet with Chakra. Files still move on USB drives. Each drive that crosses the gap bypasses all network safety. This is the most common SOP gap and the main way malware enters.

Precedent: In 2008, one USB worm (Agent.btz) infected US SIPRNet and JWICS. It took 14 months to fix (Operation Buckshot Yankee) and led to the creation of US Cyber Command.

Demand is proven and tri-service. This maps to Navy Challenge No. 5 and IAF Challenge No. 10. The same title was funded on 23 Mar 2026 to Matisoft Cyber Security Labs Pvt Ltd by TDB/DST (PIB 2243913) as a 7-module DLP + EDR + CDR suite. That validates the need. Matisoft is a heavy enterprise suite for central control. SHUCHI is the complementary edge kiosk for forward rooms.

Existing options do not fit forward units. Tier 1 data diodes and CDS (Boeing HardwareWall, Owl XD Bridge, ARBIT EAL7+ for NATO COSMIC TOP SECRET, USD 50k to 500k, NCDSMO Raise-the-Bar) are for strategic links. Tier 2 kiosks (OPSWAT MetaDefender Kiosk, 30+ engines, Deep CDR 200+ formats, Army TSMO and Navy CSTB evaluated) are closed-source and need the cloud. Tier 3 deterministic CDR (Glasswall, NATO/Five Eyes/AUKUS, NSA Raise-the-Bar top-rated, SE Labs 100% Oct 2023) is also import and Windows-centric. None is light, Maya-native, and fully offline for every room.

## 2. What SHUCHI does

A small kiosk placed at the gap. The dirty USB never touches the clean side. Only a rebuilt clean copy crosses.

```
Dirty USB (write-blocked, read-only)
  -> Check true file type (libmagic)
  -> Scan offline (ClamAV + YARA 300 + oletools)
  -> Make clean copy (deterministic CDR)
  -> Air gap
  -> Clean USB + signed receipt
  -> Wipe dirty drive
```

Four steps for each file:

1. **Intake.** USBGuard blocks writing. Drive is mounted read-only. True type is checked with libmagic to catch wrong extensions and polyglot files. If type is not supported or check fails, file is blocked and logged, not transferred.

2. **Scan.** Offline scan with ClamAV (offline signatures), YARA (300 rules), and oletools with mraptor for macros in Office files. No internet is used. Result is logged per file. Update is via monthly signed offline pack on a clean USB.

3. **Rebuild.** A new clean file is made from scratch. The file is opened and saved again as a new file using qpdf for PDFs, exiftool for metadata, Pillow for images, and LibreOffice headless for Office files, as per ISO 32000 and OOXML. Only content is kept. Hidden code, scripts, and exploits are left behind. Checking can miss, remaking removes. Hindi and Office formatting is kept as is.

4. **Handover.** Clean file is given on a clean USB with a signed receipt. Receipt is signed by TPM 2.0 and stored in a hash-chain WORM log that cannot be changed. After handover, the dirty drive is fully wiped with a DoD 3-pass wipe. Each file gets a per-file verdict on the receipt.

## 3. Stack

| Part | Tools |
|------|-------|
| Platform | Maya OS, Electron + Python, N100 mini-PC with TPM 2.0, receipt printer |
| Intake | USBGuard, udisks read-only mount, libmagic |
| Scan | ClamAV offline, YARA 300, oletools (olevba, msodde, mraptor) |
| Rebuild (CDR) | qpdf, exiftool, Pillow, LibreOffice headless |
| Trust | tpm2-tools (TPM 2.0 quote), hash-chain WORM log, PDF receipt |

All parts are open-source (GPL/MIT) and can be checked by DGQA. Build can be made again for audit. No hidden binary. No cloud. No licence fee.

## 4. How it is different

| Point | Imports / Matisoft | SHUCHI |
|-------|-------------------|--------|
| Where it is used | Heavy SOC suite for central control | Light kiosk for any room |
| Can it be checked | No, closed | Yes, full code open |
| Maya OS / Internet | No / Needs cloud | Yes / No internet needed |
| Record | Can be edited | Cannot be changed (TPM + hash chain) |
| Cost per unit | Rs. 12 to 15 lakh + yearly fee | Rs. 35,000 |

5000+ need estimated (2 to 3 per establishment). SHUCHI is for the edge; Matisoft is for central policy. They complement.

## 5. Repo layout

```
shuchi/
  README.md           — this file
  ARCHITECTURE.md     — pipeline, threat model, and air-gap design
  BUILD.md            — how to build on Maya OS
  TESTING.md          — 130-file corpus and test steps
  ROADMAP.md          — 15-day demo and 180-day pilot
  LICENSE             — GPL-3.0
  src/
    pipeline/         — verify, detect, rebuild
    cdr/              — qpdf, exiftool, Pillow, LibreOffice wrappers
    audit/            — TPM quote, WORM log, PDF receipt
    ui/               — Electron UI
  rules/yara/         — 300 YARA rules
  scripts/            — install and test scripts
  tests/corpus/       — 130 files (clean, infected, malformed, Hindi)
  hardware/           — N100 + TPM + printer wiring
  docs/               — DGQA audit notes, SOP
```

## 6. Build

See `BUILD.md`. Summary for Maya OS:

```bash
git clone https://github.com/mastaan66/shuchi
cd shuchi
./scripts/install_maya.sh
pip install -r requirements.txt
npm install
npm run dev
```

Hardware for demo: N100 mini-PC with TPM 2.0, 8GB RAM, 256GB SSD, USBGuard, receipt printer (USB). Total about Rs. 35,000.

## 7. Test

See `TESTING.md`. Corpus is 130 files: 40 clean (including 10 Hindi Office files), 30 infected (EICAR and macro samples), 30 malformed (polyglot, wrong extension), 30 mixed. Target is no silent failure and correct Hindi preservation. EICAR is used for baseline.

```bash
./scripts/eicar_test.sh
python -m tests.run_corpus
```

## 8. Plan

**We are building the demo as per a 15-day plan and will complete by 28 September with guidance.**

| Phase | What | When |
|-------|------|------|
| D1 to D2 | Rig and test — Maya VM, USBGuard, EICAR | Day 1 to 2 |
| D3 to D6 | Core build — 5 file types (PDF, DOCX, XLSX, PPTX, image) | Day 3 to 6 |
| D7 to D9 | Log and screen — TPM log, Electron UI, Hindi check | Day 7 to 9 |
| D10 to D11 | Corpus test — 130 files, video | Day 10 to 11 |
| D12 to D15 | Paper and video — 2-page paper and 2-minute video by 28 Sep | Day 12 to 15 |

Post-grant, 180 days to 10-kiosk trial:

M1 design 30 days (10%), M2 15 types 60 days (20%), M3 hardening 90 days (20%), M4 trials at one Navy and one IAF unit 120 days (25%), M5 DGQA papers 150 days (15%), M6 trial of 10 units 180 days (10%). Budget is hardware 10%, people 60%, testing 20%.

## 9. DGQA and audit

* All code is GPL-3.0 and can be checked.
* Build can be made again. No hidden binary.
* TPM 2.0 quote and hash-chain log provide a record that cannot be changed.
* Monthly signed offline pack updates signatures without internet.

Seeking T-Hub guidance for DGQA and user trial.

## 10. Contact

Sk Mastan, Independent Contributor, Hyderabad, Telangana — +91-7075439928 — mastaanshaik37@gmail.com — github.com/mastaan66

For iDEX Open Challenge 19. Work in progress.
