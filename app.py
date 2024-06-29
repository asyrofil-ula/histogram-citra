import os
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'supersecretkey'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_histogram(image):
    image_array = np.array(image)
    histograms = {
        'red': np.histogram(image_array[:, :, 0], bins=256, range=(0, 256))[0].tolist(),
        'green': np.histogram(image_array[:, :, 1], bins=256, range=(0, 256))[0].tolist(),
        'blue': np.histogram(image_array[:, :, 2], bins=256, range=(0, 256))[0].tolist(),
    }
    return histograms

def calculate_histogram_gray(image):
    image_array = np.array(image.convert("L"))
    histogram, _ = np.histogram(image_array, bins=256, range=(0, 256))
    return histogram.tolist()

def calculate_normalized_histogram(image):
    image_array = np.array(image).astype(np.float32) / 255.0
    histograms = {
        'red': np.histogram(image_array[:, :, 0], bins=256, range=(0, 1))[0].tolist(),
        'green': np.histogram(image_array[:, :, 1], bins=256, range=(0, 1))[0].tolist(),
        'blue': np.histogram(image_array[:, :, 2], bins=256, range=(0, 1))[0].tolist(),
    }
    return histograms

def calculate_normalized_histogram_gray(image):
    image_array = np.array(image.convert("L")).astype(np.float32) / 255.0
    histogram, _ = np.histogram(image_array, bins=256, range=(0, 1))
    return histogram.tolist()

def calculate_statistics(histogram):
    values = np.array(histogram)
    mean = np.mean(values)
    variance = np.var(values)
    std_dev = np.std(values)
    return {'mean': mean, 'variance': variance, 'std_dev': std_dev}

def convert_to_grayscale(input_image_path, output_image_path):
    img = Image.open(input_image_path).convert('L')
    img.save(output_image_path)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/pages/rgb', methods=['GET'])
def rgb():
    return render_template('/pages/rgb.html')

@app.route('/pages/gray', methods=['GET'])
def gray():
    return render_template('/pages/gray.html')

@app.route('/upload/rgb', methods=['POST'])
def upload_image_rgb():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Proses gambar dan hitung histogram
        path_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img = Image.open(path_file)
        histogram = calculate_histogram(img)
        normalized_histogram = calculate_normalized_histogram(img)
        
        # Hitung statistik
        stats = {
            'red': calculate_statistics(histogram['red']),
            'green': calculate_statistics(histogram['green']),
            'blue': calculate_statistics(histogram['blue']),
        }
        normalized_stats = {
            'red': calculate_statistics(normalized_histogram['red']),
            'green': calculate_statistics(normalized_histogram['green']),
            'blue': calculate_statistics(normalized_histogram['blue']),
        }
        
        return render_template('/pages/rgb.html', 
            filename=filename, 
            histogram=histogram, 
            normalized_histogram=normalized_histogram, 
            stats=stats, 
            normalized_stats=normalized_stats
        )
    else:
        flash('Allowed image types are - png, jpg, jpeg')
        return redirect(request.url)



@app.route('/upload/gray', methods=['POST'])
def upload_image_gray():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Convert to grayscale and save
        grayscale_filename = 'gray_' + filename
        grayscale_file_path = os.path.join(app.config['UPLOAD_FOLDER'], grayscale_filename)
        convert_to_grayscale(file_path, grayscale_file_path)
        
        # Calculate the histogram
        img = Image.open(file_path)
        histogram = calculate_histogram_gray(img)
        normalized_histogram = calculate_normalized_histogram_gray(img)
        
        # Calculate statistics
        stats = calculate_statistics(histogram)
        normalized_stats = calculate_statistics(normalized_histogram)
        
        return render_template('/pages/gray.html', filename=filename, histogram=histogram, normalized_histogram=normalized_histogram, stats=stats, normalized_stats=normalized_stats)
    else:
        flash('Allowed image types are - png, jpg, jpeg')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == '__main__':
    app.run(debug=True)
