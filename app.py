from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, get_flashed_messages
import os
import cv2
#os.environ['MEDIAPIPE_CPU_ONLY'] = '1'
#import mediapipe as mp
#from mediapipe import solutions as mp


# class PoseDetector:

#     def __init__(self, mode = False, upBody = False, smooth=True, detectionCon = 0.5, trackCon = 0.5):

#         self.mode = mode
#         self.upBody = upBody
#         self.smooth = smooth
#         self.detectionCon = detectionCon
#         self.trackCon = trackCon

#         self.mpDraw = mp.drawing_utils
#         self.mpPose = mp.pose
#         #self.pose = self.mpPose.Pose(self.mode, self.upBody, self.smooth, self.detectionCon, self.trackCon)
#         self.pose = self.mpPose.Pose()

#     def findPose(self, img, draw=True):
#         imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         self.results = self.pose.process(imgRGB)
#         if self.results.pose_landmarks:
#             if draw:
#                 self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)

#         return img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS

#     def getPosition(self, img, draw=True):
#         lmList= []
#         if self.results.pose_landmarks:
#             for id, lm in enumerate(self.results.pose_landmarks.landmark):
#                 h, w, c = img.shape
#                 cx, cy = int(lm.x * w), int(lm.y * h)
#                 lmList.append([id, cx, cy])
#                 if draw:
#                     cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
#         return lmList


app = Flask(__name__)

net = cv2.dnn.readNetFromTensorflow("graph_opt.pb")

BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
               "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
               "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
               "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
               ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
               ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
               ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
               ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"] ]

thr = 0.2

def getPose(frame):
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    inWidth = frameWidth 
    inHeight = frameHeight
    
    net.setInput(cv2.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))
    out = net.forward()
    out = out[:, :19, :, :]  # MobileNet output [1, 57, -1, -1], we only need the first 19 elements

    assert(len(BODY_PARTS) == out.shape[1])

    points = []
    for i in range(len(BODY_PARTS)):
        # Slice heatmap of corresponging body's part.
        heatMap = out[0, i, :, :]

        # Originally, we try to find all the local maximums. To simplify a sample
        # we just find a global one. However only a single pose at the same time
        # could be detected this way.
        _, conf, _, point = cv2.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]
        # Add a point if it's confidence is higher than threshold.
        points.append((int(x), int(y)) if conf > thr else None)

    for pair in POSE_PAIRS:
        partFrom = pair[0]
        partTo = pair[1]
        assert(partFrom in BODY_PARTS)
        assert(partTo in BODY_PARTS)

        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]

        if points[idFrom] and points[idTo]:
            cv2.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
            cv2.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv2.FILLED)
            cv2.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv2.FILLED)

    t, _ = net.getPerfProfile()
    freq = cv2.getTickFrequency() / 1000
    return frame



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
    print(type(file),"is the type of video file")
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    feedback = 0
    #det = posecamera.pose_tracker.PoseTracker()
    #print(filename)
    cap = cv2.VideoCapture('uploads/' + filename)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    #fourcc = cv2.VideoWriter_fourcc(*'avc1')
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    outputFileName = 'annotatedVideo.avi'
    out = cv2.VideoWriter('uploads/' + outputFileName, fourcc, fps, (width, height))
    #detector = PoseDetector()
    while True:
        ret,frame = cap.read()
        print("next frame")
        if not ret:
            break
        #flipped_frame = cv2.flip(frame,1)
        #out.write(flipped_frame)
        #frame, p_landmarks, p_connections = detector.findPose(frame, False)
        cv2.line(frame,(100,100),(200,200),(0,0,255), thickness=3,lineType=cv2.LINE_AA)
        #mp.drawing_utils.draw_landmarks(frame, p_landmarks, p_connections)
        #if (feedback % 6 == 0):#only detect a pose every 6 frames, to speed up computational times
        #    frame = getPose(frame)
        out.write(frame)
        


        feedback += 1
        print("frame number: ",feedback)
    cap.release()
    out.release()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    return redirect(url_for('show_video', filename=outputFileName,feedback=feedback))

@app.route('/video/<filename>')
def show_video(filename):
    feedback = None
    feedback = request.args.get('feedback')
    return render_template('video.html',filename=filename, feedback=feedback)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
