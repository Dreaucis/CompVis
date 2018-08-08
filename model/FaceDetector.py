import numpy as np
import cv2 as cv
import os

# TODO: Clean up methods
# TODO: Generalize frame scaling solution

class VideoCamera():
    def __init__(self):
        self.video = cv.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def set_cascade(self, cascade_type):
        if cascade_type == 'haar':
            path = os.path.join(os.path.dirname(__file__), 'haarcascades')
            front_cascade = cv.CascadeClassifier(os.path.join(path, 'haarcascade_frontalface_default.xml'))
            profile_cascade = cv.CascadeClassifier(os.path.join(path, 'haarcascade_profileface.xml'))
        else:
            path = os.path.join(os.path.dirname(__file__), 'lbpcascades')
            front_cascade = cv.CascadeClassifier(os.path.join(path, 'lbpcascade_frontalface_improved.xml'))
            profile_cascade = cv.CascadeClassifier(os.path.join(path, 'lbpcascade_profileface.xml'))
        return front_cascade, profile_cascade

    def calculate_overlap_1d(self, min_1, max_1, min_2, max_2):
        if min_1 > max_2 or min_2 > max_1:
            return 0
        else:
            return abs(min(max_1, max_2) - max(min_1, min_2))

    def calculate_overlap_2d(self, l_1, l_2):
        x_over = [0]
        y_over = [0]
        for (x_1, y_1, w_1, h_1) in l_1:
            x_over.append(self.calculate_overlap_1d(x_1, x_1 + w_1, l_2[0], l_2[0] + l_2[2]))
            y_over.append(self.calculate_overlap_1d(y_1, y_1 + h_1, l_2[1], l_2[1] + l_2[3]))
        return max(x_over) * max(y_over)

    def detect_face(self, cascade, gray_img, scale, num_neighbours):
        return cascade.detectMultiSacle(gray_img, scale, num_neighbours)

    def add_to_faces(self, faces_tuple, gray_img, max_overlap=0.5):
        face_array = faces_tuple[0]
        pro_left = faces_tuple[1]
        pro_right = faces_tuple[2]
        for (x, y, w, h) in pro_left:
            if self.calculate_overlap_2d(face_array, [x, y, w, h]) < max_overlap:
                if len(face_array) != 0:
                    face_array = np.vstack((face_array, np.array([x, y, w, h])))
                else:
                    face_array = np.array([[x, y, w, h]])
        for (x, y, w, h) in pro_right:
            x = gray_img.shape[1] - x - w
            if self.calculate_overlap_2d(face_array, [x, y, w, h]) < max_overlap:
                if len(face_array) != 0:
                    face_array = np.vstack((face_array, np.array([x, y, w, h])))
                else:
                    face_array = np.array([[x, y, w, h]])
        return face_array

    def print_rectangles(self, face_array, img, color):
        if not isinstance(face_array, tuple):  # There are no faces
            for (x, y, w, h) in face_array:
                cv.rectangle(img, (x, y), (x + w, y + h), color, 2)

    def get_frame(self, cascade):
        """
        Detects faces in video. Press 'p' on the image window to freeze frame.

        :param cascade: String describing type of cascade (i.e. haar or lbp).
        :param max_time: Integer describing the maximum time of video capture.
        :return: Tuple containing the last frame and the position of faces in the frame
        """
        front_cascade, profile_cascade = self.set_cascade(cascade)

        # Capture frame-by-frame
        ret, frame = self.video.read()

        # Scaling down the image
        frame = cv.resize(frame, None, fx=0.5, fy=0.5)

        # Our operations on the frame come here
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Detecting faces front
        front = front_cascade.detectMultiScale(gray, 1.2, 5)
        # Detecting profile looking left
        profiles_left = profile_cascade.detectMultiScale(gray, 1.2, 5)
        # Detecting profile looking right
        gray = cv.flip(gray, 1)
        profiles_right = profile_cascade.detectMultiScale(gray, 1.2, 5)

        # Creating list of faces without overlap
        faces = self.add_to_faces((front, profiles_left, profiles_right), gray)

        # Adding rectangles to frame
        self.print_rectangles(faces, frame, (0, 255, 0))

        out_frame = cv.resize(frame, None, fx=2, fy=2, interpolation=cv.INTER_CUBIC)

        ret, jpeg = cv.imencode('.jpg', out_frame)
        return jpeg.tobytes()

    def get_frame_and_faces(self, cascade):
        """
        Detects faces in video. Press 'p' on the image window to freeze frame.

        :param cascade: String describing type of cascade (i.e. haar or lbp).
        :param max_time: Integer describing the maximum time of video capture.
        :return: Tuple containing the last frame and the position of faces in the frame
        """
        front_cascade, profile_cascade = self.set_cascade(cascade)

        # Capture frame-by-frame
        ret, frame = self.video.read()

        # Scaling down the image
        frame = cv.resize(frame, None, fx=0.5, fy=0.5)

        # Our operations on the frame come here
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Detecting faces front
        front = front_cascade.detectMultiScale(gray, 1.2, 5)
        # Detecting profile looking left
        profiles_left = profile_cascade.detectMultiScale(gray, 1.2, 5)
        # Detecting profile looking right
        gray = cv.flip(gray, 1)
        profiles_right = profile_cascade.detectMultiScale(gray, 1.2, 6)

        # Creating list of faces without overlap
        faces = self.add_to_faces((front, profiles_left, profiles_right), gray)

        return frame, faces

    def save_and_return_frame_and_faces(self, cascade):
        frame_array, faces = self.get_frame_and_faces(cascade)
        np.save(os.path.join('model', 'frame_array'), frame_array)
        np.save(os.path.join('model', 'faces'), faces)
        return frame_array, faces

    def print_faces_on_frame(self, frame, faces):
        self.print_rectangles(faces, frame, (0, 255, 0))
        out_frame = cv.resize(frame, None, fx=2, fy=2, interpolation=cv.INTER_CUBIC)
        ret, jpeg = cv.imencode('.jpg', out_frame)
        return jpeg.tobytes()

    def frame_and_face_to_jpg(self, frame, faces):
        # Adding rectangles to frame
        self.print_rectangles(faces, frame, (0, 255, 0))

        frame = cv.resize(frame, None, fx=2, fy=2, interpolation=cv.INTER_CUBIC)

        ret, jpeg = cv.imencode('.jpg', frame)
        return jpeg.tobytes()

    def frame_to_jpg(self, frame):
        frame = cv.resize(frame, None, fx=2, fy=2, interpolation=cv.INTER_CUBIC)
        ret, jpeg = cv.imencode('.jpg', frame)
        return jpeg.tobytes()

    def draw_winner(self, frame, faces, count):
        # Sampling a random face and adding a red rectangle
        if len(faces) > 0:
            self.print_rectangles([faces[count]], frame, (0, 0, 255))
        out_frame = cv.resize(frame, None, fx=2, fy=2, interpolation=cv.INTER_CUBIC)
        ret, jpeg = cv.imencode('.jpg', out_frame)
        return jpeg.tobytes()

    def get_lottery_frame(self, cascade):
        """
        Selects a face in a frame

        :param cascade: String describing type of cascade (i.e. haar or lbp).
        :param max_time: Integer describing the maximum time of video capture.
        :return: Tuple containing the last frame and the position of faces in the frame
        """
        front_cascade, profile_cascade = self.set_cascade(cascade)

        # Capture frame-by-frame
        ret, frame = self.video.read()

        # Scaling down the image
        frame = cv.resize(frame, None, fx=0.5, fy=0.5)

        # Our operations on the frame come here
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Detecting faces front
        front = front_cascade.detectMultiScale(gray, 1.2, 5)
        # Detecting profile looking left
        profiles_left = profile_cascade.detectMultiScale(gray, 1.2, 5)
        # Detecting profile looking right
        gray = cv.flip(gray, 1)
        profiles_right = profile_cascade.detectMultiScale(gray, 1.2, 6)

        # Creating list of faces without overlap
        faces = self.add_to_faces((front, profiles_left, profiles_right), gray)

        # Adding rectangles to frame
        self.print_rectangles(faces, frame, (0, 255, 0))

        # Sampling a random face and adding a red rectangle
        if len(faces) > 0:
            sampled_face = np.random.choice(len(faces))
            self.print_rectangles([faces[sampled_face]], frame, (0, 0, 255))

        out_frame = cv.resize(frame, None, fx=2, fy=2, interpolation=cv.INTER_CUBIC)

        ret, jpeg = cv.imencode('.jpg', out_frame)
        return jpeg.tobytes()
