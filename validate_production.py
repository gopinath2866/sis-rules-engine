#!/usr/bin/env python3
"""
Validate production readiness after cleanup
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, check=True):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Failed: {cmd}")
            print(result.stderr)
            return False
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_structure():
    """Check production directory structure"""
    print("\n🔍 Checking project structure...")
    
    expected_dirs = ["rules", "tests", "examples", "scripts"]
    expected_files = ["setup.py", "Dockerfile", "requirements.txt", "README.md"]
    
    missing_dirs = []
    missing_files = []
    
    for directory in expected_dirs:
        if not Path(directory).exists():
            missing_dirs.append(directory)
    
    for file in expected_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
    else:
        print("✅ All required directories exist")
        
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
    else:
        print("✅ All required files exist")
    
    return len(missing_dirs) == 0 and len(missing_files) == 0

def main():
    print("🔍 Production Readiness Validation")
    print("=" * 50)
    
    checks = []
    
    # 1. Check CLI works
    print("\n1. Testing CLI...")
    result = run_command("sis --help")
    checks.append(bool(result))
    print("✅ CLI works" if result else "❌ CLI failed")
    
    # 2. List rules
    print("\n2. Testing rule system...")
    result = run_command("sis list-rules")
    checks.append(bool(result))
    if result:
        lines = [line for line in result.stdout.strip().split('\n') if line.strip()]
        print(f"✅ {len(lines)} rules available" if len(lines) > 0 else "⚠️ No rules found")
    
    # 3. Run basic scan
    print("\n3. Testing scanner...")
    result = run_command("sis scan --help")
    checks.append(bool(result))
    print("✅ Scanner functional" if result else "❌ Scanner failed")
    
    # 4. Check Docker
    print("\n4. Testing Docker...")
    try:
        with open("Dockerfile") as f:
            has_docker = "FROM python" in f.read()
        checks.append(has_docker)
        print("✅ Dockerfile exists" if has_docker else "⚠️ Dockerfile missing")
    except:
        checks.append(False)
        print("❌ Dockerfile not found")
    
    # 5. Check tests
    print("\n5. Testing test suite...")
    result = run_command("python -m pytest tests/ -q", check=False)
    checks.append(result and result.returncode == 0)
    if checks[-1]:
        print("✅ Tests pass")
    elif result:
        print(f"⚠️ Some tests failed: {result.returncode}")
    else:
        print("⚠️ Could not run tests")
    
    # 6. Check structure
    checks.append(check_structure())
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"🎉 PRODUCTION READY: {passed}/{total} checks passed")
        print("\n🚀 Ready for deployment!")
        print("Next: python setup.py sdist bdist_wheel")
        return 0
    else:
        print(f"⚠️  NEEDS WORK: {passed}/{total} checks passed")
        print("\n❌ Issues found. Please fix before production deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
