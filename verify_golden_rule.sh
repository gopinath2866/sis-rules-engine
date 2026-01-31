#!/bin/bash
set -e

echo "🧪 GOLDEN RULE IRR-DEC-01 VERIFICATION"
echo "======================================"
echo "Run: $(date)"
echo ""

# Test 1: Text output
echo "1. Testing scanner (text output)..."
if ./sis-scan scan test_canonical_irr_dec_01.tf 2>&1 | grep -q "IRR-DEC-01"; then
    echo "   ✅ Scanner finds IRR-DEC-01"
else
    echo "   ❌ Scanner doesn't find IRR-DEC-01"
    exit 1
fi

# Test 2: JSON output
echo "2. Testing JSON output..."
if ./sis-scan scan --format json test_canonical_irr_dec_01.tf 2>/dev/null | python3 -c "import json, sys; data=json.load(sys.stdin); exit(0 if data['summary']['total_violations'] == 1 else 1)"; then
    echo "   ✅ JSON output shows 1 violation"
else
    echo "   ❌ JSON output doesn't show expected violation"
    exit 1
fi

# Test 3: Explain command
echo "3. Testing explain command..."
if ./sis-scan explain IRR-DEC-01 2>&1 | grep -q "Rule: IRR-DEC-01"; then
    echo "   ✅ Explain command works"
else
    echo "   ❌ Explain command broken"
    exit 1
fi

# Test 4: Clean file
echo "4. Testing clean file..."
cat > /tmp/clean_golden_test.tf << 'CLEANEOF'
resource "aws_rds_cluster" "clean" {
  cluster_identifier = "clean"
  engine = "aurora"
}
CLEANEOF

if ./sis-scan scan /tmp/clean_golden_test.tf 2>&1 | grep -q "No violations"; then
    echo "   ✅ Clean file passes"
else
    echo "   ❌ Clean file shows violations"
    rm -f /tmp/clean_golden_test.tf
    exit 1
fi

rm -f /tmp/clean_golden_test.tf

# Test 5: Exit codes
echo "5. Testing exit codes..."
./sis-scan scan test_canonical_irr_dec_01.tf >/dev/null 2>&1
VIOLATION_EXIT=$?
if [ $VIOLATION_EXIT -eq 1 ]; then
    echo "   ✅ Exit code 1 on violation"
else
    echo "   ❌ Expected exit code 1 on violation, got $VIOLATION_EXIT"
    exit 1
fi

cat > /tmp/test_clean_exit.tf << 'CLEANEOF'
resource "aws_rds_cluster" "clean" {
  cluster_identifier = "clean"
  engine = "aurora"
}
CLEANEOF

./sis-scan scan /tmp/test_clean_exit.tf >/dev/null 2>&1
CLEAN_EXIT=$?
rm -f /tmp/test_clean_exit.tf

if [ $CLEAN_EXIT -eq 0 ]; then
    echo "   ✅ Exit code 0 on clean"
else
    echo "   ❌ Expected exit code 0 on clean, got $CLEAN_EXIT"
    exit 1
fi

echo ""
echo "✅ GOLDEN RULE IRR-DEC-01 VERIFIED"
echo ""
echo "All tests passed. This rule is production-ready."
