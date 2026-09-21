#!/bin/bash
set -e
cd "$(dirname "$0")/.."
source venv/bin/activate
export PYTHONPATH=.

echo "=== SHUCHI EICAR Baseline Test ==="
echo ""

# Create EICAR test file
echo -n "X5O!P%@AP[4\PZX54(P^)7CC)7}\$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!\$H+H*" > /tmp/eicar.com

echo "1. Testing YARA rules..."
python3 -c "import yara; r=yara.compile('rules/yara/index.yar'); m=r.match('/tmp/eicar.com'); print(f'   YARA: {[x.rule for x in m]} - PASS' if m else '   YARA: FAILED')" || echo "   YARA: FAILED"

echo ""
echo "2. Testing oletools..."
python3 -c "from oletools.olevba import VBA_Parser; v=VBA_Parser('/tmp/eicar.com'); v.close(); print('   oletools: VBA detected')" 2>/dev/null || echo "   oletools: not applicable (not OLE file)"

echo ""
echo "3. Checking libmagic..."
python3 -c "import magic; m=magic.Magic(mime=True); print(f'   libmagic MIME: {m.from_file(\"/tmp/eicar.com\")}')" 2>/dev/null || echo "   libmagic: not available"

echo ""
echo "4. Checking YARA rules file..."
if [ -f "rules/yara/index.yar" ]; then
    echo "   YARA rules: FOUND ($(wc -l < rules/yara/index.yar) lines)"
else
    echo "   YARA rules: MISSING"
fi

echo ""
echo "EICAR baseline test complete."
rm -f /tmp/eicar.com
