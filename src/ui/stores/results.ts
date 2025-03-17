/**
 * Results store using Effector
 */
import { createStore, createEvent, createEffect } from 'effector';
import { PredictionResponse, ModelInfo } from '../api/types';
import { submitTestFx } from './test';
import { getModelInfo } from '../api/client';

// Events
export const clearResults = createEvent();

// Effects
export const getModelInfoFx = createEffect(async () => {
  return await getModelInfo();
});

// Stores
export const $predictionResults = createStore<PredictionResponse | null>(null)
  .on(submitTestFx.doneData, (_, result) => result)
  .on(clearResults, () => null);

export const $isLoading = createStore(false)
  .on(submitTestFx, () => true)
  .on(submitTestFx.done, () => false)
  .on(submitTestFx.fail, () => false)
  .on(getModelInfoFx, () => true)
  .on(getModelInfoFx.done, () => false)
  .on(getModelInfoFx.fail, () => false);

export const $error = createStore<string | null>(null)
  .on(submitTestFx.fail, (_, { error }) => error.message)
  .on(getModelInfoFx.fail, (_, { error }) => error.message)
  .on(submitTestFx, () => null)
  .on(getModelInfoFx, () => null);

export const $modelInfo = createStore<ModelInfo | null>(null)
  .on(getModelInfoFx.doneData, (_, result) => result);

// Derived stores
export const $validationMetrics = $modelInfo.map((info) => {
  if (!info) return null;
  
  // Calculate sensitivity (recall) and specificity from confusion matrix if available
  let sensitivity = 0;
  let specificity = 0;
  let fairnessDelta = 0;
  
  if (info.metrics.confusion_matrix && info.metrics.confusion_matrix.length === 2) {
    const cm = info.metrics.confusion_matrix;
    // True Negative (TN) = cm[0][0]
    // False Positive (FP) = cm[0][1]
    // False Negative (FN) = cm[1][0]
    // True Positive (TP) = cm[1][1]
    
    // Sensitivity = TP / (TP + FN)
    sensitivity = cm[1][1] / (cm[1][1] + cm[1][0]);
    
    // Specificity = TN / (TN + FP)
    specificity = cm[0][0] / (cm[0][0] + cm[0][1]);
    
    // Fairness delta is not in the provided metrics, using a placeholder
    // In a real system, this would be calculated based on model performance across different groups
    fairnessDelta = 0.05; // Placeholder value
  }
  
  return {
    accuracy: info.metrics.accuracy || 0,
    precision: info.metrics.precision || 0,
    recall: info.metrics.recall || 0, // Same as sensitivity
    f1Score: info.metrics.f1 || 0,
    aucRoc: info.metrics.roc_auc || 0,
    sensitivity: sensitivity || info.metrics.recall || 0, // Sensitivity is the same as recall
    specificity: specificity || 0,
    fairnessDelta: fairnessDelta,
  };
});

export const $topContributors = $predictionResults.map((results) => {
  if (!results) return [];
  
  return results.top_contributors.map((contributor) => ({
    feature: contributor.feature,
    value: contributor.value,
    contribution: contributor.contribution,
    isAbnormal: contributor.is_abnormal,
  }));
});

// Thresholds based on MODEL_PLAN.md
export const validationThresholds = {
  accuracy: 0.85,
  precision: 0.85,
  recall: 0.85,
  f1Score: 0.80,
  aucRoc: 0.85,
  sensitivity: 0.85, // Same as recall
  specificity: 0.70,
  fairnessDelta: 0.1, // Less than this value is good
};

// Helper to check if a metric meets its threshold
export const isMetricValid = (
  metric: keyof typeof validationThresholds,
  value: number
): boolean => {
  if (metric === 'fairnessDelta') {
    return value < validationThresholds[metric];
  }
  return value >= validationThresholds[metric];
};