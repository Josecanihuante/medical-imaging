import torch
import numpy as np
from PIL import Image
import io
import time
import logging
from typing import Dict, Optional
from backend.app.models.knee_classifier import KneeClassifier, get_transforms_inference, KL_DESCRIPTIONS
import torch.nn.functional as F

logger = logging.getLogger(__name__)

# Singleton model
_model: Optional[KneeClassifier] = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model(checkpoint_path: str) -> KneeClassifier:
    """Load the EfficientNetV2-L model from checkpoint."""
    global _model
    if _model is None:
        try:
            _model = KneeClassifier(
                model_name="tf_efficientnetv2_l",
                num_classes=5,
                pretrained=False  # We load our own weights
            )
            state_dict = torch.load(checkpoint_path, map_location=_device)
            _model.load_state_dict(state_dict)
            _model.to(_device)
            _model.eval()
        except Exception as e:
            logger.error(f"Failed to load model from {checkpoint_path}: {str(e)}")
            raise RuntimeError(f"Failed to load model: {str(e)}")
    return _model


def predict(image_bytes: bytes, tta_steps: int = 3) -> Dict:
    """Run inference on image bytes with test-time augmentation.
    
    Args:
        image_bytes: Raw image bytes
        tta_steps: Number of test-time augmentation steps (default: 3)
    
    Returns:
        Dict with keys: kl_grade, confidence, probabilities, processing_time_ms
    """
    start_time = time.time()
    
    # Load model if not already loaded
    if _model is None:
        # This should not happen in production if startup event works
        raise RuntimeError("Model not loaded. Call load_model first.")
    
    # Transformations
    transform = get_transforms_inference()
    
    # Open image
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # Prepare TTA
    if tta_steps <= 1:
        # No TTA, just regular transform
        augmented_images = [transform(image)]
    else:
        # Apply TTA: we'll use different random augmentations
        # For simplicity, we'll use the same transform but could add randomness
        augmented_images = [transform(image) for _ in range(tta_steps)]
    
    # Stack into batch
    batch = torch.stack(augmented_images).to(_device)
    
    # Inference
    with torch.no_grad():
        outputs = _model(batch)
        # Average predictions across TTA steps
        probs = F.softmax(outputs, dim=1)
        avg_probs = probs.mean(dim=0)
        
        # Get prediction
        confidence, predicted = torch.max(avg_probs, dim=0)
        kl_grade = predicted.item()
        confidence = confidence.item()
        
        # Build probabilities dict
        probabilities = {
            f"kl_{i}": avg_probs[i].item() 
            for i in range(len(avg_probs))
        }
    
    processing_time_ms = int((time.time() - start_time) * 1000)
    
    return {
        "kl_grade": kl_grade,
        "confidence": confidence,
        "probabilities": probabilities,
        "processing_time_ms": processing_time_ms
    }