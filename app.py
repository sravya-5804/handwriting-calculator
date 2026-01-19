import os
import sys
import io
import base64
import zipfile
import gdown
from flask import Flask, request, jsonify, render_template
from PIL import Image

# ---------------- PATHS ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MODEL_ZIP = os.path.join(BASE_DIR, "recognition_model.zip")
MODEL_DIR = os.path.join(BASE_DIR, "recognition_model")

sys.path.append(BASE_DIR)

from calculator.core.calculator import createCalculator
from calculator.network.models import loadClassifierModel

# ---------------- DOWNLOAD MODEL ----------------
# ---------------- DOWNLOAD MODEL ----------------
if not os.path.exists(MODEL_DIR):
    print("📥 Downloading model from Google Drive...")

    FILE_ID = "16v0vM98B_NIJ88VMZAv37F4H0cg7pPty"
    MODEL_ZIP = os.path.join(BASE_DIR, "recognition_model.zip")

    gdown.download(
        id=FILE_ID,
        output=MODEL_ZIP,
        quiet=False,
        fuzzy=True
    )

    if not os.path.exists(MODEL_ZIP):
        raise RuntimeError("❌ Model download failed")

    with zipfile.ZipFile(MODEL_ZIP, "r") as zip_ref:
        zip_ref.extractall(BASE_DIR)

    print("✅ Model downloaded and extracted")


# ---------------- FLASK APP ----------------
app = Flask(__name__)

calculator = createCalculator(
    loadClassifierModel(MODEL_DIR)
)

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
    data = request.json["image"]
    img_bytes = base64.b64decode(data.split(",")[1])
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    path = os.path.join(UPLOAD_DIR, "canvas.png")
    img.save(path)

    expr, ans = calculator.calculate(path)
    return jsonify({"expression": expr, "result": ans})

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
