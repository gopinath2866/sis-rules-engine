#!/usr/bin/env bash
# generate_full_suite.sh — POSIX-compatible, no associative arrays

set -e

VECTOR_DIR="tests/test_vectors/full_suite"
mkdir -p "$VECTOR_DIR"

echo "Generating 25 canonical test vectors..."

# List of rule IDs
RULES=(
  ADMIN-01 ADMIN-02 ADMIN-03 ADMIN-04 ADMIN-05 ADMIN-06 ADMIN-07
  IRR-DEC-01 IRR-DEC-02 IRR-DEC-03 IRR-DEC-04 IRR-DEC-05 IRR-DEC-06 IRR-DEC-07 IRR-DEC-08 IRR-DEC-09 IRR-DEC-10
  IRR-IDENT-01 IRR-IDENT-02 IRR-IDENT-03 IRR-IDENT-04 IRR-IDENT-05 IRR-IDENT-06 IRR-IDENT-07 IRR-IDENT-08
)

for RULE in "${RULES[@]}"; do
    FILE="$VECTOR_DIR/$RULE.json"
    case $RULE in
        ADMIN-*)
            cat > "$FILE" <<EOF
{"files":[{"name":"$RULE.tf","type":"terraform","content":"resource \\"aws_iam_policy\\" \\"$RULE\\" { policy = '{\"Statement\":[{\"Effect\":\"Allow\",\"Action\":\"*\",\"Resource\":\"*\"}]}' }"}]}
EOF
            ;;
        IRR-DEC-*)
            cat > "$FILE" <<EOF
{"files":[{"name":"$RULE.tf","type":"terraform","content":"resource \\"aws_s3_bucket\\" \\"$RULE\\" { lifecycle { prevent_destroy = true } }"}]}
EOF
            ;;
        IRR-IDENT-*)
            cat > "$FILE" <<EOF
{"files":[{"name":"$RULE.tf","type":"terraform","content":"resource \\"aws_iam_role\\" \\"$RULE\\" { assume_role_policy = '{\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::123456789012:role/Admin\"}}]}' }"}]}
EOF
            ;;
    esac
done

echo "Generated ${#RULES[@]} test vectors in $VECTOR_DIR"
