import asyncio
import aiofiles
from pathlib import Path
from ultralytics import YOLO
from typing import List, Dict
from fastapi import UploadFile

_MODEL = None

async def save_upload(upload: UploadFile, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(dest, "wb") as f:
        while chunk := await upload.read(1024*64):
            await f.write(chunk)
    await upload.close()
    return dest

async def _load_model(weights: str):
    global _MODEL
    if _MODEL is None:
        # instantiate model in a thread to avoid blocking event loop
        _MODEL = await asyncio.to_thread(YOLO, weights)
    return _MODEL

async def run_detection(image_path: Path, weights: str, conf: float = 0.25) -> List[Dict]:
    """
    Runs YOLO inference on image_path and returns list of dicts:
    { "class_id": int, "label": str, "confidence": float, "box": (x1,y1,x2,y2) }
    Returns empty list on error or if model unavailable.
    """
    model = await _load_model(weights)
    if model is None:
        return []

    # run inference in thread
    try:
        results = await asyncio.to_thread(model, image_path.as_posix(), conf=conf, verbose=False)
    except Exception:
        return []

    if not results:
        return []

    res = results[0]
    boxes = getattr(res, "boxes", None)
    names = getattr(res, "names", {}) or {}
    
    detections = []
    if not boxes:
        return detections

    for box in boxes:
        try:
            xyxy = box.xyxy[0].tolist()
        except Exception:
            # fallback if structure differs
            try:
                xyxy = box.xyxy.tolist()[0]
            except Exception:
                continue
        try:
            cls = int(box.cls[0]) if getattr(box, "cls", None) is not None else -1
            confv = float(box.conf[0]) if getattr(box, "conf", None) is not None else 0.0
        except Exception:
            cls, confv = -1, 0.0

        label = names.get(cls, str(cls))
        detections.append({
            "class_id": cls,
            "label": label,
            "confidence": round(confv, 4),
            "box": (float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3]))
        })

    return detections