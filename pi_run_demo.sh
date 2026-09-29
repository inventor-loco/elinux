#!/usr/bin/env bash
# Native rpicam demo: IMX500 ROI detection with bounding boxes drawn on preview.
# Must be run from the repo root so the relative network_file path in test_config.json resolves.
set -e
cd "$(dirname "$0")"

rpicam-hello \
    -t 0 \
    --post-process-file test_config.json \
    --shutter 50 \
    --width 1920 --height 1080 \
    --framerate 15 \
    --metadata - \
    --metadata-format json \
  | python3 -c '
import sys, json
for line in sys.stdin:
    line = line.strip()
    if not line.startswith("{"):
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    dets = d.get("ObjectDetect") or []
    for det in dets:
        box = det.get("box", [0,0,0,0])
        conf = det.get("confidence", 0.0)
        print(f"detected  conf={conf:.2f}  box=[{box[0]:.3f}, {box[1]:.3f}, {box[2]:.3f}, {box[3]:.3f}]", flush=True)
'
