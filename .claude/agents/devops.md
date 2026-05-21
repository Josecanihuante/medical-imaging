---
name: devops
description: Configura el deployment del microservicio médico en Render.com y Vercel. Conoce los requisitos de RAM para PyTorch y la estrategia de montaje del modelo.
---

# DevOps — Medical Imaging Deployment

## Infraestructura

| Componente | Plataforma | Plan | Motivo |
|---|---|---|---|
| Backend API | Render.com | Starter (2GB RAM) | PyTorch requiere >1GB RAM |
| Modelo .pth | Render Disk | 3GB | Archivo de 1.4GB |
| Frontend | Vercel | Hobby/Pro | Proxy a Render |
| Base de datos | Neon PostgreSQL | Free | Schema `medical` |

## Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MODEL_PATH=/opt/model/tf_efficientnetv2_l_fold0_best.pth

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

## render.yaml
```yaml
services:
  - type: web
    name: medical-imaging-api
    runtime: docker
    dockerfilePath: ./backend/Dockerfile
    plan: starter
    healthCheckPath: /api/v1/medical/health
    envVars:
      - key: SECRET_KEY
        sync: false
      - key: ALLOWED_ORIGINS
        value: '["https://tu-frontend.vercel.app"]'
      - key: DATABASE_URL
        sync: false
    disk:
      name: model-weights
      mountPath: /opt/model
      sizeGB: 3
```

## .gitignore crítico
```
# Modelo — NUNCA en git
*.pth
*.pt
model/
/opt/model/

# Entorno
.env
.env.*
__pycache__/
*.pyc
```

## Pasos de deployment

### Primera vez:
1. `git push` al repo → Render detecta render.yaml automáticamente
2. En Render Dashboard → tu servicio → Disks → subir el .pth a /opt/model/
3. En Render Dashboard → Environment → agregar SECRET_KEY y DATABASE_URL
4. Verificar: `curl https://medical-imaging-api.onrender.com/api/v1/medical/health`

### Actualizaciones de modelo:
1. Subir nuevo .pth al Render Disk (mismo nombre)
2. Render redeploy automático (o manual desde dashboard)

## Variables de entorno requeridas en Render
```
MODEL_PATH=/opt/model/tf_efficientnetv2_l_fold0_best.pth
SECRET_KEY=<string aleatorio >32 chars>
ALLOWED_ORIGINS=["https://tu-frontend.vercel.app"]
DATABASE_URL=postgresql+psycopg2://user:pass@host/db?sslmode=require
```

## Startup del servidor (app/main.py)
```python
@app.on_event("startup")
async def startup_event():
    from app.services.inference import load_model
    import os
    model_path = os.getenv("MODEL_PATH")
    if not model_path or not os.path.exists(model_path):
        raise RuntimeError(f"Modelo no encontrado en {model_path}")
    load_model(model_path)
    print(f"✓ Modelo cargado desde {model_path}")
```

## Cold start
Render Starter tiene cold start de ~30s tras inactividad.
Para mitigarlo, configurar health check ping cada 14 minutos desde UptimeRobot (gratuito).
