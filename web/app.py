import os
import sys
import uuid
import json
import csv
from flask import Flask, render_template, request, jsonify, redirect

# ==========================================================
# ⭐ 確保 Python 找得到 scGHSOM 專案根目錄
# ==========================================================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from programs.Visualize.cluster_feature_map import init_feature_map_dash


# ==========================================================
# Flask 初始化
# ==========================================================
app = Flask(__name__)

BASE_DIR = ROOT_DIR
RAW_DATA_DIR = os.path.join(BASE_DIR, "raw-data")
QUEUE_DIR = os.path.join(BASE_DIR, "web", "queue")
RESULT_DIR = os.path.join(BASE_DIR, "Result")
APPLICATION_DIR = os.path.join(BASE_DIR, "applications")

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(QUEUE_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)


# ==========================================================
# ⭐ 初始化 Dash（僅建立一次）
# ==========================================================
dash_app = init_feature_map_dash(app)


# ==========================================================
# Flask 頁面
# ==========================================================
@app.route('/')
def home():
    return render_template('home.html', title='Home')


@app.route('/run')
def run_analysis():
    return render_template('run.html', title='Run Analysis')


@app.route('/database/summary')
def summary():
    return render_template('summary.html', title='Job Summary')


@app.route('/database/feature-map')
def feature_map():
    return render_template('feature_map.html', title='Cluster Feature Map')


@app.route('/database/distribution-map')
def distribution_map():
    return render_template('distribution_map.html', title='Distribution Map')


@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html', title='Tutorial')


@app.route('/reference')
def reference():
    return render_template('reference.html', title='Reference')


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')


# ==========================================================
# 提交分析表單
# ==========================================================
@app.route('/submit', methods=['POST'])
def submit():
    file = request.files.get('file')
    tau1 = request.form.get('tau1')
    tau2 = request.form.get('tau2')
    index = request.form.get('index') or None
    label = request.form.get('label') or None
    gmail = request.form.get('gmail') or None

    job_id = f"scGHSOM_{uuid.uuid4().hex[:8]}"

    # 儲存 raw-data
    if file:
        raw_path = os.path.join(RAW_DATA_DIR, f"{job_id}.csv")
        file.save(raw_path)

    # 儲存到 queue
    job_info = {
        "job_id": job_id,
        "tau1": float(tau1),
        "tau2": float(tau2),
        "index": index,
        "label": label,
        "gmail": gmail
    }

    queue_path = os.path.join(QUEUE_DIR, f"{job_id}.json")
    with open(queue_path, "w") as f:
        json.dump(job_info, f, indent=4)

    print(f"[NEW JOB CREATED] {job_info}")

    return render_template(
        'run.html',
        title='Run Analysis',
        message=f"Upload successful! Your Job ID: {job_id}",
        tau1=tau1,
        tau2=tau2,
        gmail=gmail
    )


# ==========================================================
# Job Summary API
# ==========================================================
@app.route('/api/job/<job_id>')
def get_job_summary(job_id):

    filename = f"{job_id}_result.csv"
    filepath = os.path.join(RESULT_DIR, filename)

    if not os.path.exists(filepath):
        return jsonify({"found": False})

    try:
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            row = next(reader)

            result = {
                "found": True,
                "metrics": {
                    "ARI": row.get("ARI", "NA"),
                    "NMI": row.get("NMI", "NA"),
                    "CH": row.get("CH", "NA"),
                    "DB": row.get("DB", "NA"),
                    "Leaf": row.get("Leaf_Number", "NA")
                }
            }

        return jsonify(result)

    except:
        return jsonify({"found": False})


# ==========================================================
# ⭐ Feature Map API — 回傳 Dash URL
# ==========================================================
@app.route('/api/feature/<job_id>')
def api_feature_map(job_id):

    folders = [
        f for f in os.listdir(APPLICATION_DIR)
        if f.startswith(job_id + "-")
    ]

    if not folders:
        return jsonify({"found": False})

    return jsonify({
        "found": True,
        "dash_url": f"/feature-map/{job_id}"
    })


# ==========================================================
# ⭐ 不要有任何 /feature-map/<job_id> 的 Flask route!!!
# Dash 會處理所有 /feature-map/* 路由
# ==========================================================


# ==========================================================
# 主程序
# ==========================================================
if __name__ == '__main__':
    print("[FLASK] Starting Web Server ...")
    app.run(debug=True)


























