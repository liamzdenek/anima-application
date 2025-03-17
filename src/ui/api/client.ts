/**
 * API client for the RN Blood Test Interface
 */
import { TestFormData, PredictionRequest, PredictionResponse, ModelInfo } from './types';

const API_BASE_URL = 'http://localhost:3000/api';

/**
 * Convert form data to API request format
 */
export function formDataToRequest(formData: TestFormData): PredictionRequest {
  return {
    patient: {
      patientId: formData.patientId,
      age: formData.age,
      gender: formData.gender,
      tests: [{
        testId: formData.testId,
        testDate: formData.testDate,
        hemoglobin: formData.hemoglobin,
        hemoglobinMin: formData.hemoglobinMin,
        hemoglobinMax: formData.hemoglobinMax,
        wbc: formData.wbc,
        wbcMin: formData.wbcMin,
        wbcMax: formData.wbcMax,
        platelets: formData.platelets,
        plateletsMin: formData.plateletsMin,
        plateletsMax: formData.plateletsMax,
        neutrophils: formData.neutrophils,
        neutrophilsMin: formData.neutrophilsMin,
        neutrophilsMax: formData.neutrophilsMax,
        lymphocytes: formData.lymphocytes,
        lymphocytesMin: formData.lymphocytesMin,
        lymphocytesMax: formData.lymphocytesMax,
        rbc: formData.rbc,
        rbcMin: formData.rbcMin,
        rbcMax: formData.rbcMax,
        mcv: formData.mcv,
        mcvMin: formData.mcvMin,
        mcvMax: formData.mcvMax,
        mch: formData.mch,
        mchMin: formData.mchMin,
        mchMax: formData.mchMax,
      }]
    }
  };
}

/**
 * Make a prediction request to the API
 */
export async function predictAbnormality(formData: TestFormData): Promise<PredictionResponse> {
  const request = formDataToRequest(formData);
  
  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error (${response.status}): ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Prediction request failed:', error);
    throw error;
  }
}

/**
 * Get model information from the API
 */
export async function getModelInfo(): Promise<ModelInfo> {
  try {
    const response = await fetch(`${API_BASE_URL}/model-info`);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error (${response.status}): ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Model info request failed:', error);
    throw error;
  }
}

/**
 * Check API health
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
}