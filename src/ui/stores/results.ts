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
  
  return {
    aucRoc: info.metrics.auc_roc || 0,
    sensitivity: info.metrics.sensitivity || 0,
    specificity: info.metrics.specificity || 0,
    f1Score: info.metrics.f1_score || 0,
    fairnessDelta: info.metrics.fairness_delta || 0,
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
  aucRoc: 0.85,
  sensitivity: 0.95,
  specificity: 0.70,
  f1Score: 0.80,
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