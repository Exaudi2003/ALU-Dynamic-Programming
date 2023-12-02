from flask import Flask, render_template, request, send_file, url_for, send_from_directory
from PIL import Image, ImageFilter
import os
import uuid
import cv2
from seam_carving_module import calculate_cumulative_energy, find_vertical_seam, remove_vertical_seam

app = Flask(__name__)

upload_folder = 'uploads'
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

def create_upload_folder():
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_and_get_unique_filename(file, folder):
    unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder, unique_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)
    return unique_filename, file_path

def process_blur_image(file_path, blur_radius):
    original_image = Image.open(file_path)
    blurred_image = original_image.filter(ImageFilter.GaussianBlur(blur_radius))
    return blurred_image

def process_black_and_white_image(file_path):
    original_image = Image.open(file_path)
    black_and_white_image_result = original_image.convert('L').convert('RGB')
    return black_and_white_image_result

def seam_carving_example(image_path, new_width, new_height):
    image = cv2.imread(image_path)
    cumulative_energy = calculate_cumulative_energy(image)

    for i in range(image.shape[1] - new_width):
        seam = find_vertical_seam(cumulative_energy)
        image = remove_vertical_seam(image, seam)
        cumulative_energy = calculate_cumulative_energy(image)

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'seam_carving_result.jpg')
    cv2.imwrite(output_path, image)

    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blur_image', methods=['GET', 'POST'])
def blur_image():
    create_upload_folder()

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('blur.html', result_image=None, message="Tidak ada file diberikan.")

        file = request.files['file']

        if file.filename == '':
            return render_template('blur.html', result_image=None, message="Tidak ada file dipilih.")

        if file and allowed_file(file.filename):
            unique_filename, file_path = save_and_get_unique_filename(file, 'uploads')
            blur_radius = int(request.form['blur_radius'])
            blurred_image = process_blur_image(file_path, blur_radius)
            blurred_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'blurred_' + unique_filename)
            blurred_image.save(blurred_filename)
            download_url = url_for('download_file', filename='blurred_' + unique_filename)
            return render_template('blur.html', result_image=download_url, message="Gambar diproses dengan sukses.", unique_filename=unique_filename)

    return render_template('blur.html', result_image=None, message="Unggah gambar untuk menerapkan efek blur.")

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
            unique_filename, file_path = save_and_get_unique_filename(file, 'uploads')
            black_and_white_image_result = process_black_and_white_image(file_path)
            
            # Menggunakan 'bw_' sebagai awalan pada nama file
            bw_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'bw_' + unique_filename)
            black_and_white_image_result.save(bw_filename)
            
            # Menggunakan 'bw_' sebagai awalan pada url_for
            download_url = url_for('download_file', filename='bw_' + unique_filename)
            
            return render_template('black_and_white.html', result_image=download_url, message="Gambar diproses dengan sukses.", unique_filename=unique_filename)

    return render_template('black_and_white.html', result_image=None, message="Unggah gambar untuk mengubah menjadi hitam putih.")


@app.route('/seam_carving', methods=['GET', 'POST'])
def seam_carving():
    create_upload_folder()

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('seam_carving.html', result_image=None, message="Tidak ada file yang diberikan.")

        file = request.files['file']

        if file.filename == '':
            return render_template('seam_carving.html', result_image=None, message="Tidak ada file yang dipilih.")

        if file and allowed_file(file.filename):
            unique_filename, file_path = save_and_get_unique_filename(file, 'uploads')
            new_width = int(request.form['new_width'])
            new_height = int(request.form['new_height'])

            try:
                result_path = seam_carving_example(file_path, new_width, new_height)
                result_url = url_for('download_file', filename='seam_carving_result.jpg')
                return render_template('seam_carving.html', result_image=result_url, message="Seam Carving selesai.")
            
            except Exception as e:
                return render_template('seam_carving.html', result_image=None, message=f"Terjadi kesalahan: {str(e)}")

    return render_template('seam_carving.html', result_image=None, message="Unggah gambar untuk melakukan Seam Carving.")

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
