#!/bin/bash
# Quick script to push GATRA deployment to GitHub

echo "=========================================="
echo "GATRA Deployment - Push to GitHub"
echo "=========================================="
echo ""

# Get repository name
read -p "Enter GitHub repository name (e.g., gatra-deployment): " REPO_NAME

if [ -z "$REPO_NAME" ]; then
    echo "Error: Repository name is required"
    exit 1
fi

# Set remote
echo ""
echo "Setting up remote repository..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/ghifiardi/${REPO_NAME}.git"

echo ""
echo "Remote configured: https://github.com/ghifiardi/${REPO_NAME}.git"
echo ""

# Check if repository exists
echo "Checking if repository exists on GitHub..."
if git ls-remote --heads origin main &>/dev/null; then
    echo "✓ Repository exists, will push to main branch"
    PUSH_CMD="git push -u origin main"
else
    echo "⚠ Repository may not exist yet"
    echo ""
    echo "Please create the repository on GitHub first:"
    echo "1. Go to: https://github.com/new"
    echo "2. Repository name: ${REPO_NAME}"
    echo "3. Description: GATRA Platform Deployment Framework"
    echo "4. Choose Private or Public"
    echo "5. DO NOT initialize with README (we already have one)"
    echo ""
    read -p "Press Enter after creating the repository on GitHub..."
    PUSH_CMD="git push -u origin main"
fi

echo ""
echo "Ready to push! Executing: $PUSH_CMD"
echo ""

# Push
$PUSH_CMD

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Successfully pushed to GitHub!"
    echo "=========================================="
    echo ""
    echo "Repository URL: https://github.com/ghifiardi/${REPO_NAME}"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ Push failed"
    echo "=========================================="
    echo ""
    echo "Possible issues:"
    echo "1. Repository doesn't exist - create it on GitHub first"
    echo "2. Authentication required - you may need to:"
    echo "   - Use GitHub CLI: gh auth login"
    echo "   - Or use SSH: git remote set-url origin git@github.com:ghifiardi/${REPO_NAME}.git"
    echo "3. Check your GitHub credentials"
    echo ""
fi

