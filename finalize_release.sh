#!/bin/bash
echo "🚀 FINALIZING v1.0.0 RELEASE"
echo "============================="

# 1. Check status
echo "1. Checking git status..."
git status --short

# 2. Add any remaining files
echo ""
echo "2. Adding any remaining files..."
git add .

# 3. Commit if needed
if [ -n "$(git status --porcelain)" ]; then
    echo "Committing changes..."
    git commit -m "Final v1.0.0 release - $(date '+%Y-%m-%d')"
else
    echo "No changes to commit."
fi

# 4. Push main branch
echo ""
echo "3. Pushing main branch..."
git push origin main

# 5. Create and push tag
echo ""
echo "4. Creating v1.0.0 tag..."
git tag -f v1.0.0 -m "SIS Security Scanner v1.0.0 - Production Release"
git push origin --tags

echo ""
echo "✅ RELEASE FINALIZED!"
echo ""
echo "📦 Your v1.0.0 release is now on GitHub:"
echo "   https://github.com/gopinath2866/sis-rules-engine/releases"
echo ""
echo "🎉 Ready to launch to customers!"
