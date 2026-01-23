import cv2
import argparse
from pathlib import Path
from ultralytics import YOLO

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--source", "-s", required=True, help="Image file or folder")
    p.add_argument("--weights", "-w", default="yolov8n.pt", help="YOLO weights file")
    p.add_argument("--conf", "-c", type=float, default=0.25, help="Confidence threshold")
    p.add_argument("--imgsz", type=int, default=640, help="Inference image size")
    p.add_argument("--save-dir", default="d:\\Projects\\Yolo\\outputs", help="Save annotated images")
    return p.parse_args()

def find_images(path: Path):
    if path.is_file():
        return [path]
    exts = ("*.jpg", "*.jpeg", "*.png", "*.bmp")
    imgs = []
    for e in exts:
        imgs.extend(path.rglob(e))
    return sorted(imgs)

# ...existing code...
def print_summary(result):
    boxes = getattr(result, "boxes", None)
    if not boxes or len(boxes) == 0:
        print(" No detections")
        return
    names = result.names if hasattr(result, "names") else {}
    for i, box in enumerate(boxes):
        xyxy = box.xyxy[0].tolist()
        cls = int(box.cls[0]) if box.cls is not None else -1
        conf = float(box.conf[0]) if box.conf is not None else 0.0
        label = names.get(cls, str(cls))
        print(f" [{i}] {label} conf={conf:.2f} box={tuple(round(v,1) for v in xyxy)}")

def annotate_and_save(result, save_path: Path):
    img_rgb = result.plot()  # returns RGB numpy array with annotations
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(save_path), img_bgr)

if __name__ == "__main__":
    args = parse_args()
    print("Args: ", args)
    src = Path(args.source)
    images = find_images(src)
    if not images:
        print("No images found")
    else:
        print("Found images: ", find_images(src)[:5])
        model = YOLO(args.weights)
        out_dir = Path(args.save_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for image in images:
            results = model(image.as_posix(), imgsz=args.imgsz, conf=args.conf, verbose=False)
            print_summary(results[0]) 
            annotate_and_save(results[0], out_dir / image.name)
            print("Saved:", out_dir / image.name)