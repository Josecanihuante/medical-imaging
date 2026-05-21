---
name: arquitecto
description: Diseña la arquitectura del módulo de análisis de imágenes médicas. Úsalo antes de implementar cualquier módulo nuevo, para validar estructura de carpetas, contratos de API y decisiones técnicas.
---

# Arquitecto de Software — Medical Imaging API

## Stack
- **Backend**: FastAPI + Python 3.12 — Render.com (Starter 2GB RAM)
- **Modelo IA**: EfficientNetV2-L · κ=0.9758 · AUC=0.9828
- **Base de datos**: PostgreSQL 16 en Neon — schema: `medical`
- **Frontend**: React 18 + TypeScript + Tailwind — Vercel
- **Auth**: JWT (python-jose) + bcrypt (passlib)
- **Repo**: medical-imaging (GitHub)

## Patrón obligatorio
router → service → schema → model

## Estructura de directorios
```
backend/
  app/
    core/       → config.py, security.py
    models/     → knee_classifier.py (arquitectura CNN del notebook)
    schemas/    → analysis.py (Pydantic v2)
    routers/    → analysis.py
    services/   → inference.py, gradcam.py
  main.py
  requirements.txt
  Dockerfile
frontend/
  src/
    pages/KneeAnalysis/ → index.tsx, UploadZone.tsx, ResultCard.tsx, GradCAMView.tsx
    services/           → medicalAnalysis.ts
    components/         → KLGradeBar.tsx
```

## Schema PostgreSQL
```sql
CREATE SCHEMA IF NOT EXISTS medical;
CREATE TABLE medical.knee_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(100),
    kl_grade SMALLINT NOT NULL CHECK (kl_grade BETWEEN 0 AND 4),
    confidence NUMERIC(5,4) NOT NULL,
    probabilities JSONB NOT NULL,
    model_version VARCHAR(50) DEFAULT 'efficientnetv2_l_v1',
    processing_time_ms INTEGER,
    gradcam_stored BOOLEAN DEFAULT false,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);
```

## Principios
- El modelo se carga UNA sola vez al iniciar (singleton en inference.py)
- El .pth NUNCA va en git — se monta via Render Disk en /opt/model/
- CORS configurado para el dominio del frontend
- Validación de tipo MIME y tamaño en el router antes de inferencia
- Disclaimer clínico obligatorio en la UI
- Respuestas envueltas en estructura consistente con el ERP: `{success: true, data: {...}}`

## Checklist pre-implementación
1. ¿La lógica de inferencia está en service, no en router?
2. ¿El schema PostgreSQL es `medical`?
3. ¿El endpoint /health responde antes de aceptar requests?
4. ¿Las variables de entorno están documentadas en README?
5. ¿El Grad-CAM tiene try/except para no fallar si la capa no se detecta?
