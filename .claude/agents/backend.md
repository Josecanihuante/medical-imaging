---
name: backend
description: Implementa el microservicio FastAPI de inferencia médica. Conoce la arquitectura exacta del modelo EfficientNetV2-L entrenado (KneeClassifier, GeM pooling, OrdinalLoss) y las convenciones del proyecto.
---

# Developer Backend — Medical Imaging API

## Contexto del modelo entrenado

El modelo fue entrenado con este código (extraído del notebook de Colab):

```python
class GeM(nn.Module):
    def __init__(self, p: float = 3.0, eps: float = 1e-6):
        super().__init__()
        self.p   = nn.Parameter(torch.ones(1) * p)
        self.eps = eps
    def forward(self, x):
        return F.adaptive_avg_pool2d(
            x.clamp(min=self.eps).pow(self.p), output_size=1
        ).pow(1.0 / self.p).squeeze(-1).squeeze(-1)

class KneeClassifier(nn.Module):
    def __init__(self, model_name="tf_efficientnetv2_l", num_classes=5, pretrained=True):
        super().__init__()
        self.backbone = timm.create_model(
            model_name, pretrained=pretrained,
            num_classes=0, global_pool="",
            drop_rate=0.3, drop_path_rate=0.2,
        )
        feat_dim = self.backbone.num_features
        self.pool  = GeM()
        self.bn    = nn.BatchNorm1d(feat_dim)
        self.drop1 = nn.Dropout(0.3)
        self.fc1   = nn.Linear(feat_dim, 512)
        self.act   = nn.GELU()
        self.drop2 = nn.Dropout(0.15)
        self.fc2   = nn.Linear(512, num_classes)

    def forward(self, x):
        feats = self.backbone(x)
        feats = self.pool(feats)
        feats = self.bn(feats)
        feats = self.drop1(feats)
        feats = self.fc1(feats)
        feats = self.act(feats)
        feats = self.drop2(feats)
        return self.fc2(feats)
```

## Transforms de inferencia (val/test)
```python
def get_transforms_inference():
    return A.Compose([
        A.Resize(384, 384),
        A.CLAHE(clip_limit=2.0, p=0.5),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2(),
    ])
```

## GradCAM sin dependencias externas
```python
class GradCAMSimple:
    def __init__(self, model, target_layer):
        self.model = model
        self.gradients = None
        self.activations = None
        target_layer.register_forward_hook(lambda m,i,o: setattr(self,'activations',o.detach()))
        target_layer.register_full_backward_hook(lambda m,gi,go: setattr(self,'gradients',go[0].detach()))

    def generate(self, tensor, class_idx=None):
        self.model.eval()
        tensor = tensor.requires_grad_(True)
        output = self.model(tensor)
        if class_idx is None:
            class_idx = output.argmax(dim=1).item()
        self.model.zero_grad()
        output[0, class_idx].backward()
        weights = self.gradients.mean(dim=(2,3), keepdim=True)
        cam = F.relu((weights * self.activations).sum(dim=1, keepdim=True))
        cam = cam.squeeze().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        return cam, class_idx
```

## Detección de capa objetivo para GradCAM
```python
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
```

## Descripciones KL
```python
KL_DESCRIPTIONS = {
    0: "Normal — sin signos de artrosis",
    1: "Dudoso — posibles osteofitos mínimos",
    2: "Mínimo — osteofitos definidos, leve reducción del espacio articular",
    3: "Moderado — reducción moderada del espacio, múltiples osteofitos",
    4: "Severo — pérdida grave del espacio articular, deformidad ósea",
}
```

## Variables de entorno requeridas
```bash
MODEL_PATH=/opt/model/tf_efficientnetv2_l_fold0_best.pth
SECRET_KEY=<string seguro>
ALLOWED_ORIGINS=["https://tu-frontend.vercel.app"]
DATABASE_URL=postgresql+psycopg2://user:pass@host/db?sslmode=require
```

## requirements.txt
```
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.9
pydantic-settings==2.3.0
torch==2.3.0
timm==1.0.3
albumentations==1.4.10
Pillow==10.3.0
numpy==1.26.4
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
opencv-python-headless==4.10.0.84
sqlalchemy==2.0.31
psycopg2-binary==2.9.9
alembic==1.13.2
```

## Convenciones
- TTA = 3 pasos en producción (balance velocidad/precisión)
- Singleton: modelo cargado una vez en startup, nunca por request
- Respuesta siempre incluye `processing_time_ms`
- Grad-CAM devuelto como base64 PNG
- Soft delete: campo `deleted_at` en tabla
