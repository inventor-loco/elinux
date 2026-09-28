#!/bin/bash
set -e

echo "========================================="
echo "   Raspberry Pi IMX500 Setup & Test      "
echo "========================================="

# 1. Check if we are in the repository root
if [ ! -f "weights_imx_model/packerOut.zip" ]; then
    echo "Error: weights_imx_model/packerOut.zip not found!"
    echo "Please run this script from the root of the elinux repository."
    exit 1
fi

# 2. Package the RPK (Task 13)
echo "[1/3] Packaging the RPK using imx500-package..."
imx500-package -i weights_imx_model/packerOut.zip -o weights_imx_model

# Check if network.rpk was produced
if [ ! -f "weights_imx_model/network.rpk" ]; then
    echo "Error: network.rpk was not generated!"
    exit 1
fi
echo "network.rpk successfully generated at weights_imx_model/network.rpk"

# 3. Create the test configuration JSON (Task 14)
echo "[2/3] Generating test_config.json..."
NETWORK_RPK_PATH="$(pwd)/weights_imx_model/network.rpk"

cat <<EOF > test_config.json
{
    "version": 2.0,
    "pipeline": [
        {
            "type": "imx500_object_detection",
            "max_detections": 300,
            "threshold": 0.0,
            "network_file": "${NETWORK_RPK_PATH}",
            "classes": ["ROI"]
        },
        {
            "type": "object_detect_draw_cv",
            "line_thickness": 6
        }
    ]
}
EOF
echo "Created test_config.json pointing to ${NETWORK_RPK_PATH}"

# 4. Run the camera test (Task 14)
echo "[3/3] Running camera test with rpicam-hello..."
echo "Press Ctrl+C to stop the test."
echo ""

rpicam-hello -t 0 --post-process-file test_config.json --shutter 50 -v 2 --viewfinder-width 1920 --viewfinder-height 1080
