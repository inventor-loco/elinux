import os
os.environ["ULTRALYTICS_SKIP_REQUIREMENTS_CHECKS"] = "1"

from ultralytics import YOLO

def verify_original_model():
    print("Loading original weights.pt...")
    model = YOLO("/home/inventor-loco/Desktop/REPOS/elinux/weights.pt")
    
    # Test on one image
    test_image = "/home/inventor-loco/Desktop/REPOS/elinux/dataset/frame_114.jpg"
    print(f"Running inference on {test_image}...")
    results = model(test_image)
    
    for r in results:
        print("Detections:")
        print(r.boxes.data)

def export_imx():
    print("Loading original weights.pt for IMX export...")
    model = YOLO("/home/inventor-loco/Desktop/REPOS/elinux/weights.pt")
    
    print("Starting IMX export...")
    model.export(
        format="imx",
        imgsz=640,
        data="/home/inventor-loco/Desktop/REPOS/elinux/imx_linux.yaml",
        fraction=0.5
    )
    print("Export finished.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        export_imx()
    else:
        verify_original_model()
