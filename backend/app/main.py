from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.routers import analysis
import os
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Medical Imaging API",
    description="Análisis de artrosis de rodilla mediante IA",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router)

@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    from backend.app.services.inference import load_model
    
    # Check if model file exists
    if not os.path.exists(settings.MODEL_PATH):
        error_msg = f"Model file not found at {settings.MODEL_PATH}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    # Load the model
    try:
        load_model(settings.MODEL_PATH)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise RuntimeError(f"Failed to load model: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Medical Imaging API - Análisis de Artrosis de Rodilla"}