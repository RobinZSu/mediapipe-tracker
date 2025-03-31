import cv2
from cv2_enumerate_cameras import enumerate_cameras
# from cv2_enumerate_cameras import supported_backends
from cv2.videoio_registry import getBackendName

import platform

LIST_CAMERAS = []

prefered_backend = cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_V4L2

DEFAULT_RES = [(1280, 720), (640, 360), (320, 240)] # TODO: custom resolutions
CAMERA_FPS = 30 # TODO: enumerate supported fps / use user setting
 
# enumerate supported cameras and resolutions
for camera_info in enumerate_cameras():
    if camera_info.index != prefered_backend:
        continue
    for w, h in DEFAULT_RES:
        try:
            cap = cv2.VideoCapture(camera_info.index, camera_info.backend)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            cap.set(cv2.CAP_PROP_FPS, 30) 
        except Exception:
            if cap.isOpened() :
                cap.release() 
                continue

        if not cap.isOpened():
            continue

        # release capture device
        cap.release()
        # add supported camera and spec to list
        cam_name = f"[{getBackendName(camera_info.index)}] {camera_info.name} ({w}x{h})"
        LIST_CAMERAS.append((camera_info.index, cam_name, camera_info.backend, (w, h)))
