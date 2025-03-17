/**
 * Main data simulation orchestrator
 * 
 * This file coordinates the generation of synthetic blood test data
 * for the Active Patient Follow-Up Alert Dashboard project.
 */

import * as fs from 'fs';
import * as path from 'path';
import { Patient, PatientData } from '../shared/types';
import { generatePatients } from './patientGenerator';
import { 
  generateBloodTestSeries, 
  determinePatientAbnormality 
} from './bloodTestGenerator';

// Configuration with environment variable support for CLI
const CONFIG = {
  // Number of patients to generate
  patientCount: parseInt(process.env.PATIENT_COUNT || '350', 10),
  // Number of tests per patient (average)
  testsPerPatient: {
    min: parseInt(process.env.MIN_TESTS || '3', 10),
    max: parseInt(process.env.MAX_TESTS || '8', 10)
  },
  // Time range for tests (in months)
  timeRange: parseInt(process.env.TIME_RANGE || '6', 10),
  // Probability of a patient having abnormal results
  abnormalProbability: parseFloat(process.env.ABNORMAL_PROBABILITY || '0.3'),
  // Output directory
  outputDir: process.env.OUTPUT_DIR || path.resolve(__dirname, '../../data'),
  // Whether to generate a summary file
  generateSummary: process.env.GENERATE_SUMMARY !== 'false'
};

/**
 * Ensure the output directory exists
 */
function ensureOutputDir(): void {
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
    console.log(`Created output directory: ${CONFIG.outputDir}`);
  }
}

/**
 * Generate data for a single patient and save to file
 */
function generatePatientData(patient: Patient): PatientData {
  // Determine number of tests for this patient
  const testCount = Math.floor(
    Math.random() * (CONFIG.testsPerPatient.max - CONFIG.testsPerPatient.min + 1) + 
    CONFIG.testsPerPatient.min
  );
  
  // Generate blood test series
  const tests = generateBloodTestSeries(
    patient,
    testCount,
    CONFIG.timeRange,
    CONFIG.abnormalProbability
  );
  
  // Determine overall abnormality
  const { label, confidence } = determinePatientAbnormality(tests);
  
  return {
    patient,
    tests,
    label,
    confidence
  };
}

/**
 * Save patient data to JSON file
 */
function savePatientData(patientData: PatientData): void {
  const filePath = path.join(
    CONFIG.outputDir,
    `patient-${patientData.patient.patientId}.json`
  );
  
  fs.writeFileSync(
    filePath,
    JSON.stringify(patientData, null, 2)
  );
}

/**
 * Generate a summary of the dataset
 */
function generateSummary(patientDataList: PatientData[]): void {
  const abnormalCount = patientDataList.filter(p => p.label === 'ABNORMAL').length;
  const normalCount = patientDataList.length - abnormalCount;
  
  const summary = {
    totalPatients: patientDataList.length,
    abnormalPatients: abnormalCount,
    normalPatients: normalCount,
    abnormalPercentage: (abnormalCount / patientDataList.length) * 100,
    averageTestsPerPatient: patientDataList.reduce(
      (sum, p) => sum + p.tests.length, 
      0
    ) / patientDataList.length,
    generatedAt: new Date().toISOString(),
    config: CONFIG
  };
  
  fs.writeFileSync(
    path.join(CONFIG.outputDir, 'summary.json'),
    JSON.stringify(summary, null, 2)
  );
  
  console.log('Dataset Summary:');
  console.log(`- Total Patients: ${summary.totalPatients}`);
  console.log(`- Abnormal Patients: ${summary.abnormalPatients} (${summary.abnormalPercentage.toFixed(1)}%)`);
  console.log(`- Normal Patients: ${summary.normalPatients}`);
  console.log(`- Average Tests Per Patient: ${summary.averageTestsPerPatient.toFixed(1)}`);
}

/**
 * Main function to generate the complete dataset
 */
export function generateDataset(): void {
  console.log('Starting blood test data generation...');
  console.time('Data generation completed in');
  
  // Ensure output directory exists
  ensureOutputDir();
  
  // Generate patients
  const patients = generatePatients(CONFIG.patientCount);
  console.log(`Generated ${patients.length} patient profiles`);
  
  // Generate and save data for each patient
  const patientDataList: PatientData[] = [];
  
  for (const patient of patients) {
    const patientData = generatePatientData(patient);
    savePatientData(patientData);
    patientDataList.push(patientData);
    
    // Log progress every 10 patients
    if (patientDataList.length % 10 === 0) {
      console.log(`Processed ${patientDataList.length}/${patients.length} patients`);
    }
  }
  
  // Generate summary
  if (CONFIG.generateSummary) {
    generateSummary(patientDataList);
  }
  
  console.timeEnd('Data generation completed in');
  console.log(`Data saved to ${CONFIG.outputDir}`);
}

// If this file is run directly, generate the dataset
if (require.main === module) {
  generateDataset();
}