import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'upload'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def compare_videos(video_path1, video_path2):
    cap1 = cv2.VideoCapture(video_path1)
    cap2 = cv2.VideoCapture(video_path2)

    total_frames = min(int(cap1.get(cv2.CAP_PROP_FRAME_COUNT)), int(cap2.get(cv2.CAP_PROP_FRAME_COUNT)))

    ssim_values = []

    for frame_number in range(total_frames):
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or not ret2:
            break

        # Resize frames to have the same dimensions
        frame1 = cv2.resize(frame1, (640, 480))  # Adjust dimensions as needed
        frame2 = cv2.resize(frame2, (640, 480))  # Adjust dimensions as needed

        gray_frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray_frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        similarity_index, _ = ssim(gray_frame1, gray_frame2, full=True)
        ssim_values.append(similarity_index)

    cap1.release()
    cap2.release()

    avg_ssim = np.mean(ssim_values)

    similarity_threshold = 0.9

    if avg_ssim > similarity_threshold:
        return "Videos are similar."
    else:
        return "Videos are different."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_files():
    if 'file1' not in request.files or 'file2' not in request.files:
        flash('Please select two videos for comparison.')
        return redirect(request.url)

    file1 = request.files['file1']
    file2 = request.files['file2']

    if file1.filename == '' or file2.filename == '':
        flash('Please select two videos for comparison.')
        return redirect(request.url)

    if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)

        file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
        file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))

        video_path1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
        video_path2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)

        result = compare_videos(video_path1, video_path2)

        return render_template('index.html', result=result)

    else:
        flash('Allowed file types are mp4, avi, mkv.')
        return redirect(request.url)

# if __name__ == '__main__':
#     app.secret_key = 'supersecretkey'
#     app.run(debug=True)
