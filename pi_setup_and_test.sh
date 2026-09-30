#!/usr/bin/env bash
# Package the latest IMX500 packer output and start the native camera demo.
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

PACKER_ZIP="${SCRIPT_DIR}/weights_imx_model/packerOut.zip"
NETWORK_RPK="${SCRIPT_DIR}/weights_imx_model/network.rpk"

if [[ ! -f "${PACKER_ZIP}" ]]; then
    echo "Error: missing ${PACKER_ZIP}" >&2
    echo "Copy the final packerOut.zip into weights_imx_model/ first." >&2
    exit 1
fi

if ! command -v imx500-package >/dev/null 2>&1; then
    echo "Error: imx500-package is not installed or not on PATH." >&2
    echo "Install it on Raspberry Pi OS with: sudo apt install imx500-tools" >&2
    exit 1
fi

if ! command -v rpicam-hello >/dev/null 2>&1; then
    echo "Error: rpicam-hello is not installed or not on PATH." >&2
    echo "Install/update the Raspberry Pi camera software before continuing." >&2
    exit 1
fi

echo "Packaging ${PACKER_ZIP} for the IMX500 camera..."
imx500-package -i "${PACKER_ZIP}" -o "${SCRIPT_DIR}/weights_imx_model"

if [[ ! -s "${NETWORK_RPK}" ]]; then
    echo "Error: packaging did not produce ${NETWORK_RPK}" >&2
    exit 1
fi

echo "Created ${NETWORK_RPK}"
echo "Starting the camera preview. Press Ctrl+C to stop."
exec "${SCRIPT_DIR}/pi_run_demo.sh"
