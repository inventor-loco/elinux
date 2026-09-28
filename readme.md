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

## Model and deployment context

The original model has been verified against the source dataset: project notes record detections in all 74 images from that earlier dataset (172 detections total). The current 700-image collection is an expanded calibration set, including negative/background examples. Calibration does not require YOLO label files; retraining would require a separately prepared labeled dataset.

The intended deployment path is:

1. Start with `weights.pt` and the full calibration image set.
2. On a supported Linux machine, export and calibrate/quantize the model using the pinned IMX500 toolchain.
3. Package the converted model for the Raspberry Pi AI Camera and validate ROI detections on the camera.

The repository does not yet contain the conversion scripts or the packaged camera model. The earlier camera conversion loaded successfully but did not produce ROI detections; see `TODO.md` for troubleshooting notes and the current conversion status. Do not treat successful packaging alone as validation of detection quality.

## Environment notes

The dependency file captures the versions used or established during previous conversion work. In particular, `edge-mdt-cl` is pinned to `1.1.1`; the project notes warn against allowing it to be downgraded. Use Linux for IMX export. Windows remains suitable for maintaining files and inspecting or verifying the original model. The detailed Linux setup and known environment issues are documented in `TODO.md`.
