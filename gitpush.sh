#!/bin/bash

# git-push.sh
# Usage: ./git-push.sh "your commit message"

# Exit immediately if a command fails
set -e

# Check if a commit message was provided
if [ -z "$1" ]; then
  echo "❌ No commit message provided."
  echo "Usage: $0 \"your commit message\""
  exit 1
fi

# Stage all changes
git add .

# Commit with the provided message
git commit -m "$1"

# Push to the current branch
git push origin "$(git rev-parse --abbrev-ref HEAD)"

echo "✅ Changes pushed successfully!"
