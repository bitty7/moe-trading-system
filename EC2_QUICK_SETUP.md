# 🚀 EC2 Quick Setup Guide (Updated with venv)

## **What's Fixed:**
- ✅ Added `requirements.txt` with all dependencies
- ✅ Creates Python virtual environment automatically
- ✅ All commands run inside venv
- ✅ Proper isolation and dependency management

---

## **Commands to Run on EC2:**

### **1. Clone and Setup (ONE command does everything!):**
```bash
cd ~
git clone https://github.com/bitty7/moe-trading-system.git
cd moe-trading-system
chmod +x ec2_setup.sh
./ec2_setup.sh
```

**This script will:**
1. Install system packages (Python, GPU drivers, CUDA)
2. Install Ollama + llama3.1:8b model
3. **Create Python virtual environment** (`venv/`)
4. **Install all dependencies** from `requirements.txt`
5. Unzip dataset
6. Run smoke test
7. Start 25-year backtest in background

⏰ **Total time:** ~20-25 minutes setup + 3-5 hours backtest

---

## **2. Monitor Progress:**

```bash
# Watch live log
tail -f ~/moe-trading-system/full_backtest.log

# Check GPU usage
watch -n 5 nvidia-smi

# Check if backtest is running
ps aux | grep python | grep run_backtest

# Check process by PID
cat ~/moe-trading-system/backtest.pid
ps aux | grep $(cat ~/moe-trading-system/backtest.pid)
```

**You can disconnect SSH** - backtest continues with `nohup`!

---

## **3. Manual Commands (if needed):**

If you need to run commands manually:

```bash
cd ~/moe-trading-system

# Activate virtual environment
source venv/bin/activate

# Run any Python command
cd backend
python run_backtest.py --config config_smoke_test.json

# Deactivate when done
deactivate
```

---

## **4. Download Results (when complete):**

From your **local machine**:
```bash
scp -i Moe-test.pem -r \
  ubuntu@51.20.8.22:~/moe-trading-system/backend/logs/backtest_llm_full_historical_2000_2025 \
  ~/Desktop/MoE/src/backend/logs/
```

---

## **5. Stop EC2 Instance (save money!):**

AWS Console → EC2 → Stop Instance

**Total cost:** ~$2.50 for 25 years of backtesting! 🎉

---

## **Troubleshooting:**

### **If setup fails:**
```bash
# Check Python version (needs 3.8+)
python3 --version

# Check if venv was created
ls -la ~/moe-trading-system/venv/

# Manually create venv if needed
cd ~/moe-trading-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **If backtest fails:**
```bash
# Check the log
tail -100 ~/moe-trading-system/full_backtest.log

# Run manually to see errors
cd ~/moe-trading-system
source venv/bin/activate
cd backend
python run_backtest.py --config config_smoke_test.json
```

---

## **What's Different Now:**

**Before:**
- ❌ System-wide pip install (conflicts possible)
- ❌ No dependency isolation
- ❌ Manual dependency management

**After:**
- ✅ Virtual environment (`venv/`)
- ✅ Clean dependency isolation
- ✅ `requirements.txt` for reproducibility
- ✅ Automatic setup with one script

**Ready to deploy!** 🚀

