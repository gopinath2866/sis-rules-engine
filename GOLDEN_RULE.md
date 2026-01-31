# GOLDEN RULE: IRR-DEC-01

## Rule Definition
- **ID**: IRR-DEC-01
- **Title**: Deletion Protection Enabled
- **Pattern**: `deletion_protection = true`
- **Severity**: MEDIUM
- **Message**: Resource has deletion protection enabled.

## Contract (Non-Negotiable)
This rule MUST:
1. Fire when `deletion_protection = true` exists in any AWS RDS resource
2. NOT fire when `deletion_protection = false` or attribute is absent
3. Return structured JSON with correct fields
4. Exit with code 1 when violation found, 0 when clean
5. Render human-readable text output

## Canonical Test Cases
