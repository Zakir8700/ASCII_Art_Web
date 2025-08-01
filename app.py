from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.', ' ']

def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio * 0.55)
    return image.resize((new_width, new_height))

def grayify(image):
    return image.convert("L")

def pixels_to_ascii(image, chars):
    pixels = image.getdata()
    ascii_str = "".join([chars[pixel // (256 // len(chars))] for pixel in pixels])
    return ascii_str

def convert_image_to_ascii(image_path, custom_chars):
    image = Image.open(image_path)
    image = resize_image(image)
    image = grayify(image)
    ascii_str = pixels_to_ascii(image, custom_chars)
    width = image.width
    ascii_lines = [ascii_str[i:i+width] for i in range(0, len(ascii_str), width)]
    return "\n".join(ascii_lines)

@app.route("/", methods=["GET", "POST"])
def index():
    ascii_art = ""
    if request.method == "POST":
        image_file = request.files["image"]
        ascii_chars = request.form["ascii_chars"]
        if image_file and ascii_chars:
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(filepath)
            ascii_art = convert_image_to_ascii(filepath, ascii_chars)
        os.remove(filepath)
    return render_template("index.html", ascii_art=ascii_art)

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host="0.0.0.0")
