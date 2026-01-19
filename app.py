import sys
import io
import os
import base64
import zipfile
from flask import Flask, render_template, request, jsonify
from PIL import Image

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from calculator.core.calculator import createCalculator
from calculator.network.models import loadClassifierModel

import gdown

MODEL_DIR = os.path.join(BASE_DIR, "recognition_model")
MODEL_ZIP = os.path.join(BASE_DIR, "recognition_model.zip")

if not os.path.exists(MODEL_DIR):
    url = "https://drive.google.com/uc?id=YOUR_FILE_ID"
    gdown.download(url, MODEL_ZIP, quiet=False)

    with zipfile.ZipFile(MODEL_ZIP, "r") as zip_ref:
        zip_ref.extractall(BASE_DIR)


# ----------------- APP -----------------
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
    try:
        file = request.files.get("image")
        if not file:
            return jsonify({"expression": "?", "result": "?"})

        path = os.path.join(UPLOAD_DIR, file.filename)
        file.save(path)

        expr, ans = calculator.calculate(path)
        return jsonify({"expression": expr, "result": ans})

    except Exception as e:
        print(e)
        return jsonify({"expression": "?", "result": "?"})

@app.route("/predict-canvas", methods=["POST"])
def predict_canvas():
    try:
        data = request.json["image"]
        img_bytes = base64.b64decode(data.split(",")[1])
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        path = os.path.join(UPLOAD_DIR, "canvas.png")
        img.save(path)

        expr, ans = calculator.calculate(path)
        return jsonify({"expression": expr, "result": ans})

    except Exception as e:
        print(e)
        return jsonify({"expression": "?", "result": "?"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

