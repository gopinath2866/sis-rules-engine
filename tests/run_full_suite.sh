#!/bin/sh
# tests/run_full_suite.sh — POSIX-compatible version

TEST_DIR="tests/test_vectors/full_suite"
SIS_URL="http://localhost:8000/v1/scan"

# Collect rule files
RULE_FILES=$(ls "$TEST_DIR"/*.json 2>/dev/null)
if [ -z "$RULE_FILES" ]; then
    echo "No test vectors found in $TEST_DIR"
    exit 1
fi

# Results array
RESULTS=""
PASS_COUNT=0
FAIL_COUNT=0

echo "Running SIS full rule suite"
echo "----------------------------"

for file in $RULE_FILES; do
    RULE_NAME=$(basename "$file" .json)
    echo "Testing $RULE_NAME"

    RESPONSE=$(curl -s -X POST "$SIS_URL" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: test" \
        -d @"$file")

    TOTAL_FINDINGS=$(echo "$RESPONSE" | grep -o '"total_findings":[0-9]*' | head -1 | cut -d: -f2)

    if [ "$TOTAL_FINDINGS" = "" ]; then
        TOTAL_FINDINGS=0
    fi

    if [ "$TOTAL_FINDINGS" -gt 0 ]; then
        echo "[PASS] $RULE_NAME"
        PASS_COUNT=$((PASS_COUNT+1))
        RESULTS="$RESULTS$RULE_NAME:PASS\n"
    else
        echo "[FAIL] $RULE_NAME"
        FAIL_COUNT=$((FAIL_COUNT+1))
        RESULTS="$RESULTS$RULE_NAME:FAIL\n$RESPONSE\n"
    fi
done

echo "----------------------------"
echo "RESULT: $PASS_COUNT PASS / $FAIL_COUNT FAIL"
echo "----------------------------"
echo -e "$RESULTS"
