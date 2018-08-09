import os
import copy
import numpy as np
from flask import Flask, render_template, Response
from model.FaceDetector import VideoCamera
from time import sleep

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def gen_video(camera):
    while True:
        frame = camera.get_frame('haar')
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def gen_photo(camera):
    frame_array, faces = camera.save_and_return_frame_and_faces('haar')
    frame = camera.print_faces_on_frame(frame_array, faces)
    while True:
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'


def gen_lottery(camera):
    frame_array, faces = np.load(os.path.join('model', 'frame_array.npy')), np.load(os.path.join('model', 'faces.npy'))
    try:
        winner = np.random.randint(len(faces))
        for i in range(10*len(faces) + winner):
            frame = camera.draw_winner(copy.copy(frame_array), faces, i % len(faces))
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            sleep(i / 100)
    except ValueError:
        frame = camera.frame_to_jpg(copy.copy(frame_array))
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def gen_audio():
    sound = np.random.choice(os.listdir('sound'))
    with open(os.path.join("sound", sound), "rb") as wav:
        data = wav.read(1024)
        while data:
            yield data
            data = wav.read(1024)

@app.route('/video_feed')
def video_feed():
    return Response(gen_video(video_camera), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/photo_feed')
def photo_feed():
    return Response(gen_photo(video_camera), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/lottery_feed')
def lottery_feed():
    return Response(gen_lottery(video_camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/audio_feed')
def audio_feed():
    return Response(gen_audio(), mimetype='audio/x-wav')

@app.route('/video')
def video():
    global video_camera
    video_camera = VideoCamera()
    return render_template('video_feed.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)