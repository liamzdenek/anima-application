/**
 * Types for the blood test data simulation
 */

// Blood test result with specific metrics
export interface BloodTest {
  testId: string;
  patientId: string;
  testDate: string;
  // Common Complete Blood Count (CBC) metrics
  hemoglobin: number;      // g/dL
  wbc: number;             // 10^3/μL (White Blood Cells)
  rbc: number;             // 10^6/μL (Red Blood Cells)
  platelets: number;       // 10^3/μL
  hematocrit: number;      // %
  mcv: number;             // fL (Mean Corpuscular Volume)
  mch: number;             // pg (Mean Corpuscular Hemoglobin)
  mchc: number;            // g/dL (Mean Corpuscular Hemoglobin Concentration)
  neutrophils: number;     // %
  lymphocytes: number;     // %
  monocytes: number;       // %
  eosinophils: number;     // %
  basophils: number;       // %
  // Reference ranges (for labeling)
  referenceRanges: BloodTestReferenceRanges;
  // Abnormality flags
  abnormalFlags: AbnormalFlags;
}

// Reference ranges for blood test metrics (varies by gender and age)
export interface BloodTestReferenceRanges {
  hemoglobin: Range;
  wbc: Range;
  rbc: Range;
  platelets: Range;
  hematocrit: Range;
  mcv: Range;
  mch: Range;
  mchc: Range;
  neutrophils: Range;
  lymphocytes: Range;
  monocytes: Range;
  eosinophils: Range;
  basophils: Range;
}

// Range with min and max values
export interface Range {
  min: number;
  max: number;
}

// Flags for abnormal values
export interface AbnormalFlags {
  hemoglobin: boolean;
  wbc: boolean;
  rbc: boolean;
  platelets: boolean;
  hematocrit: boolean;
  mcv: boolean;
  mch: boolean;
  mchc: boolean;
  neutrophils: boolean;
  lymphocytes: boolean;
  monocytes: boolean;
  eosinophils: boolean;
  basophils: boolean;
  // Overall assessment
  isAbnormal: boolean;
  // Confidence score (0-1) for abnormality prediction
  abnormalConfidence: number;
}

// Patient data
export interface Patient {
  patientId: string;
  age: number;
  gender: 'M' | 'F';
  // Additional demographic info
  medicalHistory: string[];
  // Tests will be stored separately
}

// Complete patient data with tests (for output)
export interface PatientData {
  patient: Patient;
  tests: BloodTest[];
  // ML-ready label
  label: 'NORMAL' | 'ABNORMAL';
  confidence: number;
}