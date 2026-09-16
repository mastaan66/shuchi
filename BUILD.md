# Build — SHUCHI on Maya OS

This is for Maya OS. Also works on Debian 12 and Ubuntu 22.04 for dev.

We are building the demo as per the 15-day plan. This doc is the build steps.

## Hardware

* N100 mini-PC with TPM 2.0 (e.g., Beelink EQ12 or similar), 8GB RAM, 256GB SSD
* USBGuard capable board
* USB thermal receipt printer (USB, ESC/POS)
* Two USB drives for test: one dirty, one clean

Cost about Rs. 35,000.

## Base install on Maya OS

```bash
sudo apt update
sudo apt install -y git curl python3 python3-pip python3-venv \
  clamav clamav-freshclam \
  yara libmagic1 libmagic-dev \
  qpdf exiftool \
  libreoffice-writer libreoffice-calc libreoffice-impress \
  tpm2-tools usbguard udisks2 \
  nodejs npm

# Python deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node deps for UI
npm install
```

## Python deps (requirements.txt)

```
oletools
yara-python
pillow
python-magic
```

See `requirements.txt`.

## YARA rules

Rules are in `rules/yara/`. 300 rules compiled.

```bash
yara -r rules/yara/index.yar tests/samples/eicar.com
```

Update via signed offline pack:

```bash
./scripts/update_offline_pack.sh /media/clean/update-2026-09.tar.gz
```

## ClamAV offline

Do not use freshclam on kiosk.

On a connected build machine:

```bash
freshclam
cp /var/lib/clamav/*.cvd ./offline/
```

Copy to kiosk via clean USB:

```bash
sudo cp offline/*.cvd /var/lib/clamav/
sudo chown clamav:clamav /var/lib/clamav/*.cvd
clamscan --version
```

Verify with EICAR:

```bash
./scripts/eicar_test.sh
```

## USBGuard and mount

Dirty port is set read-only.

```bash
sudo usbguard generate-policy > /etc/usbguard/rules.conf
sudo systemctl enable --now usbguard

# Check dirty port is blocked for write
sudo usbguard list-devices
```

App mounts dirty drive as:

```bash
udisksctl mount -o ro -p /org/freedesktop/UDisks2/block_devices/sdb1
```

## TPM 2.0

Check TPM:

```bash
tpm2_getcap properties-fixed
tpm2_quote --help
```

Log is in `/var/log/shuchi/worm.log`.

## Run

```bash
# dev
source venv/bin/activate
npm run dev

# or CLI
python src/pipeline/main.py --dirty /media/dirty --clean /media/clean
```

UI is Electron. It shows file list, type, scan result, rebuild status, and print receipt.

## Build for DGQA

Reproducible build:

```bash
npm run build
python -m pip freeze > build/freeze.txt
sha256sum dist/* > build/SHA256SUMS
```

All code is GPL-3.0. No hidden binary.

## Maya OS test

We are testing on Maya OS VM and on N100 hardware. Day 1 to 2 of the 15-day plan is rig and EICAR test.

If Maya OS is not available, test on Debian 12 — same packages.
