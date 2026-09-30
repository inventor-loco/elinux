# Custom YOLO Model for Detecting LED Strips

Author: Dr. Eleni Niarchou  
Collaborators: (predoc) Atiya Fatima Usmani, Dr. Vicente Matus

## What this repository contains

This repository collects the trained object-detection model and the data and configuration used in work to prepare it for the Raspberry Pi AI Camera (Sony IMX500). It is primarily a set of model and deployment artifacts; it does not currently include the Python training, inference, or conversion scripts.

- `weights.pt` — trained Ultralytics YOLO12 detection model. It has one class, `ROI`, and uses 640 × 640 model input. The project notes report about 3.0 million parameters and 8.1 GFLOPs.
- `dataset/` — 700 JPEG images used as calibration examples for conversion/quantization. It includes images both with and without ROIs. These images are not, by themselves, a labeled training dataset; no YOLO annotation files are included.
- `imx.yaml` — Ultralytics dataset configuration. Its current `path` is a Windows-specific path (`C:/Users/eleni/Desktop`), so update it to the dataset's actual location before using it on another machine. The class mapping is `0: ROI`.
- `imx500_requirements.txt` — pinned Python package versions recorded for the IMX500 conversion environment. The conversion toolchain is platform-sensitive: the actual Ultralytics IMX export must run on Linux, not Windows.
- `TODO.md` — detailed setup history, verified model behavior, conversion guidance, and known blockers. Consult it before continuing conversion work.
- `pi_setup_and_test.sh` — on the Pi, checks camera Python dependencies, packages `weights_imx_model/packerOut.zip` into `network.rpk`, then starts the test demo.
- `pi_run_demo.sh`, `pi_test_python.py` — run the Picamera2 test with YOLO box normalization/order handling and draw valid ROI boxes. This is the supported path for the current model output.
- `test_config.json` — reference `rpicam-apps` configuration. Its standard object-detection stage does not decode this model's box coordinates correctly.
- `pi_live_hybrid.py` — older `rpicam-vid` metadata experiment, retained for reference.

## Model and deployment context

The original model has been verified against the source dataset: project notes record detections in all 74 images from that earlier dataset (172 detections total). The current 700-image collection is an expanded calibration set, including negative/background examples. Calibration does not require YOLO label files; retraining would require a separately prepared labeled dataset.

The intended deployment path is:

1. Start with `weights.pt` and the full calibration image set.
2. On a supported Linux machine, export and calibrate/quantize the model using the pinned IMX500 toolchain.
3. Package the converted model for the Raspberry Pi AI Camera and validate ROI detections on the camera.

The repository does not include the conversion scripts. The current `packerOut.zip` contains four outputs including `MultiClassNMS` boxes, scores, classes, and count, and the Pi reports ROI detections. The native `rpicam-apps` object-detection stage treats the model's normalized YOLO boxes as pixel coordinates and clips them to zero area. The Picamera2 test applies the YOLO box normalization and coordinate ordering used by Raspberry Pi's YOLO examples; the Pi run should confirm that this fixes the displayed boxes.

## Running the demo on the Raspberry Pi

Copy the newly generated `packerOut.zip` into `weights_imx_model/` on the Pi, replacing the older archive if present. Then run the setup and camera test from the repository root (or invoke it by its full path):

```bash
./pi_setup_and_test.sh
```

The script creates `weights_imx_model/network.rpk` with `imx500-package` and starts the Picamera2 preview. It requires Picamera2 and OpenCV (`python3-picamera2` and `python3-opencv` on Raspberry Pi OS). If packaging has already been done, run the preview directly:

```bash
./pi_run_demo.sh
```

Look for ROI boxes in the preview and check the terminal for messages reporting valid boxes. Zero-area or invalid boxes are reported instead of drawn. The 50 µs shutter is required for the rolling-shutter LED communication setup; do not increase it to make the scene brighter.

## Environment notes

The dependency file captures the versions used or established during previous conversion work. In particular, `edge-mdt-cl` is pinned to `1.1.1`; the project notes warn against allowing it to be downgraded. Use Linux for IMX export. Windows remains suitable for maintaining files and inspecting or verifying the original model. The detailed Linux setup and known environment issues are documented in `TODO.md`.
