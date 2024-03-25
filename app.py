from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Ensure a secure, random secret key
app.config['SECRET_KEY'] = os.urandom(24)

# Function to create a secure filepath
def secure_filepath(filename):
    return os.path.join('uploads', filename)

@app.route('/')
def index():
    return render_template('index_home.html')

@app.route('/predict/image')
def predict_image():
    return render_template('image-prediction.html')

@app.route('/predict', methods=['POST'])
def upload():
    if request.method == 'POST':
        f = request.files['image']
        
        # Ensure the uploads folder exists
        os.makedirs('uploads', exist_ok=True)
        
        # Securely save the file using the secure_filename utility
        filepath = secure_filepath(secure_filename(f.filename))
        f.save(filepath)
        
        # Redirect to the image detection page with the uploaded file path
        return redirect(url_for('detect', file_path=filepath))

@app.route('/detect', methods=['POST'])
def detect():
    input_image = request.files['file-input']
    
    # Ensure the temp folder exists
    os.makedirs('static/temp', exist_ok=True)
    
    temp_image_path = os.path.join('static', 'temp', secure_filename(input_image.filename))
    input_image.save(temp_image_path)

    yolo_script_path = os.path.join('yolov7', 'detect.py')
    output_dir = os.path.join('static', 'detection_results')
    os.makedirs(output_dir, exist_ok=True)

    subprocess.run([
        'python', yolo_script_path,
        '--weights', 'yolov7/best.pt',
        '--img-size', '640',
        '--conf', '0.25',
        '--source', temp_image_path
    ])

    # Clean up: Remove the temporary input image
    os.remove(temp_image_path)

    output_image_filename = secure_filename(input_image.filename)
    output_image_path = os.path.join(output_dir, f"{os.path.splitext(output_image_filename)[0]}_detected.jpg")

    # Render the image_detection.html template with the prediction result
    return render_template('image_detection.html', result_image=output_image_filename, output_image_path=output_image_path)

@app.route('/detect_video', methods=['POST'])
def detect_video():
    input_video = request.files['file-input']
    
    # Ensure the temp folder exists
    os.makedirs('static/temp', exist_ok=True)
    
    temp_video_path = os.path.join('static', 'temp', secure_filename(input_video.filename))
    input_video.save(temp_video_path)

    yolo_script_path = os.path.join('yolov7', 'detect.py')
    output_dir = os.path.join('static', 'detection_results')
    os.makedirs(output_dir, exist_ok=True)

    subprocess.run([
        'python', yolo_script_path,
        '--weights', 'yolov7/best.pt',
        '--img-size', '640',
        '--conf', '0.25',
        '--source', temp_video_path
    ])

    # Clean up: Remove the temporary input image
    os.remove(temp_video_path)

    output_video_filename = secure_filename(input_video.filename)
    output_video_path = os.path.join(output_dir, f"{os.path.splitext(output_video_filename)[0]}_detected.mp4")

    # Render the image_detection.html template with the prediction result
    return render_template('video_detection.html', result_video=output_video_filename, output_video_path=output_video_path)
    

@app.route('/image_detection.html')
def image_detection():
    return render_template('image_detection.html')

@app.route('/index_home.html')
def index_again():
    return render_template('index_home.html')

@app.route('/webcam.html')
def webcam():
    return render_template('webcam.html')

@app.route('/video_detection.html')
def video_detection():
    return render_template('/video_detection.html')

if __name__ == '__main__':
    app.run(debug=True)
