/**
 * Patient data generator
 */

import { Patient } from '../shared/types';
import { 
  generateId, 
  randomIntInRange, 
  randomPick, 
  randomBoolean,
  commonMedicalConditions
} from './utils';

/**
 * Generate a random patient
 */
export function generatePatient(): Patient {
  const gender = randomBoolean(0.5) ? 'M' : 'F';
  const age = randomIntInRange(18, 85);
  
  return {
    patientId: generateId('P', 8),
    age,
    gender,
    medicalHistory: generateMedicalHistory(age)
  };
}

/**
 * Generate a realistic medical history based on age
 */
function generateMedicalHistory(age: number): string[] {
  const history: string[] = [];
  
  // Older patients tend to have more conditions
  const conditionCount = Math.min(
    randomIntInRange(0, Math.floor(age / 15)),
    5 // Cap at 5 conditions
  );
  
  // Ensure no duplicates
  const availableConditions = [...commonMedicalConditions];
  
  for (let i = 0; i < conditionCount; i++) {
    if (availableConditions.length === 0) break;
    
    const index = randomIntInRange(0, availableConditions.length - 1);
    const condition = availableConditions[index];
    
    if (condition !== 'None') {
      history.push(condition);
      // Remove the selected condition to avoid duplicates
      availableConditions.splice(index, 1);
    }
  }
  
  // If no conditions were added, add 'None'
  if (history.length === 0) {
    history.push('None');
  }
  
  return history;
}

/**
 * Generate a batch of patients
 */
export function generatePatients(count: number): Patient[] {
  const patients: Patient[] = [];
  
  for (let i = 0; i < count; i++) {
    patients.push(generatePatient());
  }
  
  return patients;
}