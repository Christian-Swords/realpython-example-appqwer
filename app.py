# from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, get_flashed_messages
# import os

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] ='uploads'
# app.secret_key = 'secret_key'
# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/show_number', methods=['POST'])
# def show_number():
#     number = request.form['number']
#     return redirect(url_for('display_number', number=number))

# @app.route('/display_number/<number>')
# def display_number(number):
#     return render_template('display_number.html', number=number)

# @app.route('/uploadUsersFile', methods = ['POST'])
# def uploadUsersFile():
#     file = request.files['video']
#     filename = file.filename
#     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#     feedback = "Too Low"
#     flash(feedback)
#     return redirect(url_for('show_video', filename=filename))

# @app.route('/video/<filename>')
# def show_video(filename):
#     feedback = None
#     feedback_messages = get_flashed_messages()
#     if feedback_messages:
#         feedback = feedback_messages[0]
#     return render_template('video.html',filename=filename, feedback=feedback)

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, get_flashed_messages
import os
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] ='uploads'
app.secret_key = 'secret_key'
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/show_number', methods=['POST'])
def show_number():
    number = request.form['number']
    return redirect(url_for('display_number', number=number))

@app.route('/display_number/<number>')
def display_number(number):
    return render_template('display_number.html', number=number)

@app.route('/uploadUsersFile', methods = ['POST'])
def uploadUsersFile():
    file = request.files['video']
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    feedback = 0

    print(filename)
    cap = cv2.VideoCapture('uploads/' + filename)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('uploads/output_video.mp4', fourcc, fps, (width, height))
    while True:
        ret,frame = cap.read()
        flipped_frame = cv2.flip(frame,1)
        if not ret:
            break
        flipped_frame = cv2.flip(frame,1)
        out.write(flipped_frame)
        feedback += 1
    cap.release()
    out.release()
    return redirect(url_for('show_video', filename=filename,feedback=feedback))

@app.route('/video/<filename>')
def show_video(filename):
    feedback = None
    feedback = request.args.get('feedback')
    return render_template('video.html',filename=filename, feedback=feedback)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
