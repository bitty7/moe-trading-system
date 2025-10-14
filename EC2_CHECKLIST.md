# AWS EC2 Deployment Checklist

## ✅ **Quick Start Guide**

---

## **📋 Pre-Deployment (Local Machine)**

### **1. Push Code to GitHub:**
```bash
cd ~/Desktop/MoE/src

# Add all files
git add .

# Commit
git commit -m "LLM baseline complete - ready for EC2 deployment"

# Push to GitHub
git push origin main
```

**Repository:** https://github.com/bitty7/moe-trading-system.git ✅

---

## **🖥️ AWS EC2 Setup**

### **2. Launch EC2 Instance:**

**Go to:** AWS Console → EC2 → Launch Instance

**Configuration:**
- [ ] Name: `moe-trading-backtest`
- [ ] AMI: **Ubuntu Server 22.04 LTS**
- [ ] Instance type: **g4dn.xlarge** (T4 GPU, $0.526/hr)
- [ ] Key pair: Create new → Name: `moe-trading-key` → Download .pem
- [ ] Storage: **100 GB gp3**
- [ ] Security: Allow SSH from My IP
- [ ] **Launch Instance**

**Wait 2-3 minutes** for instance to start

**Note the Public IPv4:** `___.___.___.___`

---

### **3. Connect to EC2:**
```bash
# Set key permissions
chmod 400 ~/Downloads/moe-trading-key.pem

# Connect (replace with YOUR IP)
ssh -i ~/Downloads/moe-trading-key.pem ubuntu@YOUR_EC2_IP
```

---

### **4. Setup Environment (On EC2):**
```bash
# Clone repository
git clone https://github.com/bitty7/moe-trading-system.git
cd moe-trading-system

# Run setup script
chmod +x ec2_setup.sh
./ec2_setup.sh
```

**This takes ~15-20 minutes** (installs Python, GPU drivers, Ollama, models)

---

### **5. Verify Setup:**
```bash
# Check GPU
nvidia-smi

# Check Ollama
ollama list

# Should see: llama3.1:8b
```

---

## **🚀 Run Backtest**

### **6. Smoke Test First:**
```bash
cd ~/moe-trading-system/backend

# Quick test (~30 seconds)
python run_backtest.py --config config_smoke_test.json
```

**Expected:** Shows results, no errors

---

### **7. Run Full Historical Backtest:**
```bash
# Run in background (takes 1-2 hours)
nohup python run_backtest.py --config config_full_historical.json > ../full_backtest.log 2>&1 &

# Save process ID
echo $! > ../backtest.pid
```

---

### **8. Monitor Progress:**
```bash
# View live log
tail -f ~/moe-trading-system/full_backtest.log

# Check GPU usage
watch -n 5 nvidia-smi

# Check if still running
cat ~/moe-trading-system/backtest.pid
ps aux | grep $(cat ~/moe-trading-system/backtest.pid)
```

**To detach from tail:** Press `Ctrl+C`
**To disconnect SSH safely:** Type `exit` (backtest keeps running with nohup)

---

## **📥 Download Results**

### **9. When Complete (from local machine):**
```bash
# Download results folder
scp -i ~/Downloads/moe-trading-key.pem -r \
  ubuntu@YOUR_EC2_IP:~/moe-trading-system/backend/logs/backtest_llm_full_historical_2019_2024 \
  ~/Desktop/MoE/src/backend/logs/

# View results locally
cd ~/Desktop/MoE/src/backend
python test/view_results.py backtest_llm_full_historical_2019_2024
```

---

### **10. Or Push to GitHub (from EC2):**
```bash
# On EC2
cd ~/moe-trading-system
git add backend/logs/backtest_llm_full_historical_2019_2024/
git commit -m "Add full historical backtest results (2019-2024)"
git push origin main

# Then on local machine
cd ~/Desktop/MoE/src
git pull origin main
```

---

## **💰 Stop Instance**

### **11. Stop EC2 (Save Money):**

**From AWS Console:**
- EC2 → Instances → Select instance → Instance state → **Stop**

**Costs after stopping:**
- Compute: $0/hr ✅
- Storage: ~$10/month for 100GB

**To resume:** Instance state → Start (new IP will be assigned)

---

## **📊 Expected Results**

**Full Historical Backtest (2018-2025, 6.6 years):**
- Trading days: ~1,500
- Decisions: ~4,500 (3 tickers)
- Runtime: 1-2 hours on g4dn.xlarge
- Output: All 5 JSON files with complete metrics
- File sizes: ~5-10 MB total

**Key Metrics to Check:**
- Total Return (6 year cumulative)
- Annualized Return
- Sharpe Ratio
- Max Drawdown
- Total Trades
- Runtime (for LLM vs pre-trained comparison)

---

## **⚠️ Important Reminders**

- [ ] **Save your .pem key** - Can't download again!
- [ ] **Note the public IP** - Changes when instance stops/starts
- [ ] **Use nohup** - So backtest continues if SSH disconnects
- [ ] **Download results** - Before terminating instance
- [ ] **Stop instance** - When done to save money
- [ ] **Check costs** - Monitor AWS billing dashboard

---

## **🎯 Total Cost Estimate**

| Activity | Time | Cost (g4dn.xlarge) |
|----------|------|-------------------|
| Setup | 20 min | $0.18 |
| Smoke test | 1 min | $0.01 |
| Full backtest | 1-2 hrs | $0.53-$1.05 |
| **Total** | **~2 hrs** | **~$1.20** |

**Very affordable!** 🎉

---

## **✅ Success Checklist**

After deployment, you should have:
- [ ] EC2 instance running with GPU
- [ ] Ollama + llama3.1:8b installed
- [ ] Smoke test passed
- [ ] Full historical backtest completed
- [ ] Results downloaded locally
- [ ] EC2 instance stopped
- [ ] Total cost: ~$1-2

---

**Ready to deploy? Follow the checklist in order!** 🚀

