# EC2 Deployment Guide

## 🚀 Step-by-Step EC2 Deployment

### 1. Prepare Your Code

First, push your current code to GitHub:

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit with MoE trading system"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 2. Launch EC2 Instance

1. **Go to AWS Console** → EC2 → Launch Instance
2. **Choose Instance Type**: `g4dn.xlarge` or `g5.xlarge` (GPU support)
3. **AMI**: Ubuntu 22.04 LTS
4. **Storage**: At least 50GB (recommended 100GB)
5. **Security Group**: Allow SSH (port 22) from your IP
6. **Key Pair**: Create or select existing key pair

### 3. Connect to EC2

```bash
# Download your key pair and set permissions
chmod 400 your-key-pair.pem

# Connect to EC2
ssh -i your-key-pair.pem ubuntu@YOUR_EC2_IP
```

### 4. Clone and Setup

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# Run the setup script
chmod +x ec2_setup.sh
./ec2_setup.sh
```

**Note**: Update the GitHub URL in `ec2_setup.sh` before running.

### 5. Run Full Backtest

```bash
# Run the full backtest
chmod +x run_full_backtest.sh
./run_full_backtest.sh
```

### 6. Monitor Progress

```bash
# Check progress
tail -f logs/latest_backtest.log

# Check GPU usage
nvidia-smi

# Check disk space
df -h
```

### 7. Download Results

When the backtest completes:

```bash
# From your local machine, download results
scp -i your-key-pair.pem -r ubuntu@YOUR_EC2_IP:~/YOUR_REPO_NAME/logs/ ./local_logs/

# Or use AWS CLI to download
aws s3 sync s3://your-bucket/logs/ ./local_logs/
```

### 8. Push Results to GitHub

```bash
# On EC2, commit and push results
cd ~/YOUR_REPO_NAME
git add logs/
git commit -m "Add full backtest results from EC2"
git push origin main

# On your local machine, pull results
git pull origin main
```

## 🔧 Troubleshooting

### GPU Issues
```bash
# Check GPU status
nvidia-smi

# Restart Ollama with GPU
sudo systemctl restart ollama
ollama list
```

### Memory Issues
```bash
# Check memory usage
free -h

# If low memory, use smaller model
ollama pull llama3.1:8b
```

### Storage Issues
```bash
# Check disk space
df -h

# Clean up if needed
sudo apt-get autoremove
sudo apt-get autoclean
```

## 📊 Expected Performance

- **Setup Time**: 15-30 minutes
- **Model Download**: 10-20 minutes (depending on internet)
- **Full Backtest**: 2-8 hours (depending on data size)
- **Processing Rate**: 2-5 days/second with GPU

## 💰 Cost Estimation

- **g4dn.xlarge**: ~$0.50/hour
- **g5.xlarge**: ~$1.00/hour
- **Total for 8-hour backtest**: $4-8

## 🎯 Next Steps

1. **Analyze Results**: Review the generated logs and metrics
2. **Optimize Parameters**: Adjust trading parameters based on results
3. **Scale Up**: Run on larger datasets or more tickers
4. **Production**: Deploy for real-time trading (future)

## 📞 Support

If you encounter issues:
1. Check the logs in `logs/` directory
2. Verify GPU is working: `nvidia-smi`
3. Check Ollama status: `ollama list`
4. Review system resources: `htop`, `df -h`, `free -h` 