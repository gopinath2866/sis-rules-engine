import sys
print("Python path:", sys.path)
try:
    import packaging
    print("✓ packaging module found")
except ImportError as e:
    print(f"✗ packaging module NOT found: {e}")

try:
    from src.sis.rules.loader import load_rules
    print("✓ Loader imported successfully")
    r = load_rules(['canonical'])
    print(f"✓ Loaded {len(r)} rules")
except Exception as e:
    print(f"✗ Error: {e}")
