/**
 * API configuration
 */

// Get API endpoint from environment variable or use default
export const API_BASE_URL = import.meta.env.VITE_API_ENDPOINT || 'http://localhost:3000/api';

// API endpoints
export const ENDPOINTS = {
  PREDICT: `${API_BASE_URL}/predict`,
  MODEL_INFO: `${API_BASE_URL}/model-info`,
  HEALTH: `${API_BASE_URL}/health`,
};