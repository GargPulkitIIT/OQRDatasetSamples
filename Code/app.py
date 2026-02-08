import os
import base64
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from io import BytesIO

from config import Config
from encoder import encode
from decoder import decode
from OQR.Processing.OQRGenerator import OQR_Generator

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.route("/")
def home():
    return redirect(url_for("encoder_page"))

@app.route("/encoder", methods=["GET", "POST"])
def encoder_page():
    encoded_value = None
    v1 = v2 = v3 = None
    oqr_type = "3"

    if request.method == "POST":
        oqr_type = request.form.get("oqr_type", "3")
        v1 = request.form.get("v1")
        v2 = request.form.get("v2")
        v3 = request.form.get("v3") if oqr_type == "3" else None

        if oqr_type == "2":
            encoded_value = encode(v1, v2, None)
        else:
            encoded_value = encode(v1, v2, v3)

    return render_template("encoder.html", encoded_value=encoded_value, v1=v1, v2=v2, v3=v3, oqr_type=oqr_type)

@app.route("/decoder", methods=["GET", "POST"])
def decoder_page():
    v1 = v2 = v3 = None

    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            flash("No file selected")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("File type not allowed")
            return redirect(request.url)

        filename = secure_filename(file.filename or "")
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        # Simulated encoded data extraction
        with open(path, "rb") as f:
            encoded_data = f.read().decode(errors="ignore")

        v1, v2, v3 = decode(encoded_data)

    return render_template("decoder.html", v1=v1, v2=v2, v3=v3)

if __name__ == "__main__":
    app.run(debug=True)
