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

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install \
    pandas \
    numpy \
    requests \
    pillow \
    matplotlib \
    seaborn \
    scikit-learn \
    python-dotenv \
    fastapi \
    uvicorn

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

# Set up environment
echo "🔧 Setting up environment..."
cp .env.example .env  # If you have an example env file

# Create logs directory
mkdir -p logs

# Set permissions
chmod +x run_full_backtest.sh

echo "✅ EC2 setup completed successfully!"
echo "🎯 Next steps:"
echo "   1. Run: ./run_full_backtest.sh"
echo "   2. Monitor progress in logs/"
echo "   3. Download results when complete"

# Display system info
echo "📊 System Information:"
echo "   GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits)"
echo "   Memory: $(free -h | grep Mem | awk '{print $2}')"
echo "   Storage: $(df -h / | tail -1 | awk '{print $4}') available" 