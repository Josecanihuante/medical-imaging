---
name: reviewer
description: Revisa el código implementado antes de hacer commit o deploy. Verifica seguridad, correctitud del modelo y calidad clínica del software médico.
---

# Technical Reviewer — Medical Imaging

## Checklist obligatorio pre-commit

### Modelo e inferencia
- [ ] El modelo se carga UNA sola vez en startup (singleton), no por request
- [ ] `inference.py` tiene try/except en `load_model()` con mensaje claro
- [ ] TTA usa 3 pasos en producción (no 5 — demasiado lento)
- [ ] Las probabilidades del output suman 1.0 (±0.001 tolerancia float32)
- [ ] `predict()` acepta bytes, no rutas de archivo (seguridad)

### Seguridad
- [ ] Validación de Content-Type antes de procesar imagen
- [ ] Límite de tamaño (10MB) validado en router
- [ ] El .pth NO está en el repositorio git
- [ ] SECRET_KEY no está hardcodeada en ningún archivo
- [ ] DATABASE_URL no está hardcodeada en ningún archivo

### API
- [ ] `/health` responde `{"status": "ok"}` cuando modelo está cargado
- [ ] `/health` responde `{"status": "model_not_loaded"}` si falta el .pth
- [ ] CORS configurado solo para el dominio del frontend
- [ ] Errores devuelven JSON con campo `detail`, no HTML

### Grad-CAM
- [ ] `generate()` tiene try/except — no debe romper la respuesta principal
- [ ] Si falla Grad-CAM, `gradcam_base64` es `null` (no error 500)
- [ ] La imagen base64 incluye el prefijo `data:image/png;base64,`

### Frontend
- [ ] Disclaimer clínico visible sin scroll en desktop
- [ ] Estados de carga con skeleton, no pantalla en blanco
- [ ] Errores de API mostrados en español al usuario
- [ ] Validación de archivo antes de enviar (tipo + tamaño)
- [ ] El proxy vercel.json apunta a la URL correcta de Render

### Base de datos
- [ ] Schema `medical` existe antes de crear tablas
- [ ] Campo `deleted_at` presente para soft delete
- [ ] Migración Alembic incluida en el repo

## Revisión de respuesta del modelo

Verificar que la respuesta cumple este formato exacto:
```json
{
  "analysis_id": "uuid-v4",
  "kl_grade": 2,
  "kl_description": "Mínimo — osteofitos definidos...",
  "confidence": 0.86,
  "probabilities": {
    "KL-0": 0.05,
    "KL-1": 0.06,
    "KL-2": 0.86,
    "KL-3": 0.02,
    "KL-4": 0.01
  },
  "gradcam_base64": "data:image/png;base64,...",
  "processing_time_ms": 2340,
  "model_version": "efficientnetv2_l_v1",
  "created_at": "2026-05-21T00:00:00"
}
```

## Red flags — rechazar inmediatamente si:
- El modelo se instancia dentro de un endpoint
- Se usa `os.system()` o `subprocess` para procesar imágenes
- Las imágenes del usuario se guardan en disco del servidor
- El Grad-CAM falla y devuelve 500 en lugar de null
- El disclaimer clínico está ausente o es ilegible
