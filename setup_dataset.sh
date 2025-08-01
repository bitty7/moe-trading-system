#!/bin/bash
# Setup Dataset for EC2
# This script unzips the HS500-samples.zip file to create the proper dataset structure

set -e

echo "📦 Setting up dataset on EC2..."

# Install unzip if not available
if ! command -v unzip &> /dev/null; then
    echo "📦 Installing unzip..."
    sudo apt-get update
    sudo apt-get install -y unzip
fi

# Check if we're in the right directory
if [ ! -f "dataset/HS500-samples.zip" ]; then
    echo "❌ HS500-samples.zip not found in dataset/ directory"
    echo "   Current directory: $(pwd)"
    echo "   Available files in dataset/:"
    ls -la dataset/ || echo "   dataset/ directory not found"
    exit 1
fi

# Remove existing HS500-samples directory if it exists
if [ -d "dataset/HS500-samples" ]; then
    echo "🗑️  Removing existing HS500-samples directory..."
    rm -rf dataset/HS500-samples
fi

# Unzip the dataset
echo "📂 Unzipping HS500-samples.zip..."
cd dataset

# Create HS500-samples directory if it doesn't exist
mkdir -p HS500-samples

# Unzip into the HS500-samples directory
unzip -q HS500-samples.zip -d HS500-samples/

# Verify the dataset structure
echo "✅ Dataset extracted successfully!"
echo "📋 Dataset structure:"
ls -la HS500-samples/

# Check for required files
echo "🔍 Verifying required data files..."
if [ -f "HS500-samples/SP500_time_series/aa.csv" ]; then
    echo "✅ Price data files found"
else
    echo "❌ Price data files missing"
fi

if [ -d "HS500-samples/SP500_images" ]; then
    echo "✅ Chart images found"
else
    echo "❌ Chart images missing"
fi

if [ -d "HS500-samples/SP500_news" ]; then
    echo "✅ News data found"
else
    echo "❌ News data missing"
fi

if [ -d "HS500-samples/SP500_tabular" ]; then
    echo "✅ Fundamental data found"
else
    echo "❌ Fundamental data missing"
fi

cd ..

echo "🎯 Dataset setup completed!"
echo "📊 Ready to run backtest with full dataset" 