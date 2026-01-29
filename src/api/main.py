from pathlib import Path
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form

from utils import save_upload, run_detection
from models import Detection, DetectResponse

UPLOAD_DIR = Path("d:/Projects/Yolo/uploads")
MODEL_WEIGHTS = "yolov8n.pt"

app = FastAPI(title="Image Detector API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/detect", response_model=DetectResponse)
async def detect(file: UploadFile = File(...), conf: float = Form(0.25)):
    if file.content_type.split("/")[0] != "image":
        return JSONResponse(status_code=400, content={"Error": "Only image uploads allowed"})
    dest = UPLOAD_DIR / file.filename
    await save_upload(file, dest)
    detections = await run_detection(dest, MODEL_WEIGHTS, conf)
    return {"detections": detections}