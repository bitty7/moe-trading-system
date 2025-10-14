# 🚀 Simplified AWS EC2 Deployment Guide

## **One Script Does Everything!**

The `ec2_setup.sh` script now handles the complete workflow:
1. Installs all dependencies
2. Runs smoke test
3. Starts full historical backtest (2000-2025)

---

## **Quick Start (3 Steps)**

### **Step 1: Push to GitHub** (Local Machine)
```bash
cd ~/Desktop/MoE/src
git add .
git commit -m "Ready for EC2 - 25 year historical backtest"
git push origin main
```

### **Step 2: Launch EC2 & Connect**
1. AWS Console → EC2 → Launch Instance
2. **Instance:** g4dn.xlarge (T4 GPU, $0.526/hr)
3. **AMI:** Ubuntu 22.04
4. **Storage:** 100GB
5. Download `.pem` key, note Public IP
6. SSH: `ssh -i key.pem ubuntu@YOUR_IP`

### **Step 3: Run One Script** (On EC2)
```bash
git clone https://github.com/bitty7/moe-trading-system.git
cd moe-trading-system
chmod +x ec2_setup.sh
./ec2_setup.sh
```

**That's it!** The script will:
- Install everything (~20 min)
- Run smoke test (~30 sec)
- Start 25-year backtest in background (~3-5 hours)

---

## **Monitor Progress**

```bash
# View live log
tail -f ~/moe-trading-system/full_backtest.log

# Check GPU
watch -n 5 nvidia-smi

# Check if running
ps aux | grep $(cat ~/moe-trading-system/backtest.pid)
```

**You can disconnect SSH** - backtest continues with nohup!

---

## **Download Results** (When Complete)

From your local machine:
```bash
scp -i key.pem -r \
  ubuntu@YOUR_IP:~/moe-trading-system/backend/logs/backtest_llm_full_historical_2000_2025 \
  ~/Desktop/MoE/src/backend/logs/
```

Then view:
```bash
cd ~/Desktop/MoE/src/backend
python test/view_results.py backtest_llm_full_historical_2000_2025
```

---

## **Stop Instance** (Save Money!)

AWS Console → EC2 → Stop Instance

**Cost:** ~$2.50 total for 25 years of backtesting! 🎉

---

## **What You'll Get:**

**Complete 25-Year LLM Baseline:**
- 2000-2025 performance
- ~18,900 decisions
- Total return, Sharpe ratio
- Max drawdown, volatility
- All trades over 25 years
- **Runtime** (for pre-trained comparison)

**Perfect for your thesis!** 📚

