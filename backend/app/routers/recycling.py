from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/")
async def classify(file: UploadFile = File(...)):
    # Stub implementation
    return {"label": "plastic"}