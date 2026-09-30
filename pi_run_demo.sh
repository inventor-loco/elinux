#!/usr/bin/env bash
# Run the packaged YOLO model through the Picamera2 decoder and live overlay.
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
NETWORK_RPK="${SCRIPT_DIR}/weights_imx_model/network.rpk"
TEST_SCRIPT="${SCRIPT_DIR}/pi_test_python.py"

if [[ ! -s "${NETWORK_RPK}" ]]; then
    echo "Missing ${NETWORK_RPK}. Package the latest packerOut.zip first:" >&2
    echo "  imx500-package -i '${SCRIPT_DIR}/weights_imx_model/packerOut.zip' -o '${SCRIPT_DIR}/weights_imx_model'" >&2
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is not installed or not on PATH." >&2
    exit 1
fi

exec python3 "${TEST_SCRIPT}"
