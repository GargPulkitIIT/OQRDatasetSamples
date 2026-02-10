import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from werkzeug.utils import secure_filename

from config import Config
from encoder import encode
from decoder import decode
from image_utils import list_supported_formats

app = Flask(__name__)
app.config.from_object(Config)

app.jinja_env.globals.update(supported_formats=list_supported_formats())

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs("static/generated", exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/")
def home():
    return redirect(url_for("encoder_page"))


@app.route("/encoder", methods=["GET", "POST"])
def encoder_page():
    image_url = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()  
        qr_type = request.form.get("type")
        output_format = request.form.get("format", "png")  
        if not name:
            flash("Please provide a name for your QR code")
            return redirect(request.url)

        if not qr_type:
            flash("Type is required")
            return redirect(request.url)

        if qr_type == "2":
            data2 = request.form.get("data2", "").strip()
            data3 = request.form.get("data3", "").strip()

            if not data2 or not data3:
                flash("Data 2 and Data 3 are required for Type 2")
                return redirect(request.url)

            image_path = encode(name, "2", data3, data2, data1=None, format=output_format)

        elif qr_type == "3":
            data1 = request.form.get("data1", "").strip()
            data2 = request.form.get("data2", "").strip()
            data3 = request.form.get("data3", "").strip()

            if not data1 or not data2 or not data3:
                flash("Data 1, Data 2, and Data 3 are required for Type 3")
                return redirect(request.url)

            image_path = encode(name, "3", data3, data2, data1, format=output_format)

        else:
            flash("Invalid OQR type")
            return redirect(request.url)

        if not image_path:
            flash("QR generation failed. Please try again with different data.")
            return redirect(request.url)

        flash(f"QR code generated successfully in {output_format.upper()} format!", "success")
        filename = os.path.basename(image_path)
        image_url = url_for("static", filename=f"generated/{filename}")

    return render_template("encoder.html", image_url=image_url)


@app.route("/decoder", methods=["GET", "POST"])
def decoder_page():
    v1 = v2 = v3 = None
    error_message = None

    if request.method == "POST":
        file = request.files.get("file")

        if not file or not file.filename or file.filename == "":
            flash("No file selected")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("File type not allowed")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        v1, v2, v3 = decode(path)
        
        if v1 is None and v2 is None and v3 is None:
            error_message = "NO OQR DETECTED - Try Again"
            flash("No QR codes detected in the image. Please try with a clearer image.", "error")

    return render_template("decoder.html", v1=v1, v2=v2, v3=v3, error_message=error_message)


if __name__ == "__main__":
    app.run(debug=True)