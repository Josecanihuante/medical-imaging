import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from PIL import Image
import io
import base64
from typing import Optional, Tuple
from backend.app.models.knee_classifier import KneeClassifier


class GradCAMSimple:
    def __init__(self, model, target_layer):
        self.model = model
        self.gradients = None
        self.activations = None
        target_layer.register_forward_hook(lambda m, i, o: setattr(self, 'activations', o.detach()))
        target_layer.register_full_backward_hook(lambda m, gi, go: setattr(self, 'gradients', go[0].detach()))

    def generate(self, tensor, class_idx=None):
        self.model.eval()
        tensor = tensor.requires_grad_(True)
        output = self.model(tensor)
        if class_idx is None:
            class_idx = output.argmax(dim=1).item()
        self.model.zero_grad()
        output[0, class_idx].backward()
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = F.relu((weights * self.activations).sum(dim=1, keepdim=True))
        cam = cam.squeeze().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        return cam, class_idx


def get_target_layer(model):
    try:
        if hasattr(model.backbone, "features"):
            return model.backbone.features[-1]   # DenseNet
        elif hasattr(model.backbone, "blocks"):
            return model.backbone.blocks[-1]      # EfficientNetV2
        else:
            convs = [m for m in model.backbone.modules() if isinstance(m, nn.Conv2d)]
            return convs[-1]
    except Exception:
        return None


def generate_base64(model, image_bytes) -> Optional[str]:
    """Generate Grad-CAM heatmap and return as base64 encoded PNG.
    
    Returns None if any step fails (never raises exception).
    """
    try:
        # Transformations (same as inference)
        from backend.app.models.knee_classifier import get_transforms_inference
        transform = get_transforms_inference()
        
        # Open and transform image
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        input_tensor = transform(image).unsqueeze(0)  # Add batch dimension
        
        # Get target layer
        target_layer = get_target_layer(model)
        if target_layer is None:
            return None
            
        # Create GradCAM object
        gradcam = GradCAMSimple(model, target_layer)
        
        # Generate CAM
        cam, class_idx = gradcam.generate(input_tensor)
        
        # Resize CAM to match original image size
        from skimage.transform import resize
        cam_resized = resize(cam, image.size[::-1], mode='reflect', anti_aliasing=True)
        
        # Apply colormap (jet)
        import matplotlib.cm as cm
        jet = cm.get_cmap("jet")
        cam_colored = jet(cam_resized)
        
        # Blend with original image
        from PIL import Image as PilImage
        original = PilImage.open(io.BytesIO(image_bytes)).convert("RGBA")
        cam_image = PilImage.fromarray((cam_colored * 255).astype(np.uint8), mode="RGBA")
        
        # Resize CAM to match original if needed
        if cam_image.size != original.size:
            cam_image = cam_image.resize(original.size, PilImage.Resampling.LANCZOS)
        
        # Blend images (alpha = 0.4 for heatmap)
        blended = PilImage.blend(original, cam_image, alpha=0.4)
        
        # Convert to base64
        buffered = io.BytesIO()
        blended.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return img_base64
        
    except Exception:
        # Return None on any error (never raise exception)
        return None