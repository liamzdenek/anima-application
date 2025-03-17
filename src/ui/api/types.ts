/**
 * API types for the RN Blood Test Interface
 * Adapted from src/shared/types.ts and src/inference/schemas.py
 */

// Test result form data
export interface TestFormData {
  // Patient information
  patientId: string;
  age?: number;
  gender?: 'M' | 'F';
  
  // Test metadata
  testId: string;
  testDate: string;
  
  // Test values with reference ranges
  hemoglobin: number;
  hemoglobinMin: number;
  hemoglobinMax: number;
  
  wbc: number;
  wbcMin: number;
  wbcMax: number;
  
  platelets: number;
  plateletsMin: number;
  plateletsMax: number;
  
  neutrophils: number;
  neutrophilsMin: number;
  neutrophilsMax: number;
  
  lymphocytes: number;
  lymphocytesMin: number;
  lymphocytesMax: number;
  
  rbc: number;
  rbcMin: number;
  rbcMax: number;
  
  mcv: number;
  mcvMin: number;
  mcvMax: number;
  
  mch: number;
  mchMin: number;
  mchMax: number;
}

// API request format
export interface PredictionRequest {
  patient: {
    patientId: string;
    age?: number;
    gender?: string;
    tests: [{
      testId: string;
      testDate: string;
      hemoglobin: number;
      hemoglobinMin: number;
      hemoglobinMax: number;
      wbc: number;
      wbcMin: number;
      wbcMax: number;
      platelets: number;
      plateletsMin: number;
      plateletsMax: number;
      neutrophils: number;
      neutrophilsMin: number;
      neutrophilsMax: number;
      lymphocytes: number;
      lymphocytesMin: number;
      lymphocytesMax: number;
      rbc: number;
      rbcMin: number;
      rbcMax: number;
      mcv: number;
      mcvMin: number;
      mcvMax: number;
      mch: number;
      mchMin: number;
      mchMax: number;
    }]
  }
}

// Feature contribution in prediction response
export interface FeatureContribution {
  feature: string;
  value: number;
  contribution: number;
  is_abnormal: boolean;
}

// API response format
export interface PredictionResponse {
  patientId: string;
  prediction: 'NORMAL' | 'ABNORMAL';
  probability: number;
  confidence: number;
  risk_score: number;
  top_contributors: FeatureContribution[];
  model_version: string;
  timestamp: string;
}

// Model information
export interface ModelInfo {
  name: string;
  version: string;
  created_at: string;
  metrics: Record<string, any>;
  feature_importance?: Record<string, number>;
}

// Health check response
export interface HealthCheckResponse {
  status: string;
  model_loaded: boolean;
  model_version?: string;
}