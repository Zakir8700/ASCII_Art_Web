from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from PIL import Image
import string

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Default fallback ASCII characters
DEFAULT_ASCII_CHARS = "@#S%?*+;:,. "

def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio * 0.55)
    return image.resize((new_width, new_height))

def grayify(image):
    return image.convert("L")

def pixels_to_ascii(image, chars):
    pixels = image.getdata()
    ascii_str = "".join([chars[min(pixel * len(chars) // 256, len(chars) - 1)] for pixel in pixels])
    return ascii_str

def convert_image_to_ascii(image_path, custom_chars):
    image = Image.open(image_path)
    image = resize_image(image)
    image = grayify(image)
    ascii_str = pixels_to_ascii(image, custom_chars)
    width = image.width
    ascii_lines = [ascii_str[i:i+width] for i in range(0, len(ascii_str), width)]
    return "\n".join(ascii_lines)

def is_valid_ascii_set(chars):
    valid_chars = set(string.printable)
    return all(c in valid_chars for c in chars)

@app.route("/", methods=["GET", "POST"])
def index():
    ascii_art = ""
    error_message = ""

    if request.method == "POST":
        image_file = request.files.get("image")
        ascii_chars = request.form.get("ascii_chars", "").strip()

        if not ascii_chars:
            error_message = "Please enter at least one ASCII character."
        elif not is_valid_ascii_set(ascii_chars):
            error_message = "Invalid ASCII characters. Only printable ASCII characters are allowed."
        elif image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(filepath)

            try:
                ascii_art = convert_image_to_ascii(filepath, ascii_chars)
                os.remove(filepath) 
            except Exception as e:
                error_message = f"Error during image processing: {str(e)}"
        else:
            error_message = "Please upload a valid image."

    return render_template("index.html", ascii_art=ascii_art, error=error_message)

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host="0.0.0.0", port=10000)
