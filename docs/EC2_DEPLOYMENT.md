# 🚀 EC2 Deployment Guide for High-Performance Backtesting

This guide will help you deploy the MoE trading system on AWS EC2 for running full 25-year backtests efficiently.

## 📊 Performance Analysis

### Dataset Size
- **Time Period**: 2000-01-03 to 2025-03-28 (~25 years)
- **Trading Days**: ~19,047 days across 3 tickers
- **LLM Requests**: ~57,141 (3 experts × 19,047 days)
- **Data Size**: ~1.3MB (price data) + ~50MB (news/fundamentals/charts)

### Performance Estimates
Based on optimized code with minimal logging:
- **Processing Rate**: ~2-5 days/second (depending on instance)
- **Estimated Time**: 1-3 hours for full dataset
- **Cost**: $4-12 for complete backtest

## 🏗️ EC2 Instance Recommendations

### Option 1: g4dn.12xlarge (Recommended)
- **GPU**: 4x NVIDIA T4 GPUs
- **CPU**: 48 vCPUs (Intel Xeon)
- **RAM**: 192 GB
- **Cost**: $3.912/hour
- **Network**: 50 Gbps
- **Best for**: Cost-effective full backtests

### Option 2: p3.8xlarge (High-Performance)
- **GPU**: 4x NVIDIA V100 GPUs (faster than T4)
- **CPU**: 32 vCPUs
- **RAM**: 244 GB
- **Cost**: $12.24/hour
- **Network**: 10 Gbps
- **Best for**: Fastest processing, budget not a concern

### Option 3: g5.12xlarge (Latest)
- **GPU**: 4x NVIDIA A10G GPUs
- **CPU**: 48 vCPUs
- **RAM**: 384 GB
- **Cost**: $4.096/hour
- **Network**: 25 Gbps
- **Best for**: Latest hardware, good balance

## 🚀 Deployment Steps

### Step 1: Launch EC2 Instance

1. **Go to AWS Console** → EC2 → Launch Instance
2. **Choose AMI**: Amazon Linux 2023 (recommended)
3. **Instance Type**: Select one of the recommended types above
4. **Storage**: 50 GB GP3 (sufficient for code and data)
5. **Security Group**: Allow SSH (port 22) from your IP
6. **Key Pair**: Create or select existing key pair

### Step 2: Connect to Instance

```bash
# Connect via SSH
ssh -i your-key.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y
```

### Step 3: Install Dependencies

```bash
# Install Python 3.10 and pip
sudo yum install python3.10 python3.10-pip -y

# Install Docker (for Ollama)
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Git
sudo yum install git -y

# Logout and login again for docker group to take effect
exit
# SSH back in
```

### Step 4: Install Ollama and LLM Models

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama

# Pull the LLM model (this may take 10-20 minutes)
ollama pull llama2:7b

# Test the model
ollama run llama2:7b "Hello, world!"
```

### Step 5: Deploy Your Code

```bash
# Clone your repository or upload code
git clone <your-repo-url>
cd <your-project>

# Or upload via SCP
# scp -r -i your-key.pem /path/to/your/code ec2-user@your-instance-ip:~/

# Install Python dependencies
pip3 install -r requirements.txt
```

### Step 6: Upload Dataset

```bash
# Create data directory
mkdir -p dataset/HS500-samples

# Upload your dataset (via SCP or S3)
# scp -r -i your-key.pem /path/to/dataset ec2-user@your-instance-ip:~/dataset/

# Or download from S3
aws s3 cp s3://your-bucket/dataset/ dataset/ --recursive
```

### Step 7: Configure Environment

```bash
# Create .env file
cat > .env << EOF
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama2:7b
DATA_PATH=./dataset/HS500-samples
LOG_LEVEL=WARNING
EOF
```

### Step 8: Run High-Performance Backtest

```bash
# Navigate to backend directory
cd backend

# Run the high-performance backtest
python3 test_high_performance.py

# Or run directly
python3 -c "
from evaluation.backtester import run_high_performance_backtest
from core.data_types import BacktesterConfig

config = BacktesterConfig(
    start_date='2000-01-01',
    end_date='2025-03-28',
    tickers=['aa', 'aaau', 'aacg'],
    initial_capital=100000,
    position_sizing=0.15,
    max_positions=3,
    cash_reserve=0.2,
    min_cash_reserve=0.1,
    transaction_cost=0.001,
    slippage=0.0005,
    log_level='WARNING'
)

results = run_high_performance_backtest(config)
print(f'Backtest completed! Total trades: {len(results.trade_log)}')
"
```

## 📈 Performance Monitoring

### Monitor Progress
```bash
# Check progress in real-time
tail -f logs/backtest_*/config.json

# Monitor system resources
htop
nvidia-smi  # If using GPU instance
```

### Check Results
```bash
# List generated files
ls -la logs/backtest_*/

# Check file sizes
du -sh logs/backtest_*/*.json

# View sample results
head -20 logs/backtest_*/results.json
```

## 💰 Cost Optimization

### Spot Instances (Save 60-90%)
- Use Spot instances for non-critical runs
- Set max bid at 50% of on-demand price
- Monitor spot price trends

### Reserved Instances (Save 30-60%)
- For frequent backtesting
- 1-year or 3-year commitment
- Significant cost savings

### Auto Scaling
- Start instance only when needed
- Use AWS Lambda to trigger backtests
- Stop instance after completion

## 🔧 Performance Optimization Tips

### 1. Instance Selection
- **CPU**: More cores = faster expert processing
- **RAM**: 192GB+ recommended for large datasets
- **GPU**: Accelerates LLM inference
- **Network**: Higher bandwidth for data loading

### 2. Code Optimizations
- ✅ Minimal logging (WARNING level only)
- ✅ Batch processing
- ✅ Memory-efficient data structures
- ✅ Progress tracking every 100 days

### 3. System Optimizations
```bash
# Increase file descriptor limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize disk I/O
sudo yum install hdparm -y
sudo hdparm -t /dev/xvda  # Test disk performance
```

## 🚨 Troubleshooting

### Common Issues

1. **Out of Memory**
   ```bash
   # Monitor memory usage
   free -h
   
   # Kill memory-intensive processes
   sudo pkill -f ollama
   ```

2. **Slow LLM Responses**
   ```bash
   # Check Ollama status
   curl http://localhost:11434/api/tags
   
   # Restart Ollama
   sudo systemctl restart ollama
   ```

3. **Disk Space Issues**
   ```bash
   # Check disk usage
   df -h
   
   # Clean up old logs
   rm -rf logs/backtest_old_*
   ```

### Performance Debugging
```bash
# Monitor system resources
htop
iotop
nvidia-smi -l 1  # GPU monitoring

# Check network performance
iperf3 -c speedtest.amazonaws.com
```

## 📊 Expected Results

### Processing Times (Estimated)
- **g4dn.12xlarge**: 2-3 hours
- **p3.8xlarge**: 1-2 hours
- **g5.12xlarge**: 2-3 hours

### Output Files
- `config.json`: Backtest configuration
- `portfolio_daily.json`: Daily portfolio values
- `tickers_daily.json`: Daily ticker decisions
- `trades.json`: All executed trades
- `results.json`: Final performance metrics

### File Sizes (Estimated)
- Total: 50-100 MB for 25-year backtest
- Compressible to 10-20 MB with gzip

## 🎯 Next Steps

1. **Run Test Backtest**: Start with 1 year to validate setup
2. **Monitor Performance**: Track processing rate and resource usage
3. **Optimize Further**: Adjust batch sizes and logging levels
4. **Scale Up**: Consider multiple instances for different strategies
5. **Automate**: Set up automated backtesting pipelines

## 💡 Pro Tips

- **Use tmux/screen** for long-running backtests
- **Set up CloudWatch** for monitoring
- **Use S3** for storing results and checkpoints
- **Consider EFS** for shared data across instances
- **Use Spot Fleet** for cost optimization

This setup will allow you to run full 25-year backtests efficiently and cost-effectively on AWS EC2! 🚀 