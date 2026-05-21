import axios from 'axios';

export interface AnalysisResult {
  id: string;
  patient_id?: string;
  kl_grade: number;
  confidence: number;
  probabilities: Record<string, number>;
  processing_time_ms: number;
  gradcam_base64?: string | null;
  created_at: string;
  notes?: string;
}

export const analyzeXray = async (
  file: File,
  patientId?: string,
  includeGradcam = false
): Promise<AnalysisResult> => {
  const formData = new FormData();
  formData.append('file', file);
  if (patientId) {
    formData.append('patientId', patientId);
  }
  formData.append('includeGradcam', includeGradcam.toString());

  try {
    const response = await axios.post(
      '/api/v1/medical/analyze',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    
    if (response.data && response.data.success && response.data.data) {
      return response.data.data;
    } else {
      throw new Error('Respuesta de API inválida');
    }
  } catch (error: any) {
    console.error('Error en analyzeXray:', error);
    
    // Manejo de errores con mensajes en español
    if (error.response) {
      // El servidor respondió con un código de estado fuera de 2xx
      throw new Error(
        error.response.data?.detail || 
        `Error del servidor: ${error.response.status}`
      );
    } else if (error.request) {
      // Se hizo la solicitud pero no se recibió respuesta
      throw new Error('No se pudo conectar con el servidor. Verifique su conexión.');
    } else {
      // Algo ocurrió al configurar la solicitud
      throw new Error(`Error al configurar la solicitud: ${error.message}`);
    }
  }
};