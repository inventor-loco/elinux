#!/usr/bin/env python3
"""Run the custom IMX500 YOLO model with YOLO-aware box decoding."""

from pathlib import Path

import cv2
from picamera2 import Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import NetworkIntrinsics


MODEL = Path(__file__).resolve().parent / "weights_imx_model" / "network.rpk"
THRESHOLD = 0.30
WINDOW = "IMX500 LED-strip ROI detection"


def main():
    if not MODEL.is_file():
        raise SystemExit(
            f"Missing model: {MODEL}\n"
            "Run ./pi_setup_and_test.sh to package packerOut.zip first."
        )

    # Set up network metadata before creating Picamera2, as required by its API.
    imx500 = IMX500(str(MODEL))
    intrinsics = imx500.network_intrinsics or NetworkIntrinsics()
    intrinsics.task = "object detection"
    intrinsics.labels = ["ROI"]
    intrinsics.bbox_normalization = True
    intrinsics.bbox_order = "xy"
    intrinsics.update_with_defaults()

    picam2 = Picamera2(imx500.camera_num)
    config = picam2.create_preview_configuration(
        main={"size": (1920, 1080), "format": "RGB888"},
        controls={"FrameRate": 15},
        buffer_count=12,
    )
    picam2.configure(config)

    try:
        imx500.show_network_fw_progress_bar()
        picam2.start()
        # Keep the short exposure used for the rolling-shutter LED test setup.
        picam2.set_controls({"AeEnable": False, "ExposureTime": 50, "AnalogueGain": 4.0})
        print(f"Running {MODEL}; threshold={THRESHOLD:.2f}. Press q or Esc to stop.", flush=True)

        _, input_height = imx500.get_input_size()
        frame_count = 0
        while True:
            request = picam2.capture_request()
            try:
                frame = request.make_array("main")
                metadata = request.get_metadata()
                outputs = imx500.get_outputs(metadata, add_batch=True)
                detection_count = 0

                if outputs is not None and len(outputs) >= 3:
                    boxes, scores, classes = outputs[0][0], outputs[1][0], outputs[2][0]

                    # The YOLO RPK emits normalized (y0, x0, y1, x1) boxes.
                    # Match Raspberry Pi's YOLO demo: normalize by input height,
                    # then reorder to (x0, y0, x1, y1) before coordinate mapping.
                    boxes = boxes / input_height
                    boxes = boxes[:, [1, 0, 3, 2]]

                    frame_height, frame_width = frame.shape[:2]
                    for box, score, class_id in zip(boxes, scores, classes):
                        confidence = float(score)
                        if confidence < THRESHOLD or int(class_id) != 0:
                            continue

                        x0, y0, x1, y1 = (float(value) for value in box)
                        # Picamera2's IMX500 helper takes the normalized
                        # (x0, y0, x1, y1) box and returns an ISP Rectangle.
                        coords = [x0, y0, x1, y1]
                        rect = imx500.convert_inference_coords(coords, metadata, picam2)
                        # Picamera2 releases have returned either a tuple or
                        # a libcamera Rectangle here.
                        if hasattr(rect, "x"):
                            x, y, width, height = (
                                int(rect.x), int(rect.y), int(rect.width), int(rect.height)
                            )
                        else:
                            x, y, width, height = (int(value) for value in rect)

                        # Discard invalid or fully clipped detections rather than
                        # drawing a misleading zero-area box.
                        x0p = max(0, min(frame_width - 1, x))
                        y0p = max(0, min(frame_height - 1, y))
                        x1p = max(0, min(frame_width - 1, x + width))
                        y1p = max(0, min(frame_height - 1, y + height))
                        if x1p <= x0p or y1p <= y0p:
                            print(
                                f"Invalid ROI box after coordinate conversion: "
                                f"x={x}, y={y}, w={width}, h={height}; raw={box.tolist()}",
                                flush=True,
                            )
                            continue

                        cv2.rectangle(frame, (x0p, y0p), (x1p, y1p), (0, 255, 0), 3)
                        cv2.putText(
                            frame,
                            f"ROI {confidence:.2f}",
                            (x0p, max(20, y0p - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2,
                        )
                        detection_count += 1

                frame_count += 1
                if detection_count:
                    print(f"frame {frame_count}: {detection_count} valid ROI box(es)", flush=True)

                cv2.imshow(WINDOW, cv2.resize(frame, (960, 540)))
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):
                    break
            finally:
                request.release()
    finally:
        cv2.destroyAllWindows()
        picam2.stop()


if __name__ == "__main__":
    main()
