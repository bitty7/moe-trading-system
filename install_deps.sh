#!/bin/bash
# Quick dependency installer for EC2

set -e

echo "🐍 Installing missing Python dependencies..."

# Install dependencies from requirements.txt
cd backend
pip3 install -r requirements.txt

# Install additional dependencies that might be needed
pip3 install matplotlib seaborn fastapi uvicorn

echo "✅ Dependencies installed successfully!"

# Verify installation
echo "🔍 Verifying installations..."
python3 -c "import numpy; print('numpy:', numpy.__version__)"
python3 -c "import pandas; print('pandas:', pandas.__version__)"
python3 -c "import requests; print('requests: OK')"
python3 -c "import PIL; print('PIL: OK')"

echo "🎯 Ready to run backtest!" 