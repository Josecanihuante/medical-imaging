# Medical Imaging — Análisis de Artrosis de Rodilla

Microservicio de análisis de radiografías de rodilla mediante IA.
Clasifica automáticamente el grado de artrosis según la escala Kellgren-Lawrence (KL 0–4).

## Métricas del modelo
- κ cuadrático ponderado: 0.9758 (validación) / 0.9651 (test)
- AUC-ROC macro: 0.9828
- Accuracy: 89% sobre 3.772 imágenes de test

## Stack técnico
- **Backend**: FastAPI + Python 3.12 + PyTorch + timm
- **Modelo**: EfficientNetV2-L con GeM Pooling (checkpoint: `tf_efficientnetv2_l_fold0_best.pth`)
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **DB**: PostgreSQL 16 en Neon (schema: `medical`)
- **Deploy**: Render.com (backend) + Vercel (frontend)

## Instalación

### Backend
1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno virtual: `venv\Scripts\activate` (Windows) o `source venv/bin/activate` (Linux/Mac)
4. Instalar dependencias: `pip install -r backend/requirements.txt`
5. Crear archivo `.env` basado en el ejemplo siguiente:
```
MODEL_PATH=/opt/model/tf_efficientnetv2_l_fold0_best.pth
SECRET_KEY=<string seguro de al menos 32 caracteres>
ALLOWED_ORIGINS=["https://tu-frontend.vercel.app"]
DATABASE_URL=postgresql+psycopg2://user:pass@host/db?sslmode=require
```

### Frontend
1. Navegar a `frontend/`
2. Instalar dependencias: `npm install`
3. Crear archivo `.env.local` con:
```
NEXT_PUBLIC_API_URL=https://medical-imaging-api.onrender.com
```

## Variables de entorno requeridas

### Backend (Render.com)
- `MODEL_PATH`: Ruta al checkpoint del modelo (ej: `/opt/model/tf_efficientnetv2_l_fold0_best.pth`)
- `SECRET_KEY`: String seguro para firmar JWT
- `ALLOWED_ORIGINS`: Lista de orígenes permitidos para CORS (ej: `["https://tu-frontend.vercel.app"]`)
- `DATABASE_URL`: URL de conexión a PostgreSQL en Neon

### Frontend (Vercel)
- `NEXT_PUBLIC_API_URL`: URL del backend desplegado

## Subir el modelo .pth a Render Disk

1. En Render.com, crear un nuevo Web Service conectado a este repositorio
2. En la configuración del service, añadir un Disco Persistente:
   - Name: `model-storage`
   - Mount Path: `/opt/model`
   - Size: 3 GB
3. Desplegar el servicio una primera vez (fallará porque no hay .pth)
4. Acceder al servicio vía SSH en el dashboard de Render
5. Subir el archivo `tf_efficientnetv2_l_fold0_best.pth` a `/opt/model/`
6. Reiniciar el servicio

## Comandos de prueba

### Health check
```bash
curl https://medical-imaging-api.onrender.com/api/v1/medical/health
```
Respuesta esperada:
```json
{"success":true,"data":{"status":"ok","model_loaded":true}}
```

### Analizar una radiografía
```bash
curl -X POST "https://medical-imaging-api.onrender.com/api/v1/medical/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@ruta/a/tu/radiografia.jpg" \
  -F "patientId=PACIENTE123" \
  -F "includeGradcam=true"
```
Respuesta esperada:
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "kl_grade": 2,
    "confidence": 0.87,
    "probabilities": {"kl_0": 0.05, "kl_1": 0.08, "kl_2": 0.87, "kl_3": 0.0, "kl_4": 0.0},
    "processing_time_ms": 1250,
    "gradcam_base64": "string_base64_png_o_null",
    "created_at": "2024-05-21T10:00:00Z"
  }
}
```

## Despliegue

### Backend en Render.com
1. Crear nuevo Web Service
2. Conectar repositorio GitHub
3. Configurar:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables: As defined above
   - Disco Persistente: Mount en `/opt/model`

### Frontend en Vercel
1. Importar proyecto desde GitHub
2. Configurar Variable de Entorno:
   - `NEXT_PUBLIC_API_URL`: URL del backend en Render
3. Desplegar

## Disclaimer clínico

> Este análisis es una herramienta de apoyo diagnóstico basada en IA.
> No reemplaza el criterio clínico de un médico especialista.