#!/usr/bin/env bash
# Run the packaged LED-strip detector with Raspberry Pi's native camera preview.
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
NETWORK_RPK="${SCRIPT_DIR}/weights_imx_model/network.rpk"
OUTPUT_DIR="${SCRIPT_DIR}/output"
CONFIG="${OUTPUT_DIR}/test_config.runtime.json"

if [[ ! -s "${NETWORK_RPK}" ]]; then
    echo "Missing ${NETWORK_RPK}. Package the latest packerOut.zip first:" >&2
    echo "  imx500-package -i '${SCRIPT_DIR}/weights_imx_model/packerOut.zip' -o '${SCRIPT_DIR}/weights_imx_model'" >&2
    exit 1
fi

if ! command -v rpicam-hello >/dev/null 2>&1; then
    echo "Error: rpicam-hello is not installed or not on PATH." >&2
    exit 1
fi

mkdir -p "${OUTPUT_DIR}"
cat > "${CONFIG}" <<EOF
{
    "imx500_object_detection": {
        "max_detections": 5,
        "threshold": 0.3,
        "network_file": "${NETWORK_RPK}",
        "temporal_filter": {
            "tolerance": 0.1,
            "factor": 0.2,
            "visible_frames": 4,
            "hidden_frames": 2
        },
        "classes": ["ROI"]
    },
    "object_detect_draw_cv": {
        "line_thickness": 2
    }
}
EOF

echo "Using model: ${NETWORK_RPK}"
echo "Using post-processing config: ${CONFIG}"
echo "Look for ROI boxes in the preview and detection/box-coordinate messages below. Press Ctrl+C to stop."

# 50 us exposure is required by the rolling-shutter LED communication setup.
exec rpicam-hello \
    -t 0 \
    --post-process-file "${CONFIG}" \
    --shutter 50 \
    --viewfinder-width 1920 \
    --viewfinder-height 1080 \
    --framerate 15 \
    -v 2
