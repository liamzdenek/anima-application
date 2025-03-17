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

// Normal test data for demonstration
const normalTestData: TestFormData = {
  patientId: 'P-123456',
  age: 45,
  gender: 'F',
  testId: 'TEST-789012',
  testDate: new Date().toISOString().split('T')[0],
  
  // CBC values within normal range for a 45-year-old female
  hemoglobin: 13.5,
  hemoglobinMin: 12.0,
  hemoglobinMax: 16.0,
  
  wbc: 7.2,
  wbcMin: 4.5,
  wbcMax: 11.0,
  
  platelets: 250,
  plateletsMin: 150,
  plateletsMax: 450,
  
  neutrophils: 4.1,
  neutrophilsMin: 2.0,
  neutrophilsMax: 7.5,
  
  lymphocytes: 2.3,
  lymphocytesMin: 1.0,
  lymphocytesMax: 4.5,
  
  rbc: 4.6,
  rbcMin: 4.0,
  rbcMax: 5.5,
  
  mcv: 90,
  mcvMin: 80,
  mcvMax: 100,
  
  mch: 30,
  mchMin: 27,
  mchMax: 33,
};

// Abnormal test data for demonstration
const abnormalTestData: TestFormData = {
  patientId: 'P-654321',
  age: 52,
  gender: 'M',
  testId: 'TEST-987654',
  testDate: new Date().toISOString().split('T')[0],
  
  // CBC values with several abnormal parameters
  hemoglobin: 10.2, // Low
  hemoglobinMin: 13.5,
  hemoglobinMax: 17.5,
  
  wbc: 15.8, // High
  wbcMin: 4.5,
  wbcMax: 11.0,
  
  platelets: 120, // Low
  plateletsMin: 150,
  plateletsMax: 450,
  
  neutrophils: 12.5, // High
  neutrophilsMin: 2.0,
  neutrophilsMax: 7.5,
  
  lymphocytes: 0.8, // Low
  lymphocytesMin: 1.0,
  lymphocytesMax: 4.5,
  
  rbc: 3.8, // Low
  rbcMin: 4.5,
  rbcMax: 5.9,
  
  mcv: 75, // Low
  mcvMin: 80,
  mcvMax: 100,
  
  mch: 25, // Low
  mchMin: 27,
  mchMax: 33,
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

// Demo data events
export const loadNormalTestData = createEvent();
export const loadAbnormalTestData = createEvent();

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
  })
  // Handle demo data loading
  .on(loadNormalTestData, () => normalTestData)
  .on(loadAbnormalTestData, () => abnormalTestData);

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