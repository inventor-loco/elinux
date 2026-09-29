#!/usr/bin/env bash
# Native rpicam demo: IMX500 ROI detection with bounding boxes on preview
# and one brief stdout line per detected ROI.
# Must be run from the repo root.
set -e
cd "$(dirname "$0")"

NETWORK_RPK_PATH="$(pwd)/weights_imx_model/network.rpk"
if [ ! -f "${NETWORK_RPK_PATH}" ]; then
    echo "Missing ${NETWORK_RPK_PATH}. Package it first:"
    echo "  imx500-package -i weights_imx_model/packerOut.zip -o weights_imx_model"
    exit 1
fi

# Generate config with the absolute RPK path (relative paths silently fail on some builds).
CONFIG=output/test_config.runtime.json
mkdir -p output
cat > "${CONFIG}" <<EOF
{
    "imx500_object_detection": {
        "max_detections": 300,
        "threshold": 0.3,
        "network_file": "${NETWORK_RPK_PATH}",
        "classes": ["ROI"],
        "bbox_normalization": true,
        "bbox_order": "xy"
    },
    "object_detect_draw_cv": {
        "line_thickness": 6
    }
}
EOF

rpicam-hello \
    -t 0 \
    --post-process-file "${CONFIG}" \
    --shutter 50 \
    --viewfinder-width 1920 --viewfinder-height 1080 \
    --metadata - \
    --metadata-format json \
  | python3 -c '
import sys, json
seen_keys = set()
DET_KEYS = ("ObjectDetect", "Imx500ObjectDetect", "Detections", "objects")
for line in sys.stdin:
    line = line.strip()
    if not line.startswith("{"):
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    # Log any new top-level keys we have not seen (helps identify the detection key).
    new = [k for k in d.keys() if k not in seen_keys]
    for k in new:
        seen_keys.add(k)
        print(f"[meta-key] {k}", flush=True)
    for key in DET_KEYS:
        dets = d.get(key)
        if not dets:
            continue
        for det in dets:
            if isinstance(det, dict):
                box = det.get("box") or det.get("bbox") or [0,0,0,0]
                conf = det.get("confidence", det.get("score", 0.0))
                print(f"detected[{key}]  conf={conf:.2f}  box={box}", flush=True)
            else:
                print(f"detected[{key}]  raw={det}", flush=True)
'
