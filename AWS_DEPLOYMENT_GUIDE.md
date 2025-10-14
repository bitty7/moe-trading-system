# 🚀 AWS EC2 Deployment Guide - Full Historical Backtest

This guide walks you through deploying the MoE Trading System on AWS EC2 with GPU for running the complete historical backtest (2019-2024).

---

## 📋 **Prerequisites**

- AWS Account
- GitHub account
- SSH key pair for EC2
- Your code ready to push

---

## **Step 1: Create Config for Full Historical Run** ✅

Already created: `backend/config_full_historical.json`

**Configuration:**
- Date range: **2000-01-03 to 2025-03-28** (~25 years) - EVERY data point from all tickers
- Tickers: aa (full 25 years), aaau (from 2018), aacg (from 2008)
- Trading days: ~6,300 days
- Decisions: ~18,900 total (3 tickers)
- Initial capital: $1M
- Strategy: Entropy-based dynamic weighting

**Estimated runtime:**
- Local: ~8-10 hours (at 0.2 days/sec) - Not recommended
- EC2 GPU: **~3-5 hours** (estimated 2-5x faster)

---

## **Step 2: Push Code to GitHub** 📤

### **2.1 Initialize Git (if not done):**
```bash
cd /Users/thabetalenezi/Desktop/MoE/src

# Check current status
git status

# If not initialized
git init
git add .
git commit -m "Complete LLM baseline implementation - research ready"
```

### **2.2 Create GitHub Repository:**
1. Go to https://github.com/new
2. Name: `moe-trading-system` (or your choice)
3. Description: "Mixture of Experts Trading System for Research"
4. **Don't** initialize with README (you already have one)
5. Click "Create repository"

### **2.3 Push to GitHub:**
```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/moe-trading-system.git

# Push code
git branch -M main
git push -u origin main
```

---

## **Step 3: Launch AWS EC2 Instance** 🖥️

### **3.1 Instance Configuration:**

**Recommended Instance Types:**

| Instance Type | GPU | vCPUs | RAM | Price/Hour | Best For |
|--------------|-----|-------|-----|------------|----------|
| **g4dn.xlarge** | T4 (16GB) | 4 | 16GB | ~$0.526 | **Recommended** - Good balance |
| **g4dn.2xlarge** | T4 (16GB) | 8 | 32GB | ~$0.752 | Faster processing |
| **g5.xlarge** | A10G (24GB) | 4 | 16GB | ~$1.006 | Best GPU, more expensive |

**💡 Recommendation:** Start with **g4dn.xlarge** ($0.526/hr)

### **3.2 Launch Steps:**

1. **Go to AWS Console** → EC2 → Launch Instance

2. **Name:** `moe-trading-backtest`

3. **AMI:** Ubuntu Server 22.04 LTS (HVM), SSD Volume Type

4. **Instance type:** `g4dn.xlarge`

5. **Key pair:**
   - Create new key pair or select existing
   - Name: `moe-trading-key`
   - Type: RSA
   - Format: .pem
   - **Download and save the .pem file!**

6. **Network settings:**
   - Auto-assign public IP: **Yes**
   - Security group: Create new
     - Allow SSH (port 22) from **My IP**
     - Name: `moe-trading-sg`

7. **Storage:**
   - Size: **100 GB** (recommended for logs)
   - Type: gp3 (faster)

8. **Advanced details:**
   - Shutdown behavior: **Stop** (not terminate)
   - Enable termination protection: **Yes** (safety)

9. **Click "Launch Instance"**

### **3.3 Wait for Instance:**
- Status: Running
- Status checks: 2/2 passed (wait ~2-3 minutes)
- Note the **Public IPv4 address**

---

## **Step 4: Connect to EC2** 🔗

### **4.1 Prepare SSH Key:**
```bash
# Move key to safe location
mv ~/Downloads/moe-trading-key.pem ~/.ssh/
chmod 400 ~/.ssh/moe-trading-key.pem
```

### **4.2 Connect:**
```bash
# Replace with your instance IP
ssh -i ~/.ssh/moe-trading-key.pem ubuntu@YOUR_EC2_IP

# Example:
# ssh -i ~/.ssh/moe-trading-key.pem ubuntu@13.51.166.193
```

**First time:** Type `yes` to accept fingerprint

---

## **Step 5: Setup EC2 Environment** ⚙️

### **5.1 Clone Repository:**
```bash
# On EC2
cd ~
git clone https://github.com/YOUR_USERNAME/moe-trading-system.git
cd moe-trading-system
```

### **5.2 Run Setup Script (Does Everything!):**
```bash
# Make executable
chmod +x ec2_setup.sh

# Run setup - This does EVERYTHING automatically!
./ec2_setup.sh
```

**This single script will:**
- Install Python 3.10+
- Install CUDA drivers for GPU
- Install Ollama
- Download llama3.1:8b model (~4.7GB)
- Install Python dependencies
- **Run smoke test** to verify setup
- **Start full historical backtest** (2000-2025) in background
- Takes ~20 minutes setup + 3-5 hours backtest

### **5.3 Verify Setup:**
```bash
# Check GPU
nvidia-smi

# Check Ollama
ollama list

# Check Python
python3 --version
```

---

## **Step 6: Run Full Historical Backtest** 🚀

### **6.1 Quick Test First:**
```bash
cd ~/moe-trading-system/backend

# Run smoke test to verify everything works
python run_backtest.py --config config_smoke_test.json
```

**Expected:** Completes in ~30 seconds, shows results

### **6.2 Run Full Historical Backtest:**
```bash
# Run the big one (2019-2024)
nohup python run_backtest.py --config config_full_historical.json > ../full_backtest.log 2>&1 &

# Note the process ID
echo $! > ../backtest.pid
```

**Using nohup:** Runs in background even if you disconnect

---

## **Step 7: Monitor Progress** 📊

### **7.1 Check Progress:**
```bash
# View live log
tail -f ~/moe-trading-system/full_backtest.log

# Check if still running
ps aux | grep run_backtest

# Check partial results
ls -lh ~/moe-trading-system/backend/logs/backtest_llm_full_historical_2019_2024/
```

### **7.2 Check GPU Usage:**
```bash
# Monitor GPU in real-time
watch -n 5 nvidia-smi

# Check GPU utilization
nvidia-smi dmon -s u
```

### **7.3 Estimate Time Remaining:**
```bash
# Check partial progress
cd ~/moe-trading-system/backend
python test/check_backtest_status.py
```

**Estimated runtime on g4dn.xlarge:**
- ~1-2 hours for 6 years of data
- Depends on GPU speed and LLM inference time

---

## **Step 8: Download Results** 📥

### **8.1 When Backtest Completes:**

Check completion:
```bash
# Check if results.json exists
ls -lh ~/moe-trading-system/backend/logs/backtest_llm_full_historical_2019_2024/results.json

# View results
cd ~/moe-trading-system/backend
python test/view_results.py backtest_llm_full_historical_2019_2024
```

### **8.2 Download to Local Machine:**

**Option A: Using scp (from your local machine):**
```bash
# Download entire results folder
scp -i ~/.ssh/moe-trading-key.pem -r \
  ubuntu@YOUR_EC2_IP:~/moe-trading-system/backend/logs/backtest_llm_full_historical_2019_2024 \
  ~/Desktop/MoE/src/backend/logs/

# Or download just results.json
scp -i ~/.ssh/moe-trading-key.pem \
  ubuntu@YOUR_EC2_IP:~/moe-trading-system/backend/logs/backtest_llm_full_historical_2019_2024/results.json \
  ~/Desktop/results_ec2.json
```

**Option B: Push to GitHub (from EC2):**
```bash
# On EC2
cd ~/moe-trading-system
git add backend/logs/backtest_llm_full_historical_2019_2024/
git commit -m "Add full historical backtest results (2019-2024)"
git push origin main

# On local machine
cd ~/Desktop/MoE/src
git pull origin main
```

---

## **Step 9: Stop/Terminate Instance** 💰

### **Stop Instance (to save costs):**
```bash
# From AWS Console
EC2 → Instances → Select instance → Instance state → Stop
```

**Important:**
- Stopped instance: No compute charges (only storage ~$10/month for 100GB)
- Can restart later with same data
- Public IP will change (use Elastic IP to keep same IP)

### **Terminate Instance (when completely done):**
```bash
# Only do this when you're 100% sure you have all results!
EC2 → Instances → Select instance → Instance state → Terminate
```

---

## **💰 Cost Estimation**

### **For Full Historical Backtest (2000-2025, 25 years):**

| Component | Time | Cost (g4dn.xlarge @ $0.526/hr) |
|-----------|------|-------------------------------|
| Setup | 20 min | $0.18 |
| Smoke test | 1 min | $0.01 |
| **Full backtest** | **3-5 hours** | **$1.58-$2.63** |
| **Total** | **~4-5 hours** | **~$2.10-$2.80** |

**Still very affordable for 25 years of historical testing!**

---

## **⚡ Quick Start Commands (Copy-Paste)**

### **On Your Local Machine:**
```bash
# 1. Push to GitHub
cd ~/Desktop/MoE/src
git add .
git commit -m "Complete LLM baseline - ready for EC2"
git remote add origin https://github.com/YOUR_USERNAME/moe-trading-system.git
git push -u origin main
```

### **On EC2 (after launch and SSH):**
```bash
# 2. Clone and setup
git clone https://github.com/YOUR_USERNAME/moe-trading-system.git
cd moe-trading-system
chmod +x ec2_setup.sh
./ec2_setup.sh

# 3. Verify setup
nvidia-smi
ollama list

# 4. Run smoke test
cd backend
python run_backtest.py --config config_smoke_test.json

# 5. Run full historical
nohup python run_backtest.py --config config_full_historical.json > ../full_backtest.log 2>&1 &

# 6. Monitor
tail -f ../full_backtest.log

# 7. View results when done
python test/view_results.py backtest_llm_full_historical_2019_2024
```

### **Download Results (from local machine):**
```bash
scp -i ~/.ssh/moe-trading-key.pem -r \
  ubuntu@YOUR_EC2_IP:~/moe-trading-system/backend/logs/backtest_llm_full_historical_2019_2024 \
  ~/Desktop/MoE/src/backend/logs/
```

---

## **🛠️ Troubleshooting**

### **GPU Not Found:**
```bash
nvidia-smi  # Should show GPU
sudo reboot  # Restart if needed
```

### **Ollama Not Working:**
```bash
sudo systemctl status ollama
sudo systemctl restart ollama
ollama list  # Should show llama3.1:8b
```

### **Out of Memory:**
```bash
free -h  # Check RAM
# Use smaller model: ollama pull llama3.1:8b (already using smallest)
```

### **Out of Disk Space:**
```bash
df -h  # Check disk
# Clean up: sudo apt-get clean
```

---

## **📊 Expected Output**

After 1-2 hours, you should have:

```
logs/backtest_llm_full_historical_2019_2024/
├── config.json
├── results.json          ← Total return, Sharpe, runtime for 6 years
├── portfolio_daily.json  ← ~1500 daily snapshots
├── tickers_daily.json    ← ~4500 decisions
└── trades.json          ← All trades over 6 years
```

**Results will show:**
- Total return over 6 years
- Sharpe ratio for entire period
- Max drawdown
- Total trades
- Runtime (for LLM vs pre-trained comparison)

---

## **🎯 Step-by-Step Checklist**

- [ ] Create full historical config ✅ (done!)
- [ ] Push code to GitHub
- [ ] Launch g4dn.xlarge EC2 instance
- [ ] Download .pem key and save it
- [ ] Note the public IP address
- [ ] SSH into EC2
- [ ] Clone repository
- [ ] Run ec2_setup.sh
- [ ] Verify GPU and Ollama
- [ ] Run smoke test
- [ ] Run full historical backtest
- [ ] Monitor progress
- [ ] Download results
- [ ] Stop/terminate instance

---

## **🚨 Important Notes**

1. **Save your .pem key** - You can't download it again!
2. **Note the public IP** - You'll need it to connect
3. **Monitor costs** - Stop instance when done
4. **Download results** - Before terminating instance
5. **GitHub backup** - Push results to GitHub as backup

---

**Ready to deploy? Follow the steps in order!** 🚀

