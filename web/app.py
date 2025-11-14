import os
import uuid
import json
import csv
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# -------------------------
# Directory paths
# -------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DATA_DIR = os.path.join(BASE_DIR, "raw-data")
QUEUE_DIR = os.path.join(BASE_DIR, "web", "queue")
RESULT_DIR = os.path.join(BASE_DIR, "Result")

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(QUEUE_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)


# -------------------------
# 首頁與主要頁面
# -------------------------
@app.route('/')
def home():
    return render_template('home.html', title='Home')


@app.route('/run')
def run_analysis():
    return render_template('run.html', title='Run Analysis')


# -------------------------
# 提交分析表單
# -------------------------
@app.route('/submit', methods=['POST'])
def submit():
    file = request.files.get('file')
    tau1 = request.form.get('tau1')
    tau2 = request.form.get('tau2')
    index = request.form.get('index') or None
    label = request.form.get('label') or None
    gmail = request.form.get('gmail') or None

    job_id = f"scGHSOM_{uuid.uuid4().hex[:8]}"

    # 存 raw-data
    if file:
        raw_path = os.path.join(RAW_DATA_DIR, f"{job_id}.csv")
        file.save(raw_path)

    # 寫 queue JSON
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


# -------------------------
# Database 子頁面
# -------------------------
@app.route('/database/summary')
def summary():
    return render_template('summary.html', title='Job Summary')


@app.route('/database/feature-map')
def feature_map():
    return render_template('feature_map.html', title='Cluster Feature Map')


@app.route('/database/distribution-map')
def distribution_map():
    return render_template('distribution_map.html', title='Cluster Distribution Map')


# -------------------------
# 其他靜態頁面
# -------------------------
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
# ★★★ Job Summary API（返回 NA / 數值皆可）
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

            # 直接回傳字串，不轉型，不會爆掉
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

    except Exception as e:
        print("[ERROR reading result csv]", e)
        return jsonify({"found": False})


# -------------------------
# Feature Map API（暫時 placeholder）
# -------------------------
@app.route('/api/feature/<job_id>')
def get_feature_map(job_id):
    job_id_lower = job_id.lower()
    if job_id_lower == "example":
        return jsonify({
            "found": True,
            "image_url": "https://via.placeholder.com/800x400?text=Feature+Map+Preview"
        })
    else:
        return jsonify({"found": False})


# -------------------------
# Distribution Map API
# -------------------------
@app.route('/api/distribution/<job_id>')
def get_distribution_map(job_id):
    job_id_lower = job_id.lower()
    if job_id_lower == "example":
        return jsonify({
            "found": True,
            "image_url": "https://via.placeholder.com/800x400?text=Distribution+Map+Preview"
        })
    else:
        return jsonify({"found": False})


# -------------------------
# 主程式
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)










