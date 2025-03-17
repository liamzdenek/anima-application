/**
 * Test data store using Effector
 */
import { createStore, createEvent, createEffect } from 'effector';
import { TestFormData } from '../api/types';
import { predictAbnormality } from '../api/client';

// Default form values with empty strings for text fields and 0 for numeric fields
const defaultFormData: TestFormData = {
  patientId: '',
  age: undefined,
  gender: undefined,
  testId: '',
  testDate: new Date().toISOString().split('T')[0],
  
  hemoglobin: 0,
  hemoglobinMin: 0,
  hemoglobinMax: 0,
  
  wbc: 0,
  wbcMin: 0,
  wbcMax: 0,
  
  platelets: 0,
  plateletsMin: 0,
  plateletsMax: 0,
  
  neutrophils: 0,
  neutrophilsMin: 0,
  neutrophilsMax: 0,
  
  lymphocytes: 0,
  lymphocytesMin: 0,
  lymphocytesMax: 0,
  
  rbc: 0,
  rbcMin: 0,
  rbcMax: 0,
  
  mcv: 0,
  mcvMin: 0,
  mcvMax: 0,
  
  mch: 0,
  mchMin: 0,
  mchMax: 0,
};

// Events
export const updateField = createEvent<{
  field: keyof TestFormData;
  value: string | number | undefined;
}>();

export const resetForm = createEvent();

export const setDefaultRanges = createEvent<{
  gender?: 'M' | 'F';
  age?: number;
}>();

// Effects
export const submitTestFx = createEffect(async (formData: TestFormData) => {
  return await predictAbnormality(formData);
});

// Store
export const $testForm = createStore<TestFormData>(defaultFormData)
  .on(updateField, (state, { field, value }) => ({
    ...state,
    [field]: value,
  }))
  .on(resetForm, () => defaultFormData)
  .on(setDefaultRanges, (state, { gender, age }) => {
    // Set default reference ranges based on gender and age
    // These values are simplified examples and should be replaced with actual reference ranges
    if (gender === 'M') {
      return {
        ...state,
        hemoglobinMin: 13.5,
        hemoglobinMax: 17.5,
        wbcMin: 4.5,
        wbcMax: 11.0,
        plateletsMin: 150,
        plateletsMax: 450,
        neutrophilsMin: 2.0,
        neutrophilsMax: 7.5,
        lymphocytesMin: 1.0,
        lymphocytesMax: 4.5,
        rbcMin: 4.5,
        rbcMax: 5.9,
        mcvMin: 80,
        mcvMax: 100,
        mchMin: 27,
        mchMax: 33,
      };
    } else if (gender === 'F') {
      return {
        ...state,
        hemoglobinMin: 12.0,
        hemoglobinMax: 16.0,
        wbcMin: 4.5,
        wbcMax: 11.0,
        plateletsMin: 150,
        plateletsMax: 450,
        neutrophilsMin: 2.0,
        neutrophilsMax: 7.5,
        lymphocytesMin: 1.0,
        lymphocytesMax: 4.5,
        rbcMin: 4.0,
        rbcMax: 5.5,
        mcvMin: 80,
        mcvMax: 100,
        mchMin: 27,
        mchMax: 33,
      };
    }
    return state;
  });

// Validation
export const $formErrors = $testForm.map((form) => {
  const errors: Partial<Record<keyof TestFormData, string>> = {};
  
  if (!form.patientId) {
    errors.patientId = 'Patient ID is required';
  }
  
  if (!form.testId) {
    errors.testId = 'Test ID is required';
  }
  
  if (!form.testDate) {
    errors.testDate = 'Test date is required';
  }
  
  // Add validation for numeric fields
  const numericFields: Array<keyof TestFormData> = [
    'hemoglobin', 'wbc', 'platelets', 'neutrophils', 
    'lymphocytes', 'rbc', 'mcv', 'mch'
  ];
  
  numericFields.forEach((field) => {
    const value = form[field];
    if (typeof value !== 'number' || isNaN(value)) {
      errors[field] = `${field} must be a number`;
    }
  });
  
  return errors;
});

export const $isFormValid = $formErrors.map((errors) => Object.keys(errors).length === 0);