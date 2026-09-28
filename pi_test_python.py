#!/usr/bin/env python3
import cv2
from picamera2 import Picamera2
from picamera2.devices.imx500 import IMX500

print("Initializing IMX500 and Picamera2...")
# 1. Initialize IMX500 with the RPK file
imx500 = IMX500("weights_imx_model/network.rpk")

# 2. Initialize Picamera2 using the specific camera number for the IMX500
picam2 = Picamera2(imx500.camera_num)

# 3. Configure and start the camera
config = picam2.create_preview_configuration(main={"size": (1920, 1080)})
picam2.start(config)

print("Camera started. Capturing frames...")

for i in range(50):
    try:
        # Request a frame and its associated metadata
        request = picam2.capture_request()
        frame = request.make_array("main")
        metadata = request.metadata
        
        # Check if the IMX500 generated object detection metadata
        if "ObjectDetect" in metadata:
            detections = metadata["ObjectDetect"]
            
            for det in detections:
                # The bounding box is usually normalized [x, y, width, height]
                box = det.get("box", [0, 0, 0, 0])
                conf = det.get("confidence", 0)
                
                h, w, _ = frame.shape
                x1 = int(box[0] * w)
                y1 = int(box[1] * h)
                x2 = int((box[0] + box[2]) * w)
                y2 = int((box[1] + box[3]) * h)
                
                # Draw the bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
                cv2.putText(frame, f"ROI: {conf:.2f}", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                print(f"Found ROI! Conf: {conf:.2f} at {x1},{y1} -> {x2},{y2}")

        # Save the 10th frame as a test image
        if i == 10:
            cv2.imwrite("python_test_detection.jpg", frame)
            print("Saved python_test_detection.jpg with bounding boxes!")
            break
            
    except Exception as e:
        print(f"Error processing frame: {e}")

picam2.stop()
print("Test completed.")
