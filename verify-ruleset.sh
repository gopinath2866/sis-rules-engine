#!/bin/bash
echo "🔍 RULESET VERIFICATION SCRIPT"
echo "=============================="
echo ""

echo "1. Checking local SIS configuration..."
sis scan --help 2>&1 | grep -q "proxy-upgrade" && echo "   ✅ SIS has --gate proxy-upgrade" || echo "   ❌ SIS missing gate"

echo ""
echo "2. Checking workflow file..."
if [ -f ".github/workflows/proxy-upgrade-gate.yml" ]; then
    echo "   ✅ Workflow file exists"
    WF_NAME=$(grep "^name:" .github/workflows/proxy-upgrade-gate.yml | cut -d: -f2 | sed 's/^ *//')
    echo "   Workflow name: '$WF_NAME'"
else
    echo "   ❌ Missing workflow file"
fi

echo ""
echo "3. Testing SIS enforcement..."
sis scan contracts/TestProxyVulnerable.sol --gate proxy-upgrade --format json --output /tmp/verify-sis.json 2>/dev/null
SIS_EXIT=$?
if [ $SIS_EXIT -eq 1 ]; then
    echo "   ✅ SIS would block PR (exit code 1)"
    echo "   Found violations:"
    python3 -c "
import json
try:
    with open('/tmp/verify-sis.json') as f:
        data = json.load(f)
    for v in data.get('violations', []):
        print(f'     • {v[\"rule_id\"]} ({v[\"severity\"]})')
except:
    print('     (Could not parse JSON)')
" 2>/dev/null
else
    echo "   ⚠️  SIS exit code: $SIS_EXIT"
fi

echo ""
echo "4. Ruleset status check:"
echo "   Go to your PR and look for:"
echo "   - 'Merge blocked by branch protection'"
echo "   - 'Required status checks' section"
echo "   - List of required checks"
echo ""
echo "5. If ruleset is active, you should see on PR:"
echo "   ❌ Merge button disabled/grayed out"
echo "   📋 '1 approving review required'"
echo "   🤖 Status check requirement listed"
echo ""
echo "🎯 NEEDED FROM YOU:"
echo "1. What do you see on the PR page now?"
echo "2. Is the merge button enabled or disabled?"
echo "3. What messages appear near the merge button?"
