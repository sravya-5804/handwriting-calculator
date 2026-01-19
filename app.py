import sys
import io
import os
import base64
import zipfile
import requests
from flask import Flask, render_template, request, jsonify
from PIL import Image

# ---------------- PATHS ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

MODEL_ZIP_URL = "https://github.com/sravya-5804/handwriting-calculator/releases/download/v1.0/recognition_model.zip"
MODEL_ZIP_PATH = os.path.join(BASE_DIR, "recognition_model.zip")
MODEL_DIR = os.path.join(BASE_DIR, "recognition_model")

# ---------------- DOWNLOAD MODEL ----------------
if not os.path.exists(MODEL_DIR):
    print("📥 Downloading model from GitHub Releases...")
    r = requests.get(MODEL_ZIP_URL, stream=True)
    if r.status_code != 200:
        raise RuntimeError("❌ Failed to download model")

    with open(MODEL_ZIP_PATH, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    with zipfile.ZipFile(MODEL_ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(BASE_DIR)

# ---------------- IMPORT MODEL CODE ----------------
from calculator.core.calculator import createCalculator
from calculator.network.models import loadClassifierModel

calculator = createCalculator(loadClassifierModel(MODEL_DIR))

# ---------------- FLASK APP ----------------
app = Flask(__name__)

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict-upload", methods=["POST"])
def predict_upload():
    file = request.files.get("image")
    if not file:
        return jsonify({"expression": "?", "result": "?"})

    path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(path)

    expr, ans = calculator.calculate(path)
    return jsonify({"expression": expr, "result": ans})

@app.route("/predict-canvas", methods=["POST"])
def predict_canvas():
    data = request.json.get("image")
    if not data:
        return jsonify({"expression": "?", "result": "?"})

    img_bytes = base64.b64decode(data.split(",")[1])
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    path = os.path.join(UPLOAD_DIR, "canvas.png")
    img.save(path)

    expr, ans = calculator.calculate(path)
    return jsonify({"expression": expr, "result": ans})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
