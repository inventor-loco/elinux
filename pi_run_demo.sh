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
        "threshold": 0.0,
        "network_file": "${NETWORK_RPK_PATH}",
        "classes": ["ROI"]
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
