#!/bin/bash
echo "🔍 Checking possible GitHub check names..."
echo ""

echo "1. Workflow file names:"
ls .github/workflows/

echo ""
echo "2. Workflow content:"
echo "   Name from YAML:"
grep "^name:" .github/workflows/proxy-upgrade-gate.yml
echo ""
echo "   Job names (if any):"
grep -A2 "jobs:" .github/workflows/proxy-upgrade-gate.yml | tail -10

echo ""
echo "3. Based on your PR, the check is named:"
echo "   ✅ 'sis-proxy-upgrade-gate' (this is what you see)"
echo ""
echo "4. Ruleset MUST use: 'sis-proxy-upgrade-gate'"
