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

# 4. Force ultra-short exposure time (50 microseconds)
picam2.set_controls({
    "AeEnable": False, 
    "ExposureTime": 50,
    "AnalogueGain": 4.0
})

print("Camera started. Live preview active. Press 'q' to exit.")

# Make a named window that can be resized if needed
cv2.namedWindow("IMX500 Live Detection", cv2.WINDOW_NORMAL)

frame_count = 0
while True:
    try:
        # Request a frame and its associated metadata
        request = picam2.capture_request()
        frame = request.make_array("main")
        metadata = request.get_metadata()
        
        # We'll skip printing metadata keys every frame to avoid terminal spam
        # Check if the IMX500 generated object detection metadata
        found_detection = False
        
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
                found_detection = True
                
        elif "Imx500NeuralNetwork" in metadata:
            outputs = imx500.get_outputs(metadata)
            if outputs is not None and len(outputs) > 0:
                for det in outputs[0]:
                    if len(det) >= 6:
                        conf = det[1]
                        if conf < 0.1:  # Filter low confidence
                            continue
                        
                        h, w, _ = frame.shape
                        x1, y1 = int(det[2] * w), int(det[3] * h)
                        x2, y2 = int(det[4] * w), int(det[5] * h)
                        
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                        cv2.putText(frame, f"ROI: {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        found_detection = True

        if not found_detection:
            # Draw a default bounding box in the center if nothing is detected
            h, w, _ = frame.shape
            cv2.rectangle(frame, (w//4, h//4), (w*3//4, h*3//4), (255, 0, 0), 4)
            cv2.putText(frame, "DEFAULT (NO DETECTIONS)", (w//4, h//4 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Optional: scale down the display window so it fits on a Raspberry Pi screen
        display_frame = cv2.resize(frame, (960, 540))
        cv2.imshow("IMX500 Live Detection", display_frame)
        
        request.release()
        frame_count += 1
        
        # Listen for keyboard input; exit if 'q' or ESC is pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            print("Exit requested by user.")
            break
            
    except Exception as e:
        print(f"Error processing frame: {e}")
        import traceback
        traceback.print_exc()
        break

cv2.destroyAllWindows()
picam2.stop()
print(f"Test completed. Processed {frame_count} frames.")
