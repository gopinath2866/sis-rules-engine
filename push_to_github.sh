#!/bin/bash

echo "🚀 Pushing SIS v1.0.0 to GitHub..."

# Add all changes
git add .

# Commit
git commit -m "feat: Complete SIS v1.0.0 with CI/CD pipeline"

# Rename branch to main if needed
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "Renaming branch from $current_branch to main..."
    git branch -M main
fi

# Check if remote is already set
if ! git remote | grep -q origin; then
    echo "Setting remote origin..."
    git remote add origin https://github.com/gopinath2866/sis-rules-engine.git
else
    echo "Remote origin already set."
    git remote set-url origin https://github.com/gopinath2866/sis-rules-engine.git
fi

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Successfully pushed to GitHub!"
echo "📊 Check CI status: https://github.com/gopinath2866/sis-rules-engine/actions"
echo "📚 Enable GitHub Pages: https://github.com/gopinath2866/sis-rules-engine/settings/pages"
