from flask import Flask, render_template, request, send_file, url_for
from PIL import Image, ImageFilter
import os
import uuid

app = Flask(__name__)

# Tentukan folder untuk menyimpan file
upload_folder = 'uploads'
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Fungsi untuk memeriksa dan membuat folder "uploads"
def create_upload_folder():
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

# Fungsi bantu untuk memeriksa ekstensi file yang diizinkan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route untuk halaman utama
@app.route('/')
def index():
    return render_template('index.html')

# Route untuk pemrosesan gambar dengan efek blur
@app.route('/blur_image', methods=['GET', 'POST'])
def blur_image():
    create_upload_folder()

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('blur.html', result_image=None, message="Tidak ada file yang diberikan.")

        file = request.files['file']

        if file.filename == '':
            return render_template('blur.html', result_image=None, message="Tidak ada file yang dipilih.")

        if file and allowed_file(file.filename):
            # Generate nama file unik
            unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]

            # Simpan file ke server
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)

            # Buka gambar
            original_image = Image.open(file_path)

            # Efek blur pada gambar
            blur_radius = int(request.form['blur_radius'])
            blurred_image = original_image.filter(ImageFilter.GaussianBlur(blur_radius))

            # Konversi gambar ke mode RGB
            blurred_image = blurred_image.convert('RGB')

            # Simpan gambar yang telah diblur
            blurred_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'blurred_' + unique_filename)
            blurred_image.save(blurred_filename)

            # Sediakan tautan unduh
            download_url = url_for('download_file', filename='blurred_' + unique_filename)

            return render_template('blur.html', result_image=download_url, message="Gambar diproses dengan sukses.")

    return render_template('blur.html', result_image=None, message="Unggah gambar untuk menerapkan efek blur.")

# Route untuk halaman pemrosesan gambar hitam putih
@app.route('/black_and_white_image', methods=['GET', 'POST'])
def black_and_white_image():
    create_upload_folder()

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('black_and_white.html', result_image=None, message="Tidak ada file yang diberikan.")

        file = request.files['file']

        if file.filename == '':
            return render_template('black_and_white.html', result_image=None, message="Tidak ada file yang dipilih.")

        if file and allowed_file(file.filename):
            # Generate nama file unik
            unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]

            # Simpan file ke server
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)

            # Buka gambar
            original_image = Image.open(file_path)

            # Konversi gambar ke hitam putih
            black_and_white_image = original_image.convert('L')

            # Simpan gambar yang telah diubah
            bw_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'bw_' + unique_filename)
            black_and_white_image.save(bw_filename)

            # Sediakan tautan unduh
            download_url = url_for('download_file', filename='bw_' + unique_filename)

            return render_template('black_and_white.html', result_image=download_url, message="Gambar diproses dengan sukses.")

    return render_template('black_and_white.html', result_image=None, message="Unggah gambar untuk mengubah menjadi hitam putih.")

# Route untuk mengunduh file
@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
