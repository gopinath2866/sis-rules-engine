#!/bin/bash
set -e

echo "=== Migrating SIS to pack-based rule system ==="

# Create necessary directories
mkdir -p ~/.sis/rules
mkdir -p ~/.sis/licenses

# Check if old rules exist
if [ -f "rules/canonical.json" ]; then
    echo "Found legacy rules/canonical.json"
    
    # Create canonical pack directory
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
    "min": "0.1.0",
    "max": "999.999.999"
  },
  "rules_files": ["rules.json"]
}
METADATA_EOF
    
    echo "✓ Migrated canonical rules to pack format"
    echo "  Location: ~/.sis/rules/canonical/"
else
    echo "No legacy rules found to migrate"
fi

# Check for DeFi pack
if [ -d "../defi-safety-pack" ]; then
    echo "Found DeFi safety pack"
    
    # Create defi-irreversibility pack
    mkdir -p ~/.sis/rules/defi-irreversibility
    
    # Copy all JSON files
    find ../defi-safety-pack -name "*.json" -exec cp {} ~/.sis/rules/defi-irreversibility/ \;
    
    # Create metadata
    cat > ~/.sis/rules/defi-irreversibility/metadata.json << DEFI_METADATA_EOF
{
  "pack_id": "defi-irreversibility",
  "version": "1.0.0",
  "name": "DeFi Irreversibility Rules",
  "description": "Rules for detecting irreversible DeFi protocol configurations",
  "license_required": "pro",
  "engine_compatibility": {
    "min": "1.0.0",
    "max": "999.999.999"
  },
  "rules_files": ["core-irreversibility.json", "economic-irreversibility.json", "governance-irreversibility.json"]
}
DEFI_METADATA_EOF
    
    echo "✓ Migrated DeFi safety pack"
    echo "  Location: ~/.sis/rules/defi-irreversibility/"
    echo "  Note: This pack requires a Pro license"
fi

echo -e "\n=== Migration complete ==="
echo "Available packs:"
ls -la ~/.sis/rules/
echo -e "\nTo use the new pack system:"
echo "1. Run: sis scan --packs canonical <target>"
echo "2. For Pro packs, you'll need a license in ~/.sis/licenses/"
