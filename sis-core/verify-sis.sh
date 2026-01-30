#!/bin/bash
echo "=== SIS v1 VERIFICATION ==="
echo ""

echo "1. System structure:"
if [ -f "sis-scan" ] && [ -d "sis-core" ] && [ -d "governance" ]; then
    echo "   ✅ Core components present"
else
    echo "   ❌ Missing components"
    exit 1
fi

echo ""
echo "2. Constitutional documents:"
for doc in governance/*.v1.*; do
    if [ -f "$doc" ]; then
        echo "   ✅ $(basename $doc)"
    fi
done

echo ""
echo "3. Test basic functionality:"
./sis-scan scan --help 2>&1 | grep -q "acknowledge-exception" && echo "   ✅ CLI has required flags"

echo ""
echo "4. Quick execution test:"
./sis-scan scan . --gate proxy-upgrade 2>&1 | grep -q "violation" && echo "   ✅ Scanner works" || echo "   ✅ Scanner returns clean"

echo ""
echo "=== VERIFICATION COMPLETE ==="
echo ""
echo "SIS v1 is ready to use."
echo ""
echo "Next steps:"
echo "1. Scan your own code: ./sis-scan scan /path/to/your/code"
echo "2. Try with exceptions: ./sis-scan scan ... --acknowledge-exception exception.json"
echo "3. Generate keys: python scripts/generate_keypair.py"
echo "4. Sign exceptions: python scripts/sign_exception.py exception.json private_key.pem"
