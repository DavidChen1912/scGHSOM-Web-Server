import os
import sys
import time
import json

# ----------------------------------------------------------
# 專案根目錄（scGHSOM）
# ----------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ⭐ 重要：worker 執行時強制切換到專案根目錄
os.chdir(BASE_DIR)

# ⭐ 讓 Python 能找得到 execute.py、programs/
sys.path.append(BASE_DIR)

from execute import run_pipeline


QUEUE_DIR = os.path.join(BASE_DIR, "web", "queue")
RAW_DATA_DIR = os.path.join(BASE_DIR, "raw-data")
APPLICATION_DIR = os.path.join(BASE_DIR, "applications")

print(f"[WORKER STARTED]")
print(f"Current working directory: {os.getcwd()}")
print(f"Queue directory: {QUEUE_DIR}")
print(f"Raw-data directory: {RAW_DATA_DIR}")
print(f"Applications directory: {APPLICATION_DIR}")
print("========================================================")


# ----------------------------------------------------------
# Worker 無限循環
# ----------------------------------------------------------
while True:
    files = [f for f in os.listdir(QUEUE_DIR) if f.endswith(".json")]

    if not files:
        time.sleep(2)
        continue

    job_file = sorted(files)[0]
    job_path = os.path.join(QUEUE_DIR, job_file)

    print(f"\n[JOB FOUND] {job_file}")

    with open(job_path, "r") as f:
        job_info = json.load(f)

    job_id = job_info["job_id"]
    tau1 = job_info["tau1"]
    tau2 = job_info["tau2"]
    index = job_info.get("index")
    label = job_info.get("label")

    print(f"[RUNNING JOB] job_id={job_id}")
    print(f"  tau1={tau1}, tau2={tau2}, index={index}, label={label}")

    try:
        run_pipeline(
            data=job_id,
            tau1=tau1,
            tau2=tau2,
            index=index,
            label=label
        )
        print(f"[JOB COMPLETED] {job_id}")

    except Exception as e:
        print(f"[ERROR] Job {job_id} failed: {e}")

    else:
        # ------------------------------------------------------
        # 刪 queue json
        # ------------------------------------------------------
        os.remove(job_path)
        print(f"[QUEUE CLEANED] Removed {job_file}")

        # ------------------------------------------------------
        # 刪 raw-data CSV
        # ------------------------------------------------------
        raw_file_path = os.path.join(RAW_DATA_DIR, f"{job_id}.csv")
        if os.path.exists(raw_file_path):
            os.remove(raw_file_path)
            print(f"[RAW DATA CLEANED] Removed {job_id}.csv")
        else:
            print(f"[RAW DATA MISSING] {raw_file_path} not found")

    print("--------------------------------------------------------")
    time.sleep(1)
