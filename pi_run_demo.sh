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
    --framerate 15
