#!/bin/bash
set -e
echo "Install for Maya OS / Debian 12"
sudo apt update
sudo apt install -y git curl python3 python3-pip python3-venv \
  clamav yara libmagic1 libmagic-dev \
  qpdf exiftool \
  libreoffice-writer libreoffice-calc libreoffice-impress \
  tpm2-tools usbguard udisks2 \
  nodejs npm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
npm install
echo "Done. Run: source venv/bin/activate && npm run dev"
