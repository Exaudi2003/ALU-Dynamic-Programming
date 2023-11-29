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

# Fungsi untuk pemrosesan gambar dengan efek blur
def process_blur_image(file_path, blur_radius):
    original_image = Image.open(file_path)
    blurred_image = original_image.filter(ImageFilter.GaussianBlur(blur_radius))
    blurred_image = blurred_image.convert('RGB')
    return blurred_image

# Fungsi untuk pemrosesan gambar menjadi hitam putih
def process_black_and_white_image(file_path):
    original_image = Image.open(file_path)
    black_and_white_image = original_image.convert('L')
    return black_and_white_image

# Fungsi untuk menyimpan dan memberikan nama unik pada file
def save_and_get_unique_filename(file, folder):
    unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder, unique_filename)

    # Pastikan direktori sudah ada
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    file.save(file_path)
    return unique_filename, file_path


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
            # Simpan dan dapatkan nama unik file
            unique_filename, file_path = save_and_get_unique_filename(file, 'uploads')

            # Cek apakah gambar sudah diproses sebelumnya
            cached_result = process_blur_image.cache.get(file_path)
            if cached_result:
                return render_template('blur.html', result_image=cached_result, message="Gambar diproses dengan sukses (dari cache).")

            # Jika belum diproses sebelumnya, lakukan pemrosesan
            blur_radius = int(request.form['blur_radius'])
            blurred_image = process_blur_image(file_path, blur_radius)

            # Simpan gambar yang telah diblur
            blurred_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'blurred_' + unique_filename)
            blurred_image.save(blurred_filename)

            # Sediakan tautan unduh
            download_url = url_for('download_file', filename='blurred_' + unique_filename)

            # Cache hasil pemrosesan untuk digunakan di permintaan selanjutnya
            process_blur_image.cache[file_path] = download_url

            return render_template('blur.html', result_image=download_url, message="Gambar diproses dengan sukses.", unique_filename=unique_filename)

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
            # Simpan dan dapatkan nama unik file
            unique_filename, file_path = save_and_get_unique_filename(file, 'uploads')

            # Cek apakah gambar sudah diproses sebelumnya
            cached_result = process_black_and_white_image.cache.get(file_path)
            if cached_result:
                return render_template('black_and_white.html', result_image=cached_result, message="Gambar diproses dengan sukses (dari cache).")

            # Jika belum diproses sebelumnya, lakukan pemrosesan
            black_and_white_image_result = process_black_and_white_image(file_path)

            # Simpan gambar yang telah diubah
            bw_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'bw_' + unique_filename)
            black_and_white_image_result.save(bw_filename)

            # Sediakan tautan unduh
            download_url = url_for('download_file', filename='bw_' + unique_filename)

            # Cache hasil pemrosesan untuk digunakan di permintaan selanjutnya
            process_black_and_white_image.cache[file_path] = download_url

            return render_template('black_and_white.html', result_image=download_url, message="Gambar diproses dengan sukses.")

    return render_template('black_and_white.html', result_image=None, message="Unggah gambar untuk mengubah menjadi hitam putih.")

from flask import send_from_directory

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    # Inisialisasi cache
    process_blur_image.cache = {}
    process_black_and_white_image.cache = {}

    app.run(debug=True)