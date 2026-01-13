#!/bin/bash

# Simple Git push script
# Usage: ./gitpush.sh "commit message"

# Exit if no commit message is provided
if [ -z "$1" ]; then
  echo "❌ Commit message required!"
  echo "Usage: ./gitpush.sh \"your commit message\""
  exit 1
fi

# Stage all changes
git add .

# Commit with the provided message
git commit -m "$1"

# Push to the default remote (origin) and branch (main/master)
git push origin $(git rev-parse --abbrev-ref HEAD)
