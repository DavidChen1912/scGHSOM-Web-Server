import os
import sys
import uuid
import json
import csv
from flask import Flask, render_template, request, jsonify, redirect, send_file
from markupsafe import Markup

# ==========================================================
# ⭐ Ensure Python can locate scGHSOM root directory
# ==========================================================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from programs.Visualize.cluster_feature_map import init_feature_map_dash
from programs.Visualize.cluster_distribution_map import cluster_distribution_map

# ==========================================================
# Flask Init
# ==========================================================
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024  # 300 MB limit

BASE_DIR = ROOT_DIR
RAW_DATA_DIR = os.path.join(BASE_DIR, "raw-data")
QUEUE_DIR = os.path.join(BASE_DIR, "web", "queue")
RESULT_DIR = os.path.join(BASE_DIR, "Result")
APPLICATION_DIR = os.path.join(BASE_DIR, "applications")

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(QUEUE_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# ==========================================================
# ⭐ Dash Init (one-time)
# ==========================================================
dash_app = init_feature_map_dash(app)

# ==========================================================
# Flask Pages
# ==========================================================
@app.route('/')
def home():
    return render_template('run.html', title='Run Analysis')


@app.route('/results')
def results():
    return render_template('result.html', title='Results')


@app.route('/results/example')
def results_example():
    return render_template(
        "result.html",
        title="Example Result",
        job_id="example",
        auto_query=True
    )


@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html', title='Tutorial')


@app.route('/reference')
def reference():
    return render_template('reference.html', title='Reference')


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')


# ⭐ Provide example.csv to frontend (for preview)
@app.route('/fetch-example')
def fetch_example():
    example_path = os.path.join(RAW_DATA_DIR, "example.csv")
    if not os.path.exists(example_path):
        return "example.csv not found", 404
    return send_file(example_path, mimetype="text/csv")


# ==========================================================
# ⭐ Submit form
# ==========================================================
@app.route('/submit', methods=['POST'])
def submit():
    file = request.files.get('file')
    tau1 = request.form.get('tau1')
    tau2 = request.form.get('tau2')
    index = request.form.get('index') or None
    label = request.form.get('label') or None
    gmail = request.form.get('gmail') or None
    example_flag = request.form.get("example_flag")

    job_id = f"scGHSOM_{uuid.uuid4().hex[:8]}"

    # ================================
    # ⭐ Example mode
    # ================================
    if example_flag == "true":
        raw_path = os.path.join(RAW_DATA_DIR, f"{job_id}.csv")
        example_path = os.path.join(RAW_DATA_DIR, "example.csv")

        if not os.path.exists(example_path):
            return render_template(
                "run.html",
                title="Run Analysis",
                message="[ERROR] example.csv not found in raw-data/"
            )

        with open(example_path, "rb") as src, open(raw_path, "wb") as dst:
            dst.write(src.read())

    # ================================
    # ⭐ User upload
    # ================================
    else:
        if file:
            raw_path = os.path.join(RAW_DATA_DIR, f"{job_id}.csv")
            file.save(raw_path)

    # Save queue info
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

    # ======================================================
    # ⭐ Final success message (no preview/download line)
    # ======================================================
    message = Markup(
        f"Upload successful! Your Job ID: {job_id}<br>"
        f"Your analysis may take some time. Please wait patiently.<br>"
        f'You can also explore the official example result here: '
        f'<a href="/results/example" target="_blank">Results → Example</a>'
    )

    return render_template(
        'run.html',
        title='Run Analysis',
        message=message,
        tau1=tau1,
        tau2=tau2,
        gmail=gmail
    )


# ==========================================================
# ⭐ Preview (first 100 rows)
# ==========================================================
@app.route('/preview/<job_id>')
def preview_file(job_id):

    filepath = os.path.join(RAW_DATA_DIR, f"{job_id}.csv")

    if not os.path.exists(filepath):
        return f"<h3>Raw file for Job ID {job_id} not found.</h3>"

    rows = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            rows.append(row)
            if i >= 100:
                break

    html = "<h2>Preview of Uploaded File (First 100 rows)</h2>"
    html += "<table border='1' cellpadding='6' style='border-collapse: collapse;'>"

    for r in rows:
        html += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"

    html += "</table>"

    return html


# ==========================================================
# ⭐ Download raw file
# ==========================================================
@app.route('/download/<job_id>')
def download_file(job_id):
    filepath = os.path.join(RAW_DATA_DIR, f"{job_id}.csv")

    if not os.path.exists(filepath):
        return f"<h3>File for Job ID {job_id} not found.</h3>"

    return send_file(filepath, as_attachment=True)


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
# ⭐ Feature Map API
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
# ⭐ Distribution Map
# ==========================================================
@app.route('/distribution-map/<job_id>')
def distribution_map_result(job_id):

    folders = [
        f for f in os.listdir(APPLICATION_DIR)
        if f.startswith(job_id + "-")
    ]

    if not folders:
        return f"<h3>No application folder found for Job ID: {job_id}</h3>"

    folder = folders[0]
    tau1, tau2 = folder.split("-")[1:3]

    html_path = os.path.join(
        APPLICATION_DIR,
        folder,
        "graphs",
        f"CDM_{job_id}_{tau1}_{tau2}.html"
    )

    if not os.path.exists(html_path):
        try:
            cluster_distribution_map(job_id, float(tau1), float(tau2))
        except Exception as e:
            return f"<h3>Error generating Distribution Map: {e}</h3>"

    return send_file(html_path)


# ==========================================================
# Main
# ==========================================================
if __name__ == '__main__':
    print("[FLASK] Starting Web Server ...")
    app.run(host="0.0.0.0", port=5000)































