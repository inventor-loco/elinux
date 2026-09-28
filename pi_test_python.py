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
        metadata = request.get_metadata()
        
        # Debugging prints
        print(f"--- Frame {i} ---")
        print(f"Available metadata keys: {list(metadata.keys())}")
        
        # Check if the IMX500 generated object detection metadata
        if "ObjectDetect" in metadata:
            detections = metadata["ObjectDetect"]
            
            for det in detections:
                box = det.get("box", [0, 0, 0, 0])
                conf = det.get("confidence", 0)
                
                h, w, _ = frame.shape
                x1, y1 = int(box[0] * w), int(box[1] * h)
                x2, y2 = int((box[0] + box[2]) * w), int((box[1] + box[3]) * h)
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
                cv2.putText(frame, f"ROI: {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                print(f"Found ROI! Conf: {conf:.2f} at {x1},{y1} -> {x2},{y2}")
                
        elif "Imx500NeuralNetwork" in metadata:
            # Fallback for raw tensor parsing using IMX500 helper
            outputs = imx500.get_outputs(metadata)
            if outputs is not None and len(outputs) > 0:
                for det in outputs[0]:
                    # Format typically: [class_idx, score, xmin, ymin, xmax, ymax]
                    if len(det) >= 6:
                        conf = det[1]
                        if conf < 0.1:  # Filter low confidence
                            continue
                        
                        h, w, _ = frame.shape
                        x1, y1 = int(det[2] * w), int(det[3] * h)
                        x2, y2 = int(det[4] * w), int(det[5] * h)
                        
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                        cv2.putText(frame, f"ROI: {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        print(f"Found ROI (Tensor)! Conf: {conf:.2f} at {x1},{y1} -> {x2},{y2}")

        # Save the 10th frame as a test image
        if i == 10:
            cv2.imwrite("python_test_detection.jpg", frame)
            print("Saved python_test_detection.jpg with bounding boxes!")
            
        request.release()
            
    except Exception as e:
        print(f"Error processing frame: {e}")
        import traceback
        traceback.print_exc()

picam2.stop()
print("Test completed.")
