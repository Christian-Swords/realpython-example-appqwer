from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] ='uploads'
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
    return redirect(url_for('show_video', filename=filename))

@app.route('/video/<filename>')
def show_video(filename):
    return render_template('video.html',filename=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
