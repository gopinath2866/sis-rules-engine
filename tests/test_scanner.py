import src.sis.scanner as scanner_module
print("Scanner module attributes:")
for attr in dir(scanner_module):
    if not attr.startswith('_'):
        print(f"  {attr}")

# Try to import Scanner
try:
    from src.sis.scanner import Scanner
    print("\n✓ Scanner class imported successfully")
except ImportError as e:
    print(f"\n✗ Error importing Scanner: {e}")
    
# Try to create scanner instance
try:
    scanner = scanner_module.Scanner()
    print("✓ Scanner instance created")
except Exception as e:
    print(f"✗ Error creating scanner: {e}")
    
# Check if there's a scan function
if hasattr(scanner_module, 'scan'):
    print("✓ scan function exists")
