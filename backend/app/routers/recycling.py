from fastapi import APIRouter, UploadFile, File
from app.services.classification import classify_image

router = APIRouter()

@router.post("/")
async def classify(file: UploadFile = File(...)):
    label = await classify_image(file)
    if label == "battery":
        return {"label": label, "redirect": "/battery-service"}
    return {"label": label}
