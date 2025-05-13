from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import auth, recycling, points, detect

app = FastAPI()

# CORS to allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router, prefix="/auth")
app.include_router(recycling.router, prefix="/recycle")
app.include_router(points.router, prefix="/points")
app.include_router(detect.router, prefix="/detect")

# Add a root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to RecycleMe Backend"}