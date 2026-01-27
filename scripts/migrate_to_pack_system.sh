#!/bin/bash
set -e

echo "================================================================"
echo "SIS Rule Pack System Migration"
echo "================================================================"
echo ""
echo "This script migrates from the old single rules file to the new"
echo "pack-based system. Your existing rules will be preserved."
echo ""

# Check if we need to migrate
if [ -f "rules/canonical.json" ]; then
    echo "📦 Found legacy rules/canonical.json"
    echo ""
    
    # Create pack directory
    mkdir -p ~/.sis/rules/canonical
    
    # Copy rules
    cp rules/canonical.json ~/.sis/rules/canonical/rules.json
    
    # Create metadata
    cat > ~/.sis/rules/canonical/metadata.json << METADATA_EOF
{
  "pack_id": "canonical",
  "version": "1.0.0",
  "name": "Canonical Rules",
  "description": "Default security rules migrated from legacy format",
  "license_required": "free",
  "engine_compatibility": {
    "min": "1.0.0",
    "max": "999.999.999"
  },
  "rules_files": ["rules.json"]
}
METADATA_EOF
    
    echo "✅ Successfully migrated to pack system!"
    echo ""
    echo "New location: ~/.sis/rules/canonical/"
    echo "Contents:"
    ls -la ~/.sis/rules/canonical/
    echo ""
else
    echo "✅ No legacy rules found - you're already on the pack system!"
    echo ""
fi

echo "================================================================"
echo "Usage Examples:"
echo "================================================================"
echo ""
echo "Scan with canonical pack:"
echo "  sis scan --packs canonical ./terraform/"
echo ""
echo "List rules from canonical pack:"
echo "  sis rules --packs canonical"
echo ""
echo "Scan with all available packs (free tier):"
echo "  sis scan ./terraform/"
echo ""
echo "================================================================"
echo "Pack System Features:"
echo "================================================================"
echo "• Modular rule packs (canonical, defi-irreversibility, etc.)"
echo "• Versioned packs with compatibility checking"
echo "• License tiers (free/pro/enterprise)"
echo "• Multiple pack sources (user, env, built-in)"
echo "• Pack attribution in all findings"
echo ""

# Test the migration
echo "Testing migration..."
if python -c "from src.sis.rules.loader import load_rules; r=load_rules(['canonical']); print(f'Loaded {len(r)} rules')" 2>/dev/null; then
    echo "✅ Migration test passed!"
else
    echo "⚠️  Migration test failed - check for errors above"
fi
