from pydantic import BaseModel
from typing import List, Tuple

class Detection(BaseModel):
    class_id: int
    label: str
    confidence: float
    box: Tuple[float, float, float, float]

class DetectResponse(BaseModel):
    detections: List[Detection]