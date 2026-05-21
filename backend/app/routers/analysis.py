from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import logging
from typing import Optional
from backend.app.services.inference import predict
from backend.app.services.gradcam import generate_base64
from backend.app.core.config import settings
from backend.app.schemas.analysis import AnalysisResponse
from uuid import uuid4
from datetime import datetime
import time

router = APIRouter()
logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/jpg"}

@router.post("/api/v1/medical/analyze")
async def analyze_knee_xray(
    file: UploadFile = File(...),
    patientId: Optional[str] = Form(None),
    includeGradcam: bool = Form(False)
):
    """
    Analyze a knee X-ray image to determine Kellgren-Lawrence grade.
    """
    start_time = time.time()
    
    # Validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)} MB"
        )
    
    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    try:
        # Run inference
        result = predict(contents, tta_steps=3)
        
        # Generate Grad-CAM if requested
        gradcam_base64 = None
        if includeGradcam:
            # Import here to avoid circular imports
            from backend.app.services.inference import _model
            if _model is not None:
                gradcam_base64 = generate_base64(_model, contents)
        
        # Create response
        response_data = AnalysisResponse(
            id=str(uuid4()),
            patient_id=patientId,
            kl_grade=result["kl_grade"],
            confidence=result["confidence"],
            probabilities=result["probabilities"],
            processing_time_ms=result["processing_time_ms"],
            gradcam_base64=gradcam_base64,
            created_at=datetime.utcnow(),
            notes=None
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        logger.info(f"Analysis completed in {processing_time}ms for patient {patientId}")
        
        return JSONResponse(
            content={"success": True, "data": response_data.model_dump()}
        )
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during image analysis"
        )

@router.get("/api/v1/medical/health")
async def health_check():
    """
    Health check endpoint to verify service is running and model is loaded.
    """
    from backend.app.services.inference import _model
    
    model_loaded = _model is not None
    
    return JSONResponse(
        content={
            "success": True,
            "data": {
                "status": "ok",
                "model_loaded": model_loaded
            }
        }
    )