---
name: frontend
description: Implementa la interfaz React para el módulo de análisis de radiografías de rodilla. Conoce los componentes requeridos, el contrato de la API y las convenciones de diseño del proyecto.
---

# Developer Frontend — Medical Imaging UI

## Stack
- React 18 + TypeScript + Tailwind CSS
- Desplegado en Vercel
- Proxy: `/medical/*` → `https://medical-imaging-api.onrender.com`

## Contrato de la API

### POST /medical/api/v1/medical/analyze
```typescript
// Request: FormData
// - file: File (image/jpeg | image/png, max 10MB)
// - patient_id?: string
// - include_gradcam?: boolean (default: true)

// Response:
interface AnalysisResult {
  analysis_id:        string
  patient_id:         string | null
  kl_grade:           number        // 0-4
  kl_description:     string
  confidence:         number        // 0-1
  probabilities:      Record<string, number>  // {"KL-0": 0.05, ...}
  gradcam_base64:     string | null // "data:image/png;base64,..."
  processing_time_ms: number
  model_version:      string
  created_at:         string
}
```

## Componentes a implementar

### 1. UploadZone.tsx
- Drag & drop de imágenes de radiografías
- Click para abrir explorador de archivos
- Validación: solo JPG/PNG, máx 10MB
- Preview de la imagen seleccionada
- Estado visual: idle / dragover / uploading / error

### 2. ResultCard.tsx
Colores por grado KL:
```typescript
const KL_COLORS = {
  0: "bg-green-100 text-green-800 border-green-300",   // Normal
  1: "bg-yellow-100 text-yellow-800 border-yellow-300", // Dudoso
  2: "bg-orange-100 text-orange-800 border-orange-300", // Mínimo
  3: "bg-red-100 text-red-800 border-red-300",          // Moderado
  4: "bg-red-200 text-red-900 border-red-400",          // Severo
}
```
Mostrar:
- Badge con grado KL y etiqueta
- Descripción clínica
- Barra de confianza
- Barras de probabilidad por clase (KL-0 a KL-4)
- Tiempo de procesamiento y versión del modelo

### 3. GradCAMView.tsx
- Mostrar imagen base64 del heatmap
- Etiqueta: "Mapa de activación — zonas que determinaron el diagnóstico"
- Nota aclaratoria sobre interpretación

### 4. KLGradeBar.tsx
- Componente reutilizable: barra horizontal coloreada por grado KL
- Props: grade (0-4), value (0-1), label (string)

### 5. index.tsx (página principal)
- Layout de 2 columnas en desktop, 1 en mobile
- Estados: idle / loading / result / error
- Disclaimer clínico OBLIGATORIO al pie (fondo amber)

## Disclaimer clínico (texto exacto requerido)
```
⚠️ Este análisis es una herramienta de apoyo diagnóstico basada en IA.
No reemplaza el criterio clínico de un médico especialista.
Los resultados deben ser interpretados por un profesional de salud calificado.
```

## Servicio API
```typescript
// src/services/medicalAnalysis.ts
const BASE = process.env.NEXT_PUBLIC_MEDICAL_API_URL ?? "/medical"

export async function analyzeXray(
  file: File,
  patientId?: string,
  includeGradcam = true
): Promise<AnalysisResult>
```

## vercel.json (proxy)
```json
{
  "rewrites": [
    {
      "source": "/medical/:path*",
      "destination": "https://medical-imaging-api.onrender.com/:path*"
    }
  ]
}
```

## Convenciones
- Locale es-CL para fechas y números
- Sin `<form>` tags — usar onClick/onChange
- Tailwind únicamente, sin CSS custom salvo necesidad extrema
- Skeleton loaders durante carga (no spinners simples)
- Manejo explícito de errores con mensajes en español
