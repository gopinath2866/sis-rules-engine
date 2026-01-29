#!/bin/bash
# SIS Helper Script to manage rule directories

RULES_DIR="./rules"
BACKUP_DIR="./rules_backup"

case "$1" in
    "use-canonical-only")
        mkdir -p "$BACKUP_DIR"
        mv "$RULES_DIR" "$BACKUP_DIR/rules_all"
        mkdir -p "$RULES_DIR"
        cp -r "$BACKUP_DIR/rules_all/canonical" "$RULES_DIR/"
        echo "✓ Using canonical rules only"
        ;;
    "use-all-except-test")
        mkdir -p "$BACKUP_DIR"
        mv "$RULES_DIR" "$BACKUP_DIR/rules_all"
        mkdir -p "$RULES_DIR"
        cp -r "$BACKUP_DIR/rules_all/canonical" "$RULES_DIR/"
        cp -r "$BACKUP_DIR/rules_all/defi-safety" "$RULES_DIR/" 2>/dev/null || true
        cp -r "$BACKUP_DIR/rules_all/defi-irreversibility" "$RULES_DIR/" 2>/dev/null || true
        cp -r "$BACKUP_DIR/rules_all/premium" "$RULES_DIR/" 2>/dev/null || true
        echo "✓ Using all rules except test/built-in/enhanced"
        ;;
    "restore-all")
        if [ -d "$BACKUP_DIR/rules_all" ]; then
            rm -rf "$RULES_DIR"
            mv "$BACKUP_DIR/rules_all" "$RULES_DIR"
            echo "✓ Restored all rules"
        else
            echo "✗ No backup found"
        fi
        ;;
    "list-rules-count")
        echo "Current rules directory:"
        for dir in "$RULES_DIR"/*/; do
            if [ -d "$dir" ]; then
                count=$(find "$dir" -name "*.json" -exec python3 -c "
import json, sys
try:
    with open(sys.argv[1]) as f:
        data = json.load(f)
        print(len(data) if isinstance(data, list) else 1)
except:
    print('0')
" {} \; 2>/dev/null | awk '{sum+=$1} END {print sum}')
                echo "  $(basename "$dir"): $count rules"
            fi
        done
        ;;
    *)
        echo "Usage: $0 {use-canonical-only|use-all-except-test|restore-all|list-rules-count}"
        ;;
esac
