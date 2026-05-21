# Medical Imaging — Análisis de Artrosis de Rodilla

## Descripción del proyecto

Microservicio de análisis de radiografías de rodilla mediante IA.
Clasifica automáticamente el grado de artrosis según la escala Kellgren-Lawrence (KL 0–4).

**Métricas del modelo:**
- κ cuadrático ponderado: 0.9758 (validación) / 0.9651 (test)
- AUC-ROC macro: 0.9828
- Accuracy: 89% sobre 3.772 imágenes de test

## Agentes disponibles

| Agente | Cuándo usarlo |
|---|---|
| `arquitecto` | Antes de implementar cualquier módulo nuevo |
| `backend` | Implementar o modificar el microservicio FastAPI |
| `frontend` | Implementar o modificar componentes React |
| `devops` | Configurar deployment, Docker, variables de entorno |
| `reviewer` | Revisar código antes de commit o deploy |

## Stack técnico

- **Backend**: FastAPI + Python 3.12 + PyTorch + timm
- **Modelo**: EfficientNetV2-L con GeM Pooling (checkpoint: `tf_efficientnetv2_l_fold0_best.pth`)
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **DB**: PostgreSQL 16 en Neon (schema: `medical`)
- **Deploy**: Render.com (backend) + Vercel (frontend)

## Estructura del proyecto

```
medical-imaging/
├── .claude/
│   └── agents/
│       ├── arquitecto.md
│       ├── backend.md
│       ├── frontend.md
│       ├── devops.md
│       └── reviewer.md
├── backend/
│   ├── app/
│   │   ├── core/         → config.py, security.py
│   │   ├── models/       → knee_classifier.py
│   │   ├── schemas/      → analysis.py
│   │   ├── routers/      → analysis.py
│   │   └── services/     → inference.py, gradcam.py
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/KneeAnalysis/
│   │   ├── services/
│   │   └── components/
│   └── vercel.json
├── alembic/              → migraciones DB
├── render.yaml
├── CLAUDE.md             → este archivo
└── README.md
```

## Convenciones de código

- Patrón obligatorio: `router → service → schema → model`
- El modelo PyTorch se carga UNA vez al iniciar (singleton)
- El archivo `.pth` NUNCA va en git
- Respuestas API: `{success: true, data: {...}}`
- Locale: `es-CL`
- Soft delete: campo `deleted_at` en todas las tablas
- Variables de entorno: nunca hardcodeadas, siempre desde `.env`

## Archivo crítico

El checkpoint del modelo (`tf_efficientnetv2_l_fold0_best.pth`, ~1.4 GB)
se monta en Render Disk en `/opt/model/` y NO forma parte del repositorio.

## Disclaimer clínico

Todo output de la aplicación debe incluir:
> "Este análisis es una herramienta de apoyo diagnóstico basada en IA.
> No reemplaza el criterio clínico de un médico especialista."
