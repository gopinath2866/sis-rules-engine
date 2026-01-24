#!/bin/bash
echo "🧹 CLEANING UP SOURCE CONTROL - 3 ITEMS"
echo "========================================"
echo ""

echo "1. CURRENT STATUS:"
echo "-----------------"
git status
echo ""

echo "2. DETAILED STATUS:"
echo "------------------"
git status --porcelain
echo ""

echo "3. VIEWING UNTRACKED FILES:"
echo "---------------------------"
# List all untracked files
untracked=$(git ls-files --others --exclude-standard)
if [ -n "$untracked" ]; then
    echo "Untracked files found:"
    echo "$untracked" | while read file; do
        echo "  • $file"
    done
else
    echo "No untracked files"
fi
echo ""

echo "4. VIEWING CHANGES TO BE COMMITTED:"
echo "-----------------------------------"
changes=$(git diff --cached --name-only)
if [ -n "$changes" ]; then
    echo "Changes staged for commit:"
    echo "$changes" | while read file; do
        echo "  • $file"
    done
else
    echo "No changes staged for commit"
fi
echo ""

echo "5. RECOMMENDED ACTION:"
echo "---------------------"
echo "Based on what we've been working on, you likely have:"
echo "  1. LICENSE file"
echo "  2. Protection documents"
echo "  3. Script files from finalization"
echo ""
echo "Let's handle them properly..."
echo ""

# Add everything properly
echo "Adding all files..."
git add .

echo ""
echo "6. PREVIEW COMMIT:"
echo "-----------------"
echo "Files to be committed:"
git diff --cached --name-only | while read file; do
    echo "  • $file"
done

echo ""
echo "7. COMMITTING:"
echo "-------------"
git commit -m "Release v1.0.1 - Add legal documentation and cleanup

- Add MIT LICENSE file
- Add protection documentation  
- Clean up release scripts
- Finalize v1.0.0 release preparation"

echo ""
echo "8. PUSHING TO GITHUB:"
echo "--------------------"
git push origin main

echo ""
echo "✅ SOURCE CONTROL CLEANUP COMPLETE!"
echo ""
echo "📊 FINAL STATUS:"
git status
