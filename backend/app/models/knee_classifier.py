import torch
import torch.nn as nn
import torch.nn.functional as F
import timm
import albumentations as A
from albumentations.pytorch import ToTensorV2


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


def get_transforms_inference():
    return A.Compose([
        A.Resize(384, 384),
        A.CLAHE(clip_limit=2.0, p=0.5),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2(),
    ])


KL_DESCRIPTIONS = {
    0: "Normal — sin signos de artrosis",
    1: "Dudoso — posibles osteofitos mínimos",
    2: "Mínimo — osteofitos definidos, leve reducción del espacio articular",
    3: "Moderado — reducción moderada del espacio, múltiples osteofitos",
    4: "Severo — pérdida grave del espacio articular, deformidad ósea",
}