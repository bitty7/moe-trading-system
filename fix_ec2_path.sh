#!/bin/bash
# Fix DATA_PATH for EC2

set -e

echo "🔧 Fixing DATA_PATH for EC2..."

# Find the actual dataset location
if [ -d "dataset/HS500-samples" ]; then
    echo "✅ Found dataset at: dataset/HS500-samples"
    NEW_PATH="dataset/HS500-samples"
elif [ -d "../dataset/HS500-samples" ]; then
    echo "✅ Found dataset at: ../dataset/HS500-samples"
    NEW_PATH="../dataset/HS500-samples"
else
    echo "❌ Dataset not found in expected locations"
    echo "Searching for aa.csv..."
    find . -name "aa.csv" -type f 2>/dev/null || echo "No aa.csv found"
    exit 1
fi

# Update the .env file
echo "📝 Updating DATA_PATH in .env file..."
sed -i "s|DATA_PATH=.*|DATA_PATH=$NEW_PATH|" backend/.env

echo "✅ DATA_PATH updated to: $NEW_PATH"
echo "📋 Current DATA_PATH:"
grep DATA_PATH backend/.env

echo "🎯 Ready to run backtest!" 