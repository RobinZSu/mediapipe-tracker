import tkinter as tk
from tkinter import ttk 
import socket, struct
import cv2
from PIL import Image, ImageTk

from app.tracker import MP_Tracker
from utils.camera import LIST_CAMERAS, CAMERA_FPS
import TKinterModernThemes as TKMT

# Globals
# socket
DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 4242
# UDP socket
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

class TrackerApp(TKMT.ThemedTKinterFrame):
    tracker : MP_Tracker
    cap : cv2.VideoCapture
    _running : bool
    _ip : tk.StringVar
    _port : tk.IntVar

    def __init__(self):
        super().__init__("Mediapipe Head Tracker", "sun-valley", "dark")
        self._running = True
        self._ip = tk.StringVar(value=DEFAULT_IP)
        self._port = tk.IntVar(value=DEFAULT_PORT)
        self._var_cam = tk.Variable()

        self.dict_cam = {
            camera_name : (camera_idx, camera_backend, (camera_h, camera_w))
            for camera_idx, camera_name, camera_backend, (camera_w, camera_h) in LIST_CAMERAS
        }
        self.names_cam = list(self.dict_cam.keys())

        # self.root.geometry("400x400")

        """
        init tk GUI
        """
        # root
        # lbl.pack()
        self.root.resizable(False, False)

        # self.root = root
        self.frame_vis = self.addFrame("Vis", row=0)
        self.lbl_vis = self.frame_vis.Label(text='')
        self.lbl_vis.pack_forget()

        # camera selection
        self.frame_cam = self.addLabelFrame("Camera", row=1, padx=10, pady=10)
        self.list_cam = self.frame_cam.Combobox(self.names_cam, self._var_cam)
        self.list_cam.pack(padx=10, pady=10, fill='x')

        # opentrack settings
        self.frame_otk = self.addLabelFrame("OpenTrack Host Address", row=2, padx=10, pady=10, sticky="nw")
        self.frame_ip = self.frame_otk.addLabelFrame("IP", padx=10, row=0, col=0)
        self.frame_port = self.frame_otk.addLabelFrame("Port", padx=10, row=0, col=1)
        self.entry_ip = self.frame_ip.Entry(self._ip, padx=10)
        self.entry_port = self.frame_port.Entry(self._port, padx=10)


        # start button
        self.btn_start = self.Button(text="Start Tracking", command=self._start_tracking, row=3)

        # tracker
        self.cap = None
        self.tracker = None

        # bind hotkeys
        self.root.bind("<r>", self.centre_tracking)  # Press 'r' re-centre tracking
        
        # self.root.resizable(0, 0) # disable resizable
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) # onclosing
        self.run()


    def _start_tracking(self):
        camera_idx, camera_backend, (camera_w, camera_h) = self.dict_cam[self._var_cam.get()] # selected camera
        # open video capture
        cap = cv2.VideoCapture(camera_idx, camera_backend)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_h)
        cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

        # tracker instance
        self.tracker = MP_Tracker(cap, SOCKET)
        self.tracker.start(self._ip.get(), self._port.get())

        # visualize tracking
        self.update_frame()
        self.lbl_vis.pack(fill="both", expand=True)
        # swap button
        self.btn_start.configure(text="Stop", command=self._stop_tracking)

    def _stop_tracking(self):
        if self.tracker != None:
            self.tracker.stop()
            self.tracker = None
        if self.cap != None:
            self.cap.release()
            self.cap = None
        self.lbl_vis.pack_forget()
        self.btn_start.configure(text="Start Tracking", command=self._start_tracking)
        self.root.update_idletasks()

    # TK GUI bindings
    # on window close
    def on_closing(self):
        self._running = False
        if self.tracker != None:
            self.tracker.stop()
        if self.cap != None:
            self.cap.release()
        self.root.destroy()

    # centre
    def centre_tracking(self, event=None):
        try:
            self.tracker.head.center()
        except Exception:
            pass

    # update visualization
    def update_frame(self):
        if not self._running or self.tracker == None:
            return
        frame = self.tracker.frame_out
        if frame is not None:
            vis_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(vis_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.lbl_vis.imgtk = imgtk
            self.lbl_vis.configure(image=imgtk)
        self.lbl_vis.after(10, self.update_frame)
    

# MAIN
if __name__ == "__main__":
    app = TrackerApp()
    