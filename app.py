import os
import io
import sys
import base64
from flask import Flask, request, jsonify
from PIL import Image

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from calculator.core.calculator import createCalculator
from calculator.network.models import loadClassifierModel

# ---------------- LOAD MODEL ----------------
MODEL_DIR = os.path.join(BASE_DIR, "recognition_model")

print("🧠 Loading model from GitHub files...")
calculator = createCalculator(loadClassifierModel(MODEL_DIR))

# ---------------- FLASK APP ----------------
app = Flask(__name__)

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return "Handwriting Calculator API is running ✅"

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
