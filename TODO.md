# IMX500 YOLO12 Object Detection — Development TODO

## 1. Project Goal

Deploy a custom-trained **YOLO12 object detection model** to:

- Raspberry Pi 5
- Raspberry Pi AI Camera
- Sony IMX500 sensor

The model has one object class:

```text
ROI
```

The desired final result is:

```text
YOLO12 weights.pt
        ↓
Linux IMX500 conversion
        ↓
IMX500-compatible ONNX
        ↓
IMX500 packer
        ↓
packerOut.zip
        ↓
Raspberry Pi imx500-package
        ↓
network.rpk
        ↓
Raspberry Pi AI Camera
        ↓
ROI detections
```

The original YOLO model works correctly. The main unresolved problem is that the first successfully converted IMX500 model loaded onto the camera but produced no ROI detections.

A new Linux PC is now going to be used for the final conversion instead of the Raspberry Pi itself.

---

# 2. Hardware

## Raspberry Pi

- Raspberry Pi 5
- Debian Trixie 64-bit
- Architecture: `aarch64`
- Python: `3.13.5`

## Camera

- Raspberry Pi AI Camera
- Sony IMX500

The official Raspberry Pi IMX500 MobileNet SSD model works on the camera, proving that:

- camera hardware works
- IMX500 firmware works
- Raspberry Pi camera software works
- IMX500 postprocessing works
- normal camera exposure works

---

# 3. Original Model

Original trained model:

```text
weights.pt
```

Originally located in:

```text
/content/weights.pt
```

Windows copy:

```text
C:\Users\eleni\Desktop\weights.pt
```

Model information:

```text
Ultralytics: 8.4.153
Task: detect
Classes: 1
Class 0: ROI
Input: 640 x 640
Parameters: ~3,005,843
GFLOPs: ~8.1
```

Original ONNX:

```text
Input:  [1, 3, 640, 640]
Output: [1, 5, 8400]
```

---

# 4. Original Model Verification

The original model works correctly.

Example:

```text
frame_114.jpg
```

Image size:

```text
1920 x 1080
```

Original YOLO model detected:

```text
2 detections

confidence ~0.9043
box:
[150.3962, 5.4390, 371.2214, 1037.6980]

confidence ~0.8827
box:
[751.3450, 6.3797, 933.0117, 1068.9663]
```

The original model detected objects in all 74 images of the original dataset:

```text
74 images
172 total detections
```

Later Windows testing also reproduced the original model behavior.

Therefore:

**Do not retrain the model unless new evidence shows the model itself is defective.**

---

# 5. Current Dataset

The dataset has now been expanded to:

```text
700 images
```

The dataset intentionally contains:

- images containing ROI
- images containing no ROI
- varied scene/background examples

These no-ROI images SHOULD be retained.

They are useful for calibration of the already-trained model because they represent background/negative examples.

The dataset is currently intended for final IMX500 calibration/conversion.

---

# 6. Important Dataset Distinction

For this project:

## IMX500 calibration

Images do NOT need YOLO `.txt` annotation files merely to be used as calibration images.

The 700 images are being used to calibrate/quantize the existing trained model.

## Retraining

Retraining is a separate matter and would require the normal YOLO dataset/label structure.

Do not start retraining unless specifically required.

---

# 7. Existing Windows Files

Current useful files:

```text
C:\Users\eleni\Desktop\weights.pt
C:\Users\eleni\Desktop\imx.yaml
C:\Users\eleni\Desktop\imx500_requirements.txt
C:\Users\eleni\Desktop\dataset\
C:\Users\eleni\Desktop\calibration10\
```

The dataset now contains 700 images.

`calibration10` is an old 10-image calibration set. It can remain, but it should NOT be used for the final conversion.

---

# 8. Windows YAML

Current Windows YAML:

```yaml
path: C:/Users/eleni/Desktop
train: dataset
val: dataset

names:
  0: ROI
```

Do NOT use the Windows path directly on Linux.

Create a Linux-specific YAML when setting up the new Linux PC.

Example structure:

```yaml
path: /home/YOUR_USERNAME/imx500_work
train: dataset
val: dataset

names:
  0: ROI
```

Use the actual Linux path.

---

# 9. Known-Good Conversion Package Versions

These versions were established during the previous conversion work and should be preserved.

Use:

```text
Ultralytics              8.4.153
ONNX                     1.17.0
edge-mdt                 1.3.0
edge-mdt-cl              1.1.1
edge-mdt-tpc             1.3.0
imx500-converter         3.18.2
model-compression-toolkit 2.5.1
mct-quantizers           1.6.0
sdspconv                 3.18.1
```

Java:

```text
Java 21
```

Important:

```text
edge-mdt-cl MUST remain 1.1.1
```

Do not allow Ultralytics to automatically downgrade it to 1.0.0.

Before importing Ultralytics, use:

```python
import os
os.environ["ULTRALYTICS_SKIP_REQUIREMENTS_CHECKS"] = "1"
```

---

# 10. Previous Successful Colab Environment

A working environment was established with approximately:

```text
edge-mdt 1.3.0
imx500-converter 3.18.2
model-compression-toolkit 2.5.1
edge-mdt-tpc 1.3.0
sdspconv 3.18.1
uni-model 10.1.2
uni-pytorch 3.18.2
edge-mdt-cl 1.1.1
mct-quantizers 1.6.0
protobuf 4.25.5
networkx 3.0
Ultralytics 8.4.153
ONNX 1.17.0
```

Java 21 was used.

---

# 11. Important MCT/ONNX Issue

MCT and mct-quantizers cache whether ONNX is available when certain modules are imported.

We previously encountered:

```text
ONNX must be installed to use 'FakelyQuantONNXPyTorchExporter'
```

even though ONNX was actually installed.

Cause:

```python
importlib.util.find_spec("onnx")
```

had been evaluated before ONNX became available/importable.

Relevant flags included:

```text
model_compression_toolkit.verify_packages.FOUND_ONNX
mct_quantizers.common.constants.FOUND_ONNX
```

The correct approach is:

1. Install ONNX first.
2. Make sure ONNX is discoverable.
3. Only then import MCT/exporter modules.
4. If necessary, reload the exporter facade after correcting the ONNX state.

A successful check previously showed:

```text
ONNX 1.17.0
MCT 2.5.1
mct_quantizers 1.6.0
ONNX discoverable: True
MCT FOUND_ONNX: True
MCT Quantizers FOUND_ONNX: True
```

The exporter facade then exposed the real:

```text
FakelyQuantONNXPyTorchExporter
```

rather than the stub that raises the ONNX error.

---

# 12. Failed Approach — Windows Direct IMX Export

Windows/Spyder environment was successfully prepared.

However:

```python
model.export(format="imx", imgsz=640, ...)
```

failed immediately on Windows with:

```text
Export only supported on Linux.
```

Therefore:

**Do not attempt the actual Ultralytics IMX export on Windows again.**

Windows is still useful for:

- inspecting the original model
- verifying detections
- preparing/copying data
- maintaining the project

But the actual IMX export must be performed on Linux.

---

# 13. Failed Approach — Raspberry Pi as Conversion Machine

We attempted to use the Raspberry Pi's own Debian Linux instead of installing another OS.

The Pi has:

```text
Python 3.13.5
ARM64/aarch64
```

A venv was created:

```text
~/imx500-venv
```

Then a second environment:

```text
~/imx500-venv2
```

The second environment was created with:

```bash
python3 -m venv --system-site-packages ~/imx500-venv2
```

This allowed the environment to see Debian's PyTorch.

PyTorch:

```text
2.6.0+debian
```

works.

---

# 14. Raspberry Pi Packages That Worked

Inside `imx500-venv2`:

```text
PyTorch 2.6.0+debian
imx500-converter 3.18.2
sdspconv 3.18.1
```

were successfully imported.

However, the complete conversion dependency chain could not be satisfied.

---

# 15. Raspberry Pi OR-Tools Blocker

`sdspconv 3.18.1` requires:

```text
conv-allocator
```

The available versions are:

```text
conv-allocator 3.18.1
conv-allocator 3.17.1
```

`conv-allocator 3.18.1` requires:

```text
ortools == 9.9.3963
```

The Raspberry Pi Python 3.13 ARM64 environment only provides:

```text
ortools 9.12.4544
ortools 9.13.4784
ortools 9.14.6206
ortools 9.15.6755
```

There is no:

```text
ortools 9.9.3963
```

available for this Python/architecture combination.

Debian also has no:

```text
python3-ortools
```

package.

A source download of:

```text
conv-allocator==3.18.1
```

also failed because no source distribution was available from the configured indexes.

Therefore:

**Do not try to force OR-Tools 9.12+ into the Pi conversion environment without evidence of compatibility.**

The Pi should NOT be used as the conversion machine.

The Pi should remain the deployment/test machine.

---

# 16. Previous Successful Small IMX Conversion

A 10-image calibration conversion in Colab succeeded.

Command was approximately:

```python
model.export(
    format="imx",
    imgsz=640,
    data="/content/imx_test.yaml",
    fraction=1.0
)
```

It produced:

```text
/content/weights_imx_model/model_imx.onnx
```

This proved that the overall IMX export pipeline can work.

However:

**This was only a 10-image calibration run and should NOT be treated as the final model.**

---

# 17. Previous Successful IMX Packing

The converted 10-image model was successfully passed through:

```bash
imxconv-pt \
  -i /content/weights_imx_model/model_imx.onnx \
  -o /content/imx_final \
  --no-input-persistency \
  --overwrite-output
```

This produced:

```text
/content/imx_final/packerOut.zip
```

approximately 2.3 MB.

Therefore:

```text
IMX ONNX → imxconv-pt
```

works.

---

# 18. Raspberry Pi IMX500 Packaging

The generated `packerOut.zip` was copied to the Pi.

Pi command:

```bash
imx500-package \
  -i /home/atiya_lpa/packerOut_new.zip \
  -o /home/atiya_lpa/imx500_model_new
```

worked.

Produced:

```text
/home/atiya_lpa/imx500_model_new/network.rpk
```

approximately 3 MB.

Therefore:

```text
packerOut.zip → network.rpk
```

works on the Pi.

---

# 19. RPK Memory

The custom RPK fit in IMX500 memory.

Memory report:

```text
Runtime Memory Physical Size: 4.48 MB
Model Memory Physical Size: 2.58 MB
Reserved: 1 KB
Memory Usage: 7.06 MB
Total Available: 8 MB
Memory Utilization: 89%
Fit In Chip: true
Input Persistent: false
```

Therefore memory capacity is NOT the primary failure.

---

# 20. Custom RPK Graph Structure

The converted model contains NMS.

Relevant graph:

```text
MultiClassNms
MultiClassNMSWithIndices
```

The graph is NOT missing NMS.

NMS input shapes:

```text
8400 x 1 x 4
8400 x 1
```

NMS output:

```text
300 x 4
```

There are four output tensors.

Logical output dimensions from `dnnParams.xml`:

```text
ordinal 3 → 1
ordinal 2 → 300
ordinal 1 → 300
ordinal 0 → 300 x 4
```

The Pi postprocessor expects four output tensors.

Therefore the custom graph appears structurally compatible with the Pi's object-detection postprocessor.

---

# 21. Custom RPK Input

The custom RPK has:

```text
inputTensorWidth=640
inputTensorHeight=640
inputTensorFormat=RGB
```

Normalization values include:

```text
inputTensorNorm_K00=0x0400
inputTensorNorm_K02=0x0000
inputTensorNorm_K03=0x0000
inputTensorNorm_K11=0x0400
inputTensorNorm_K13=0x0000
inputTensorNorm_K20=0x0000
inputTensorNorm_K22=0x0400
inputTensorNorm_K23=0x0000
inputTensorNorm_YGain=0x0020
inputTensorNorm_YAdd=0x0000
```

The official Raspberry Pi MobileNet SSD RPK uses different values, including:

```text
inputTensorNorm_YAdd=0x0180
```

Do NOT blindly copy the official SSD normalization to the custom model.

The correct preprocessing for the YOLO model still needs to be verified.

---

# 22. Failed Camera Test

The 10-image calibrated custom RPK:

- loaded successfully to the IMX500
- fit in memory
- camera ran
- no ROI detections were produced

We tested the object detector with:

```json
"threshold": 0.0
```

and still got no detections.

Therefore the issue is not simply an excessively high detection threshold.

---

# 23. Camera/Postprocessor Investigation

The Pi postprocessor library:

```text
/usr/lib/aarch64-linux-gnu/rpicam-apps-postproc/imx500-postproc.so
```

contains:

```text
ObjectDetection::processOutputTensor
max_detections
classes
Invalid number of tensors
expected 4
Invalid tensor size
Unexpected value for num_detections
No output tensor found in metadata!
```

The custom camera test did NOT report those errors.

It showed the custom postprocessing stage being loaded:

```text
Reading post processing stage "imx500_object_detection"
```

and the camera ran normally.

This suggests that the model wasn't simply rejected by the postprocessor due to an obvious four-output/metadata mismatch.

---

# 24. ONNX Runtime Limitation

The quantized IMX ONNX cannot be loaded normally by standard ONNX Runtime because it contains custom MCT quantization operations such as:

```text
mct_quantizers:ActivationPOTQuantizer
```

Therefore:

```text
onnxruntime.InferenceSession(...)
```

is NOT a straightforward validation method for the final quantized IMX model.

The original non-quantized YOLO ONNX can still be inspected/tested normally.

---

# 25. Calibration Lessons

Previous conversion attempts used:

```text
10 images
74 images
160 images
194 images
```

The larger conversions became extremely slow in Colab.

MCT also warned that more calibration images would be preferable, with >300 mentioned as a recommendation.

The new dataset has:

```text
700 images
```

This should be used for the proper final conversion.

However, the new Linux PC must first be prepared with the correct conversion environment.

---

# 26. Current Raspberry Pi State

Do NOT modify the Pi further until a new final RPK is ready.

The Pi already has the IMX500 software stack.

Relevant tools:

```text
/usr/bin/imx500-package
/usr/bin/rpicam-hello
```

Installed IMX500 packages include:

```text
imx500-all 1.13.0-1
imx500-firmware 0.FF23+3
imx500-models 1:1.0.0-1
imx500-tools 0~20241022+2-1+trixie
rpicam-apps-imx500-postprocess 1.13.0-1
```

Existing custom model:

```text
/home/atiya_lpa/imx500_model_new/network.rpk
```

Keep it for reference.

Existing package:

```text
/home/atiya_lpa/packerOut_new.zip
```

can also be retained for reference.

---

# 27. Current Recommended Architecture

Use:

```text
Windows PC
    │
    ├── weights.pt
    ├── dataset/ (700 images)
    └── project files
          │
          ▼
Separate Linux PC
    │
    ├── Python conversion environment
    ├── Ultralytics
    ├── IMX500 converter
    ├── MCT
    ├── sdspconv
    └── Java 21
          │
          ▼
    IMX500 model conversion
          │
          ▼
    imxconv-pt
          │
          ▼
    packerOut.zip
          │
          ▼
Raspberry Pi 5
    │
    ├── imx500-package
    └── network.rpk
          │
          ▼
Raspberry Pi AI Camera
```

---

# 28. Immediate Next Tasks

## TASK 1 — Identify Linux PC

On the new Linux PC run:

```bash
cat /etc/os-release
python3 --version
uname -m
java -version
```

Do NOT install packages until the output is known.

---

## TASK 2 — Check available Python versions

We want to avoid the Raspberry Pi's Python 3.13 dependency problem.

Check:

```bash
ls /usr/bin/python3*
```

Prefer a Python version compatible with the known conversion stack, ideally Python 3.10 or another version for which the required dependencies are available.

---

## TASK 3 — Create clean conversion environment

Create a dedicated environment.

Do not reuse an existing unrelated Python environment.

---

## TASK 4 — Install exact versions

Install:

```text
Ultralytics 8.4.153
ONNX 1.17.0
edge-mdt 1.3.0
edge-mdt-cl 1.1.1
edge-mdt-tpc 1.3.0
imx500-converter 3.18.2
model-compression-toolkit 2.5.1
mct-quantizers 1.6.0
sdspconv 3.18.1
```

and Java 21.

Verify all imports before running conversion.

---

## TASK 5 — Prevent dependency auto-downgrade

Before importing Ultralytics:

```python
import os
os.environ["ULTRALYTICS_SKIP_REQUIREMENTS_CHECKS"] = "1"
```

Verify:

```text
edge-mdt-cl == 1.1.1
```

---

## TASK 6 — Copy project

Create a Linux project directory containing:

```text
weights.pt
dataset/
imx.yaml
```

The dataset should contain all 700 images.

---

## TASK 7 — Create Linux YAML

Do not reuse the Windows path.

Use a Linux path, for example:

```yaml
path: /home/USER/imx500_work
train: dataset
val: dataset

names:
  0: ROI
```

---

## TASK 8 — Verify original model

Before attempting IMX conversion, run the original `weights.pt` on Linux against a few images.

Verify that detections match the Windows behavior.

This prevents wasting time debugging a conversion when the source environment is wrong.

---

## TASK 9 — Run final IMX conversion

Use the 700-image dataset for calibration.

Do not use the old `calibration10` set for the final conversion.

Expect this to take significant time.

Do NOT interrupt merely because it reaches a stage such as:

```text
64it
```

The previous 64-iteration behavior occurred during heavy conversion work.

However, monitor CPU/RAM/disk usage and distinguish genuine progress from a dead process.

---

## TASK 10 — Validate conversion artifacts

Before transferring anything to the Pi, inspect:

```text
model_imx.onnx
packer output
dnnParams.xml
model_imx.pbtxt
MemoryReport
```

Confirm:

- input is 640 × 640
- RGB input
- four output tensors
- NMS is present
- model fits in IMX500 memory
- no unexpected export errors

---

## TASK 11 — Run `imxconv-pt`

Use:

```bash
imxconv-pt \
  -i <model_imx.onnx> \
  -o <output_directory> \
  --no-input-persistency \
  --overwrite-output
```

Confirm:

```text
packerOut.zip
```

is produced.

---

## TASK 12 — Transfer to Raspberry Pi

Copy the new:

```text
packerOut.zip
```

to the Pi.

Do NOT overwrite the old RPK yet.

Use a new directory/name for the new experiment.

---

## TASK 13 — Package new RPK

On Pi:

```bash
imx500-package \
  -i <new_packerOut.zip> \
  -o <new_output_directory>
```

Confirm:

```text
network.rpk
```

is produced.

---

## TASK 14 — Test camera

Use a dedicated custom postprocessing JSON.

Initially keep:

```json
{
    "imx500_object_detection": {
        "max_detections": 300,
        "threshold": 0.0,
        "network_file": "/path/to/new/network.rpk",
        "classes": ["ROI"]
    },
    "object_detect_draw_cv": {
        "line_thickness": 6
    }
}
```

Use normal camera exposure.

Do NOT force an extremely short shutter speed.

---

# 29. If the 700-image Model Still Produces No Detections

Do NOT immediately retrain.

Investigate in this order:

### A. Input preprocessing

Compare:

```text
YOLO preprocessing
vs.
IMX500 RPK input normalization
```

Specifically inspect:

```text
inputTensorFormat
inputTensorNorm_K00
inputTensorNorm_K02
inputTensorNorm_K03
inputTensorNorm_K11
inputTensorNorm_K13
inputTensorNorm_K20
inputTensorNorm_K22
inputTensorNorm_K23
inputTensorNorm_YGain
inputTensorNorm_YAdd
```

Do not assume the official MobileNet SSD values are correct.

---

### B. NMS semantics

Verify:

```text
boxes
scores
class IDs
num detections
```

match what the Raspberry Pi `imx500_object_detection` postprocessor expects.

The generated graph already contains:

```text
MultiClassNMSWithIndices
```

so this should be investigated semantically, not simply assumed to be missing.

---

### C. Quantization/calibration

Compare:

```text
10-image conversion
vs.
700-image conversion
```

If the 700-image model behaves differently, calibration quality is a strong candidate.

---

### D. Output tensor interpretation

Confirm that:

```text
ordinal 3 → num_detections
ordinal 2 → class IDs
ordinal 1 → scores
ordinal 0 → boxes
```

is actually interpreted correctly by the Raspberry Pi postprocessor.

The logical dimensions previously observed were:

```text
ordinal 3 → 1
ordinal 2 → 300
ordinal 1 → 300
ordinal 0 → 300 x 4
```

---

# 30. Do Not Repeat These Failed Approaches

Avoid:

1. Direct `format="imx"` export on Windows.
2. Using the Raspberry Pi Python 3.13 environment as the main converter.
3. Installing random newer OR-Tools versions to satisfy `conv-allocator`.
4. Allowing Ultralytics to downgrade `edge-mdt-cl` to 1.0.0.
5. Assuming the official MobileNet SSD input normalization is correct for this YOLO model.
6. Treating the 10-image conversion as the final model.
7. Using standard ONNX Runtime as the validator for the final quantized IMX model.
8. Retraining the YOLO model before the conversion pipeline has been properly validated.
9. Reinstalling or modifying the Pi's IMX500 camera software unnecessarily.

---

# 31. Success Criteria

The project is successful when:

1. The original `weights.pt` is verified on Linux.
2. The 700-image calibration set is accepted by the IMX conversion pipeline.
3. IMX conversion completes.
4. `imxconv-pt` produces `packerOut.zip`.
5. `imx500-package` produces a valid `network.rpk`.
6. The RPK fits in the IMX500 memory.
7. The camera loads the RPK.
8. The Raspberry Pi postprocessor recognizes the four outputs.
9. ROI detections appear on the camera.
10. Images with ROI produce detections.
11. Images without ROI do not generate excessive false detections.
12. Detection behavior is reasonably consistent with the original YOLO model.

---

# 32. Current Status

### Confirmed working

- [x] YOLO12 model
- [x] Windows inference
- [x] 700-image dataset prepared
- [x] IMX500 Pi hardware
- [x] Official IMX500 camera pipeline
- [x] IMX500 packaging tools
- [x] IMX500 RPK packaging
- [x] IMX500 memory fit
- [x] Small 10-image IMX conversion
- [x] `imxconv-pt`
- [x] Four-output/NMS graph generation
- [x] Linux IMX converter import
- [x] Pi PyTorch 2.6.0

### Known blockers / unresolved

- [ ] Final 700-image Linux conversion
- [ ] Validate final quantized model
- [ ] Determine why previous 10-image RPK produced no detections
- [ ] Verify IMX500 input normalization
- [ ] Verify IMX500 output semantics
- [ ] Validate final RPK on camera

### Current strategy

**Use a separate Linux PC for the conversion.**

Keep the Raspberry Pi primarily as the deployment/test target.

---

# 33. First Action for the New Coding Agent

Do not start installing packages immediately.

First collect:

```bash
cat /etc/os-release
python3 --version
uname -m
java -version
ls /usr/bin/python3*
```

Then determine the best Python environment for the exact IMX500 conversion versions above.

Only after that should package installation begin.