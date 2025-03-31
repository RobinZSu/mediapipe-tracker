# mediapipe-tracker  

Lightweight 6dof webcam head tracker for opentrack I have been using for flight simulation games. Based on mediapipe. Curret build with `Python 3.9.20`  

## Hardware requirements

- A `DirectShow` or `V4L2` webcam, preferbly one that supports uncompressed protocols such as `YUV2` for lower latency.

## Usage  

Assuming you're using windows, simply download and run the latests `mp_tracker.exe`. Then, go to `opentrack` to select the input method `UDP over network` and set the port accordingly.  

You may also find in this repository a `opentrack_config.ini` which includes my mapping setting in opentrack.

To reset / re-centre position and rotation, press `<r>`.

## Building / Running from Source 

Clone this repo
```bash
git clone https://github.com/RobinZSu/mediapipe-tracker.git
```

Install dependencies
```bash
pip install -r requirements
```

Running  
```bash
python -m app.main
```

Building (with `pyinstaller`)  
```bash
pyinstaller --onefile --collect-data mediapipe --collect-data TKinterModernThemes app/main.py
```  

### Other Notes  

#### Camera Resolution / Refresh Rate
I was not able to find a convenient way in Python to obtain the supported video capture resolution / refresh rates of webcams. So you may want to modify the Python script used to obtain the supported resolutions found in the dropdown menu in the GUI. Namely the fileds `DEFAULT_RES` and `CAMERA_FPS` in `utils/camera.py`  

#### Tracking with `vSeeFace`  

As an early prototype there is also a tracker implementation based on the tracking information from [vSeeFace](https://www.vseeface.icu/).  
```bash
python -m prototypes.omc
```
You would need to enable the `Send data with OSC VMC protocol` setting in in the vSeeFace app.

## Credits  

- FOXTracker (https://github.com/xuhao1/FOXTracker) - for inspiring this project  

- Google MediaPipe (https://github.com/google-ai-edge/mediapipe) - used for facial landmark tracking

- TKinterModernThemes (https://github.com/RobertJN64/TKinterModernThemes) - used to build a basic Tkinter GUI that doesn't look hideous. 
