#!/usr/bin/env python3
import cv2
from picamera2 import Picamera2

print("Initializing Picamera2...")
picam2 = Picamera2()

# Configure the camera with the IMX500 network
config = picam2.create_preview_configuration(main={"size": (1920, 1080)})
picam2.configure(config)

print("Loading network.rpk into IMX500...")
# Enable the IMX500 object detection post-processing stage
picam2.start_imx500_object_detection(
    network_file="weights_imx_model/network.rpk",
    max_detections=300,
    threshold=0.0
)

picam2.start()
print("Camera started. Capturing frames...")

for i in range(50):
    try:
        # Request a frame and its associated metadata
        request = picam2.capture_request()
        frame = request.make_array("main")
        metadata = request.metadata
        
        # Check if the IMX500 generated object detection metadata
        if "Imx500NeuralNetwork" in metadata or "ObjectDetect" in metadata:
            detections = metadata.get("ObjectDetect", [])
            if not detections:
                detections = metadata.get("Imx500NeuralNetwork", [])
            
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
