import numpy as np
import cv2
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.backend import set_session
from flask import Flask, render_template,Response
import tensorflow as tf
from gtts import gTTS
global graph
global writer
from skimage.transform import resize


sess = tf.Session()
graph = tf.get_default_graph()
writer=None

set_session(sess)
model = load_model('signlanguage1.h5')

vals = ['A','B','C','D','E','F','G','H','I']

app = Flask(__name__)

print("[INFO] accessing video stream...")
camera = cv2.VideoCapture(1)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
pred=""


@app.route('/')
def index():
    return render_template('index.html')


def detect(frame):
    global pred
    global sess
    global graph
    img = resize(frame,(64,64,1))
    x = image.img_to_array(img)
    x = np.expand_dims(x,axis=0)
    #if(np.max(x)>1):
     #   img = img/255.0
    with graph.as_default():
        set_session(sess)
        predictions = model.predict_classes(x)
    print(predictions)
    pred=vals[predictions[0]]
    print(pred)


def gen():
    while True:
        success, frame = camera.read() 
        frame = cv2.resize(frame,(640,480))
        detect(frame)
        frame = cv2.putText(frame, 'Prediction: '+pred, (00,435), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2, cv2.LINE_AA, False)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=='__main__':
    app.run()
