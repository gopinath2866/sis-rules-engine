#!/usr/bin/env python3
"""
Production Cleanup Script for sis-v1 - FIXED VERSION
Removes debug files, organizes rules, and creates production structure
"""

import os
import shutil
import sys
from pathlib import Path

class ProductionCleanup:
    def __init__(self, project_root="."):
        self.root = Path(project_root)
        self.backup_dir = None
        
    def get_debug_files(self):
        """Return list of debug/test files to remove/archive"""
        patterns = [
            "debug_*.py",
            "test_*.py",
            "check_*.py",
            "trace_*.py",
            "*_test.py",
            "view_*.py",
            "inspect_*.py",
            "*.sh.save",
            "temp_*",
            "tmp_*"
        ]
        
        debug_files = []
        for pattern in patterns:
            for file in self.root.glob(pattern):
                if file.is_file() and file != Path(__file__):
                    debug_files.append(file)
        
        return debug_files
    
    def get_temp_directories(self):
        """Return temporary directories to remove (excluding backup dir)"""
        temp_dir_patterns = [
            "rules_original",
            "rules_with_issues", 
            "rules_disabled",
            "clean_rules",
            "clean_test",
            "clean_test_2",
            "minimal_test",
            "htmlcov",
            "reports",
            "test-results",
            "temp_*",
            "tmp_*"
        ]
        
        temp_dirs = []
        for pattern in temp_dir_patterns:
            for dir_path in self.root.glob(pattern):
                if dir_path.is_dir() and dir_path != self.backup_dir:
                    temp_dirs.append(dir_path)
        
        return temp_dirs
    
    def cleanup(self, backup=True):
        """Main cleanup procedure"""
        print("🚀 Starting Production Cleanup")
        print("=" * 50)
        
        # Set backup directory
        if backup:
            self.backup_dir = self.root / "backup_debug_files"
            self.backup_dir.mkdir(exist_ok=True)
            print(f"📦 Backup directory: {self.backup_dir}")
        
        # 1. Remove debug files
        debug_files = self.get_debug_files()
        print(f"\n📁 Found {len(debug_files)} debug files")
        
        for file in debug_files:
            if backup and self.backup_dir:
                try:
                    shutil.move(str(file), str(self.backup_dir / file.name))
                    print(f"  📦 Backed up: {file.name}")
                except Exception as e:
                    print(f"  ⚠️  Couldn't backup {file.name}: {e}")
                    try:
                        file.unlink()
                        print(f"  🗑️  Removed: {file.name}")
                    except Exception as e2:
                        print(f"  ❌ Couldn't remove {file.name}: {e2}")
            else:
                try:
                    file.unlink()
                    print(f"  🗑️  Removed: {file.name}")
                except Exception as e:
                    print(f"  ❌ Couldn't remove {file.name}: {e}")
        
        # 2. Remove temporary directories (excluding backup dir)
        temp_dirs = self.get_temp_directories()
        print(f"\n📁 Found {len(temp_dirs)} temporary directories")
        
        for directory in temp_dirs:
            if backup and self.backup_dir:
                try:
                    # Create a subdirectory in backup for this directory's contents
                    dir_backup_path = self.backup_dir / f"DIR_{directory.name}"
                    if directory.exists():
                        shutil.move(str(directory), str(dir_backup_path))
                        print(f"  📦 Backed up directory: {directory.name}")
                except Exception as e:
                    print(f"  ⚠️  Couldn't backup directory {directory.name}: {e}")
                    try:
                        shutil.rmtree(directory, ignore_errors=True)
                        print(f"  🗑️  Removed directory: {directory.name}")
                    except Exception as e2:
                        print(f"  ❌ Couldn't remove directory {directory.name}: {e2}")
            else:
                try:
                    shutil.rmtree(directory, ignore_errors=True)
                    print(f"  🗑️  Removed directory: {directory.name}")
                except Exception as e:
                    print(f"  ❌ Couldn't remove directory {directory.name}: {e}")
        
        # 3. Organize rules (keep only canonical)
        print(f"\n📋 Organizing rules directory...")
        rules_dir = self.root / "rules"
        if rules_dir.exists():
            # Create canonical rules backup
            canonical_dir = rules_dir / "canonical"
            if canonical_dir.exists():
                canonical_backup = self.root / "rules_canonical_backup"
                try:
                    if canonical_backup.exists():
                        shutil.rmtree(canonical_backup)
                    shutil.copytree(canonical_dir, canonical_backup)
                    print(f"  ✅ Backed up canonical rules to: {canonical_backup}")
                except Exception as e:
                    print(f"  ⚠️  Couldn't backup canonical rules: {e}")
        
        # 4. Remove temporary shell scripts (keep production ones)
        shell_scripts = list(self.root.glob("*.sh"))
        production_scripts = {"sis-helper.sh", "setup.sh", "install.sh", "build.sh"}
        
        for script in shell_scripts:
            if script.name not in production_scripts and script.is_file():
                if backup and self.backup_dir:
                    try:
                        shutil.move(str(script), str(self.backup_dir / script.name))
                        print(f"  📦 Backed up script: {script.name}")
                    except Exception as e:
                        print(f"  ⚠️  Couldn't backup script {script.name}: {e}")
                        try:
                            script.unlink()
                            print(f"  🗑️  Removed script: {script.name}")
                        except Exception as e2:
                            print(f"  ❌ Couldn't remove script {script.name}: {e2}")
                else:
                    try:
                        script.unlink()
                        print(f"  🗑️  Removed script: {script.name}")
                    except Exception as e:
                        print(f"  ❌ Couldn't remove script {script.name}: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Cleanup Complete!")
        
        if backup and self.backup_dir and self.backup_dir.exists():
            print(f"\n⚠️  IMPORTANT: Review backup in '{self.backup_dir}'")
            print("   Delete it after confirming everything works:")
            print(f"   rm -rf {self.backup_dir}")
        
        return len(debug_files) + len(temp_dirs)
    
    def create_production_structure(self):
        """Create clean production directory structure"""
        print("\n🏗️ Creating Production Structure")
        print("=" * 50)
        
        structure = {
            "rules": [
                "canonical/",
                "defi-safety/",
                "premium/",
                "__init__.py",
                "README.md"
            ],
            "tests": [
                "__init__.py",
                "conftest.py"
            ],
            "examples": [
                "terraform/",
                "outputs/",
                "README.md"
            ],
            "scripts": [
                "__init__.py",
                "run_canonical_suite.py"
            ],
            "docs": [
                "api/",
                "rules/",
                "deployment.md"
            ]
        }
        
        for directory, contents in structure.items():
            dir_path = self.root / directory
            dir_path.mkdir(exist_ok=True)
            print(f"📁 Created/verified: {directory}/")
            
            # Create placeholder files
            for item in contents:
                if item.endswith("/"):
                    subdir = dir_path / item[:-1]
                    subdir.mkdir(exist_ok=True)
                elif not (dir_path / item).exists():
                    file_path = dir_path / item
                    if item.endswith(".md"):
                        file_path.write_text(f"# {item[:-3]}\n\nDocumentation coming soon.\n")
                    elif item.endswith(".py"):
                        file_path.write_text(f'"""\n{item}\n"""\n\n')
                    else:
                        file_path.touch()
        
        print("=" * 50)
        print("✅ Production structure created!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cleanup sis-v1 for production")
    parser.add_argument("--no-backup", action="store_true", help="Delete files instead of backing up")
    parser.add_argument("--create-structure", action="store_true", help="Create production directory structure")
    
    args = parser.parse_args()
    
    cleaner = ProductionCleanup()
    
    # Run cleanup
    try:
        cleaned = cleaner.cleanup(backup=not args.no_backup)
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        print("Trying to continue with structure creation...")
        cleaned = 0
    
    # Create structure if requested
    if args.create_structure:
        try:
            cleaner.create_production_structure()
        except Exception as e:
            print(f"\n❌ Structure creation failed: {e}")
    
    print(f"\n🎯 Next steps:")
    print("1. Run test suite: python -m pytest tests/ -v")
    print("2. Test scanner: sis scan --help")
    print("3. Update .gitignore with:")
    print("   # Debug files")
    print("   debug_*.py")
    print("   test_*.py")
    print("   *.sh.save")
    print("   # Temporary directories")
    print("   rules_*/")
    print("   clean_*/")
    print("   temp_*/")
    sys.exit(0 if cleaned > 0 else 1)
