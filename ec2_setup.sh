#!/bin/bash
# EC2 Setup Script for MoE Trading System
# This script sets up an EC2 instance with GPU support for running full backtests

set -e  # Exit on any error

echo "🚀 Starting EC2 setup for MoE Trading System..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install essential packages
echo "📦 Installing essential packages..."
sudo apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    python3-dev \
    nvidia-cuda-toolkit \
    nvidia-driver-535

# Note: Python dependencies will be installed in virtual environment later

# Install Ollama
echo "🤖 Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
echo "🚀 Starting Ollama service..."
sudo systemctl enable ollama
sudo systemctl start ollama

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
sleep 10

# Pull required models (GPU optimized for speed)
echo "📥 Pulling LLM models..."
ollama pull llama3.1:8b  # Fastest model for speed
# Skip 70b model to save time and memory

# Verify GPU support
echo "🔍 Verifying GPU support..."
nvidia-smi
ollama list

# Clone the repository
echo "📁 Cloning repository..."
cd /home/ubuntu
git clone https://github.com/bitty7/moe-trading-system.git
cd moe-trading-system

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip in venv
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies from requirements.txt
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p backend/logs

# Setup dataset (unzip HS500-samples.zip)
echo "📦 Setting up dataset..."
chmod +x setup_dataset.sh
./setup_dataset.sh

# Display system info
echo "📊 System Information:"
echo "   GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits)"
echo "   Memory: $(free -h | grep Mem | awk '{print $2}')"
echo "   Storage: $(df -h / | tail -1 | awk '{print $4}') available"

echo "✅ EC2 setup completed successfully!"
echo ""
echo "="*70
echo "🚀 STARTING FULL HISTORICAL BACKTEST (2000-2025)"
echo "="*70

# Set environment variables for GPU acceleration
export OLLAMA_HOST=0.0.0.0:11434
export CUDA_VISIBLE_DEVICES=0

# Run smoke test first to verify everything works
echo "🧪 Running smoke test first..."
cd backend

# Ensure venv is activated
source ../venv/bin/activate

python run_backtest.py --config config_smoke_test.json

if [ $? -eq 0 ]; then
    echo "✅ Smoke test passed! System is working."
    echo ""
    echo "🚀 Starting full historical backtest (2000-2025, ~25 years)..."
    echo "   This will take 3-5 hours. Running in background with nohup..."
    echo ""
    
    # Run full historical backtest in background (with venv activated)
    nohup ../venv/bin/python run_backtest.py --config config_full_historical.json > ../full_backtest.log 2>&1 &
    
    # Save process ID
    echo $! > ../backtest.pid
    
    echo "✅ Backtest started in background!"
    echo "   Process ID: $(cat ../backtest.pid)"
    echo ""
    echo "📊 To monitor progress:"
    echo "   tail -f ~/moe-trading-system/full_backtest.log"
    echo ""
    echo "📊 To check GPU usage:"
    echo "   watch -n 5 nvidia-smi"
    echo ""
    echo "📊 To check if still running:"
    echo "   ps aux | grep \$(cat ~/moe-trading-system/backtest.pid)"
    echo ""
    echo "⏰ Estimated completion: 3-5 hours"
    echo "💰 Estimated cost: ~\$2.50 (g4dn.xlarge)"
else
    echo "❌ Smoke test failed! Please check the logs."
    exit 1
fi 