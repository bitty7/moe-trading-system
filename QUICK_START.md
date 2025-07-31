# 🚀 Quick Start - EC2 Deployment (2 Hours Target)

## **Step 1: Prepare Your Key File**

1. **Place your EC2 key file** in the `src/` folder
   - Rename it to `your-key-pair.pem`
   - Or update the filename in `connect_ec2.sh`

2. **Update the EC2 IP** in `connect_ec2.sh`:
   ```bash
   EC2_IP="YOUR_ACTUAL_EC2_PUBLIC_IP"
   ```

## **Step 2: Push Code to GitHub**

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit with MoE trading system"

# Create GitHub repository: https://github.com/thabetalenezi/moe-trading-system
# Then push:
git remote add origin https://github.com/thabetalenezi/moe-trading-system.git
git push -u origin main
```

## **Step 3: Launch EC2 Instance**

1. **Go to AWS Console** → EC2 → Launch Instance
2. **Instance Type**: `g5.xlarge` (best GPU for speed)
3. **AMI**: Ubuntu 22.04 LTS
4. **Storage**: 100GB (for logs and models)
5. **Security Group**: Allow SSH (port 22) from your IP
6. **Key Pair**: Use the same key file you placed in src/

## **Step 4: Connect and Deploy**

```bash
# Connect to EC2
./connect_ec2.sh

# On EC2, run setup (takes ~15 minutes)
chmod +x ec2_setup.sh
./ec2_setup.sh

# Run full backtest (target: 2 hours)
chmod +x run_full_backtest.sh
./run_full_backtest.sh
```

## **Step 5: Monitor Progress**

```bash
# Check GPU usage
nvidia-smi

# Monitor backtest progress
tail -f logs/latest_backtest.log

# Check disk space
df -h
```

## **Step 6: Download Results**

```bash
# From your local machine
scp -i your-key-pair.pem -r ubuntu@YOUR_EC2_IP:~/moe-trading-system/logs/ ./local_logs/

# Or push to GitHub from EC2
cd ~/moe-trading-system
git add logs/
git commit -m "Add full backtest results"
git push origin main
```

## **⚡ Speed Optimizations Applied:**

1. **GPU Instance**: g5.xlarge with latest GPU
2. **Fast Model**: llama3.1:8b (smallest, fastest)
3. **Minimal Logging**: WARNING level only
4. **Optimized Lookback**: Reduced periods for speed
5. **Parallel Processing**: GPU acceleration

## **📊 Expected Timeline:**

- **Setup**: 15 minutes
- **Model Download**: 10 minutes  
- **Full Backtest**: 2 hours (target)
- **Total**: ~2.5 hours

## **🔧 Troubleshooting:**

### If it's too slow:
```bash
# Check GPU usage
nvidia-smi

# Restart Ollama
sudo systemctl restart ollama

# Use smaller model
ollama pull llama3.1:8b
```

### If you run out of memory:
```bash
# Check memory
free -h

# Kill unnecessary processes
sudo pkill -f ollama
sudo systemctl restart ollama
```

## **📞 Need Help?**

1. Check GPU: `nvidia-smi`
2. Check Ollama: `ollama list`
3. Check logs: `tail -f logs/latest_backtest.log`
4. Check resources: `htop`, `df -h`

## **🎯 Success Criteria:**

✅ GPU working: `nvidia-smi` shows GPU usage  
✅ Ollama running: `ollama list` shows models  
✅ Backtest running: Logs show progress  
✅ Results generated: `logs/` directory has files  
✅ Time target: Under 2 hours total runtime 