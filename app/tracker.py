import cv2
import time
import threading
import socket, struct
import mediapipe as mp

from .geometry import Head
from utils.camera import CAMERA_FPS

# Consts
# camera capture frame (for visualization)
frame = None
# tracking rate (meadiapipe)
dt_track = 1 / CAMERA_FPS # dt
# tracking point visualization colors
COLORS = [
  (255, 0, 0), 
  (255, 255, 0), 
  (255, 255, 255), 
  (0, 255, 255),
  (0, 255, 0)
]

# mediapipe APIs
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

"""
Mediapipe head tracker class
"""
class MP_Tracker():
    cap : cv2.VideoCapture # opencv capture
    sock : socket.socket # datagram socket
    head : Head # head 
    frame_out : cv2.Mat # output frame (for visualization)]

    # capture frame dimensions
    _w : int
    _h : int 
    # socket and ip of opentrack
    _ip : str
    _port : int
    # app running
    _running : bool
    # thread
    _t_tracking : threading.Thread

    # init
    def __init__(self, cap: cv2.VideoCapture, sock: socket.socket):
        self.cap = cap
        self.sock = sock
        self.head = None
        self.frame_out = None 

    # head tracking thread using mediapipe
    def _mp_loop(self):
        head = self.head
        while self._running:
            # Read a frame from the webcam
            ret, cap_frame = self.cap.read()
            
            # Convert the BGR image to RGB before processing.
            results = self.face_mesh.process(cv2.cvtColor(cap_frame, cv2.COLOR_BGR2RGB))

            # Print and draw face mesh landmarks on the image.
            if not results.multi_face_landmarks:
                continue

            for face_landmarks in results.multi_face_landmarks:
                points = head.get_points(face_landmarks)
                for point in points:
                    # Convert the normalized coordinate to pixel coordinates
                    x_pixel = int(point.x * self._w)
                    y_pixel = int(point.y * self._h)

                    # Define the circle radius and color
                    radius = 5

                    # Draw the circle on the frame
                    cv2.circle(cap_frame, (x_pixel, y_pixel), radius, point.color, -1)
                break

            # got all points, calculate head rotation and position
            head.update_rotation()
            head.update_position()
            
            # Flip the image horizontally for a mirrored selfie-view display.
            cap_frame = cv2.flip(cap_frame, 1)
            cv2.putText(cap_frame, f"position: {head.x:.2f} {head.y:.2f} {head.z:.2f}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(cap_frame, f"rotation: {head.pitch:.2f} {head.roll:.2f} {head.yaw:.2f}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            self.frame_out = cap_frame

            # stream over udp socket
            # Format the data as a string (use the opentrack protocol)
            buf = bytearray(8 * 6)
            data = [head.x, head.y, head.z, head.pitch, head.roll, head.yaw] 

            # Send the data over UDP
            struct.pack_into('dddddd', buf, 0, *data)
            self.sock.sendto(buf, (self._ip, self._port))
            time.sleep(dt_track)

    # start tracking
    def start(self, ip:str, port:int):
        # opentrack ip and port
        self._ip = ip
        self._port = port

        # running
        self._running = True

        # Mediapipe facemesh
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.95,
            min_tracking_confidence=0.95
        )

        # Start tracking
        ret, frame = self.cap.read() # read first frame
        self._h, self._w = frame.shape[:2] # frame dimensions


        # first time center
        while self.head == None:
            # Read a frame from the webcam
            ret, frame = self.cap.read()

            # Convert the BGR image to RGB before processing.
            results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Skip frame if now face detected
            if not results.multi_face_landmarks:
                continue

            for face_landmarks in results.multi_face_landmarks:
                self.head = Head(face_landmarks) 
                break # capture only one head

        # Init complete, start update loop in saperate thread
        self._t_tracking = threading.Thread(target=self._mp_loop, daemon=True)
        self._t_tracking.start() # start daemon

    # stop tracking
    def stop(self):
        self._running = False
        self._t_tracking.join() # wait till thread terminates
