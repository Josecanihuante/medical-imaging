from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime


class AnalysisResponse(BaseModel):
    id: str
    patient_id: Optional[str] = None
    kl_grade: int = Field(..., ge=0, le=4)
    confidence: float = Field(..., ge=0, le=1)
    probabilities: Dict[str, float]
    processing_time_ms: int
    gradcam_base64: Optional[str] = None
    created_at: datetime
    notes: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "patient_id": "PACIENTE123",
                    "kl_grade": 2,
                    "confidence": 0.87,
                    "probabilities": {
                        "kl_0": 0.05,
                        "kl_1": 0.08,
                        "kl_2": 0.87,
                        "kl_3": 0.0,
                        "kl_4": 0.0
                    },
                    "processing_time_ms": 1250,
                    "gradcam_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
                    "created_at": "2024-05-21T10:00:00Z",
                    "notes": "Paciente de 65 años con dolor progresivo"
                }
            ]
        }
    }