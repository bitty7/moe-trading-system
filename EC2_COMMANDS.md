# 🚀 EC2 Commands - Copy & Paste

## **You're already on EC2 at: `ubuntu@ip-172-31-37-217:~/moe-trading-system$`**

---

## **Step 1: Pull Latest Changes**
```bash
git pull origin main
```

---

## **Step 2: Run Setup Script**
```bash
chmod +x ec2_setup.sh
./ec2_setup.sh
```

**This will:**
- ✅ Check GPU and Ollama (already installed)
- ✅ Create virtual environment (`venv/`)
- ✅ Install Python dependencies
- ✅ Unzip dataset
- ✅ Run smoke test
- ✅ Start 25-year backtest in background

⏰ **Time:** ~5-10 minutes (since Ollama/GPU already installed)

---

## **Step 3: Monitor Progress**

```bash
# Watch live log
tail -f full_backtest.log

# Check GPU usage (in another terminal)
watch -n 5 nvidia-smi

# Check if running
ps aux | grep python | grep run_backtest
```

**Press Ctrl+C to exit tail, backtest keeps running!**

---

## **Step 4: Disconnect (Optional)**

You can close SSH - backtest continues with `nohup`!

To reconnect later:
```bash
ssh -i Moe-test.pem ubuntu@51.20.8.22
cd ~/moe-trading-system
tail -f full_backtest.log
```

---

## **Step 5: Check When Complete (3-5 hours later)**

```bash
# Check if backtest finished
ps aux | grep python | grep run_backtest

# View results
cat backend/logs/backtest_llm_full_historical_2000_2025/results.json

# Or pretty print
python3 -m json.tool backend/logs/backtest_llm_full_historical_2000_2025/results.json
```

---

## **Step 6: Download Results (from local machine)**

```bash
scp -i Moe-test.pem -r \
  ubuntu@51.20.8.22:~/moe-trading-system/backend/logs/backtest_llm_full_historical_2000_2025 \
  ~/Desktop/MoE/src/backend/logs/
```

---

## **Quick Commands Summary:**

```bash
# On EC2 (you're here now):
git pull origin main
chmod +x ec2_setup.sh
./ec2_setup.sh

# Monitor:
tail -f full_backtest.log

# When done, download from local machine:
scp -i Moe-test.pem -r ubuntu@51.20.8.22:~/moe-trading-system/backend/logs/backtest_llm_full_historical_2000_2025 ~/Desktop/MoE/src/backend/logs/
```

---

## **That's it! Just 2 commands to start:** 🎉

```bash
git pull origin main
./ec2_setup.sh
```

