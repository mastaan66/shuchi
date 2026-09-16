#!/bin/bash
set -e
# EICAR baseline test — must be flagged
EICAR='X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
echo -n "$EICAR" > /tmp/eicar.com
echo "Testing with ClamAV..."
clamscan /tmp/eicar.com || true
echo "Testing with YARA..."
yara rules/yara/index.yar /tmp/eicar.com || true
echo "If both flagged EICAR, rig is correct."
rm /tmp/eicar.com
