from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from PIL import Image, ImageFilter

app = Flask(__name__)

STATIC_IMAGE_DIR = 'static/images'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blur_image', methods=['GET', 'POST'])
def blur_image():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename != '':
            filename = os.path.join(STATIC_IMAGE_DIR, 'uploaded_image.jpg')
            file.save(filename)

            blur_radius = int(request.form['blur_radius'])
            width = int(request.form['width'])
            height = int(request.form['height'])

            image = Image.open(filename)
            blurred_image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            resized_image = blurred_image.resize((width, height))

            blurred_filename = os.path.join(STATIC_IMAGE_DIR, 'blurred_image.jpg')
            resized_image.save(blurred_filename)

            return render_template('blur.html', result_image=blurred_filename, download_url=url_for('download_blurred_image'), message="Image blurred and resized successfully.")

    return render_template('blur.html', result_image=None, message="Upload an image to blur.")

@app.route('/black_and_white_image', methods=['GET', 'POST'])
def black_and_white_image():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename != '':
            filename = os.path.join(STATIC_IMAGE_DIR, 'uploaded_image.jpg')
            file.save(filename)

            width = int(request.form['width'])
            height = int(request.form['height'])

            image = Image.open(filename).convert('L')
            resized_image = image.resize((width, height))

            bw_filename = os.path.join(STATIC_IMAGE_DIR, 'bw_image.jpg')
            resized_image.save(bw_filename)

            return render_template('black_and_white.html', result_image=bw_filename, download_bw_url=url_for('download_bw_image'), message="Image converted to black and white successfully.")

    return render_template('black_and_white.html', result_image=None, message="Upload an image to convert to black and white.")

@app.route('/download_blurred_image')
def download_blurred_image():
    blurred_filename = os.path.join(STATIC_IMAGE_DIR, 'blurred_image.jpg')
    return send_file(blurred_filename, as_attachment=True)

@app.route('/download_bw_image')
def download_bw_image():
    bw_filename = os.path.join(STATIC_IMAGE_DIR, 'bw_image.jpg')
    return send_file(bw_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
