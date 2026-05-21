# Prompts de Implementación — OpenCode
# Medical Imaging · Análisis de Artrosis de Rodilla
# Pegar cada fase en secuencia en OpenCode

---

## ═══════════════════════════════════════════
## FASE 1 — Arquitectura y base de datos
## ═══════════════════════════════════════════

```
Lee el archivo CLAUDE.md en la raíz del proyecto para entender el contexto completo.

Usando el agente @arquitecto:

1. Valida la estructura de carpetas definida en CLAUDE.md y créala completa
   en el proyecto si no existe.

2. Crea el archivo `backend/app/core/config.py` con Settings usando
   pydantic-settings, incluyendo estas variables:
   - MODEL_PATH: str
   - SECRET_KEY: str
   - ALLOWED_ORIGINS: list[str]
   - DATABASE_URL: str

3. Crea la migración Alembic para el schema `medical` con la tabla
   `knee_analyses` exactamente como está definida en el agente @arquitecto.

4. Crea el archivo `README.md` con:
   - Descripción del proyecto
   - Instrucciones de instalación
   - Variables de entorno requeridas
   - Instrucciones para subir el .pth a Render Disk
   - Comando de prueba con curl

Termina con un resumen de archivos creados.
```

---

## ═══════════════════════════════════════════
## FASE 2 — Microservicio FastAPI (backend)
## ═══════════════════════════════════════════

```
Usando el agente @backend, implementa el microservicio FastAPI completo
en la carpeta backend/ en este orden estricto:

1. `backend/app/models/knee_classifier.py`
   — Copiar EXACTAMENTE las clases GeM, KneeClassifier del agente @backend.
   — Agregar la función get_transforms_inference() con albumentations.
   — Agregar KL_DESCRIPTIONS dict.

2. `backend/app/schemas/analysis.py`
   — Clase AnalysisResponse con todos los campos definidos en el agente @backend.
   — Incluir validadores Pydantic v2.

3. `backend/app/services/inference.py`
   — Singleton del modelo (variable global _model).
   — Función load_model(checkpoint_path) que carga el .pth.
   — Función predict(image_bytes, tta_steps=3) que devuelve dict.

4. `backend/app/services/gradcam.py`
   — Clase GradCAMSimple del agente @backend.
   — Función generate_base64(model, image_bytes) → str | None.
   — Función get_target_layer(model) con try/except.
   — Si falla cualquier paso, retornar None (nunca lanzar excepción).

5. `backend/app/routers/analysis.py`
   — POST /api/v1/medical/analyze con validación de MIME y tamaño.
   — GET /api/v1/medical/health.

6. `backend/app/main.py`
   — Crear app FastAPI con CORS desde settings.
   — Evento startup que carga el modelo desde MODEL_PATH.
   — Incluir router de analysis.
   — Lanzar RuntimeError si el .pth no existe en startup.

7. `backend/requirements.txt`
   — Usar las versiones exactas del agente @backend.

Finaliza ejecutando @reviewer con su checklist completo sobre
todo el backend. Reporta cada punto como ✓ o ✗.
```

---

## ═══════════════════════════════════════════
## FASE 3 — Interfaz React (frontend)
## ═══════════════════════════════════════════

```
Usando el agente @frontend, implementa la interfaz React en la
carpeta frontend/ en este orden:

1. `frontend/src/services/medicalAnalysis.ts`
   — Interface AnalysisResult con todos los campos.
   — Función analyzeXray(file, patientId?, includeGradcam?).
   — Manejo de errores con mensajes en español.

2. `frontend/src/components/KLGradeBar.tsx`
   — Props: grade (0-4), value (0-1), label (string).
   — Colores del agente @frontend según grado KL.

3. `frontend/src/pages/KneeAnalysis/UploadZone.tsx`
   — Drag & drop + click.
   — Validación tipo (JPG/PNG) y tamaño (max 10MB) antes de emitir.
   — Preview de la imagen seleccionada.
   — Estados visuales: idle / dragover / uploading.

4. `frontend/src/pages/KneeAnalysis/ResultCard.tsx`
   — Badge con grado KL y color correspondiente.
   — Descripción clínica.
   — Barra de confianza.
   — Barras de probabilidad KL-0 a KL-4.

5. `frontend/src/pages/KneeAnalysis/GradCAMView.tsx`
   — Mostrar imagen base64.
   — Nota aclaratoria sobre interpretación del heatmap.

6. `frontend/src/pages/KneeAnalysis/index.tsx`
   — Layout 2 columnas desktop / 1 columna mobile.
   — Integra UploadZone + ResultCard + GradCAMView.
   — Skeleton loader durante análisis.
   — Disclaimer clínico OBLIGATORIO al pie (fondo amber).
   — Manejo de estado: idle / loading / result / error.

7. `frontend/vercel.json`
   — Proxy /medical/* → https://medical-imaging-api.onrender.com

Finaliza ejecutando @reviewer sobre el frontend.
Reporta cada punto del checklist como ✓ o ✗.
```

---

## ═══════════════════════════════════════════
## FASE 4 — DevOps y deployment
## ═══════════════════════════════════════════

```
Usando el agente @devops:

1. Crea `backend/Dockerfile` exactamente como está en el agente @devops.

2. Crea `render.yaml` en la raíz del proyecto con la configuración
   del agente @devops (plan starter, disk de 3GB, healthCheckPath).

3. Crea `.gitignore` en la raíz que excluya:
   - Archivos *.pth y *.pt
   - Carpeta model/
   - .env y .env.*
   - __pycache__ y *.pyc
   - node_modules/
   - .next/

4. Verifica que el README.md incluye los pasos exactos para:
   a. Primer deploy en Render
   b. Subir el archivo .pth al Render Disk
   c. Configurar variables de entorno
   d. Verificar con curl

Ejecuta @reviewer con el checklist completo del proyecto.
Genera un resumen final con todos los archivos creados y
los pasos de deploy listos para ejecutar.
```
