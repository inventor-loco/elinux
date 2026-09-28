#!/usr/bin/env python3
import subprocess
import json
import threading
import socket
import cv2
import numpy as np
import time
import os

print("Starting rpicam-vid background process...")

# 1. Launch rpicam-vid
# - Output MJPEG video to a local TCP socket
# - Output parsed JSON metadata to stdout
cmd = [
    "rpicam-vid",
    "-t", "0",
    "--post-process-file", "test_config.json",
    "--shutter", "50",
    "--codec", "mjpeg",
    "--width", "960",
    "--height", "540",
    "--framerate", "15",
    "-o", "tcp://127.0.0.1:8000",
    "--listen",
    "--metadata", "-",
    "--metadata-format", "json"
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

latest_detections = []

# 2. Thread to continuously read JSON metadata from stdout
def metadata_reader():
    global latest_detections
    for line in proc.stdout:
        line = line.strip()
        if line.startswith("{"):
            try:
                data = json.loads(line)
                if "ObjectDetect" in data:
                    latest_detections = data["ObjectDetect"]
                else:
                    latest_detections = [] # Clear if no detections in this frame
            except Exception as e:
                pass

threading.Thread(target=metadata_reader, daemon=True).start()

# Give rpicam-vid a moment to initialize the socket
time.sleep(1.5)

# 3. Read MJPEG stream via TCP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(("127.0.0.1", 8000))
    print("Connected to rpicam-vid video stream!")
except Exception as e:
    print(f"Failed to connect to video stream: {e}")
    proc.terminate()
    exit(1)

cv2.namedWindow("IMX500 Live Hybrid Detection", cv2.WINDOW_NORMAL)
bytes_buffer = b''

print("Live preview active. Press 'q' or ESC to exit.")

while True:
    try:
        chunk = s.recv(4096)
        if not chunk:
            break
        bytes_buffer += chunk
        
        # Search for JPEG start (ff d8) and end (ff d9) markers
        a = bytes_buffer.find(b'\xff\xd8')
        b = bytes_buffer.find(b'\xff\xd9')
        
        if a != -1 and b != -1:
            jpg = bytes_buffer[a:b+2]
            bytes_buffer = bytes_buffer[b+2:]
            
            # Decode JPEG
            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            
            if frame is not None:
                h, w, _ = frame.shape
                
                if not latest_detections:
                    # Draw a default bounding box in the center if nothing is detected
                    cv2.rectangle(frame, (w//4, h//4), (w*3//4, h*3//4), (255, 0, 0), 4)
                    cv2.putText(frame, "DEFAULT (NO DETECTIONS)", (w//4, h//4 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                else:
                    for det in latest_detections:
                        box = det.get("box", [0, 0, 0, 0])
                        conf = det.get("confidence", 0)
                        
                        x1, y1 = int(box[0] * w), int(box[1] * h)
                        x2, y2 = int((box[0] + box[2]) * w), int((box[1] + box[3]) * h)
                        
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
                        cv2.putText(frame, f"ROI: {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                cv2.imshow("IMX500 Live Hybrid Detection", frame)
                
            if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
                break
                
    except Exception as e:
        print(f"Error in stream processing: {e}")
        break

print("Exiting...")
proc.terminate()
cv2.destroyAllWindows()
s.close()
