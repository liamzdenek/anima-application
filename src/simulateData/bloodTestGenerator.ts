/**
 * Blood test data generator
 */

import { 
  BloodTest, 
  BloodTestReferenceRanges, 
  AbnormalFlags, 
  Patient, 
  Range 
} from '../shared/types';
import { 
  generateId, 
  randomInRange, 
  randomDateInPastMonths, 
  formatNumber,
  generateTrendSeries,
  randomBoolean
} from './utils';

// Reference ranges by gender
const maleReferenceRanges: BloodTestReferenceRanges = {
  hemoglobin: { min: 13.5, max: 17.5 },      // g/dL
  wbc: { min: 4.5, max: 11.0 },              // 10^3/μL
  rbc: { min: 4.5, max: 5.9 },               // 10^6/μL
  platelets: { min: 150, max: 450 },         // 10^3/μL
  hematocrit: { min: 41, max: 50 },          // %
  mcv: { min: 80, max: 100 },                // fL
  mch: { min: 27, max: 33 },                 // pg
  mchc: { min: 32, max: 36 },                // g/dL
  neutrophils: { min: 40, max: 60 },         // %
  lymphocytes: { min: 20, max: 40 },         // %
  monocytes: { min: 2, max: 8 },             // %
  eosinophils: { min: 1, max: 4 },           // %
  basophils: { min: 0.5, max: 1 }            // %
};

const femaleReferenceRanges: BloodTestReferenceRanges = {
  hemoglobin: { min: 12.0, max: 15.5 },      // g/dL
  wbc: { min: 4.5, max: 11.0 },              // 10^3/μL
  rbc: { min: 4.0, max: 5.2 },               // 10^6/μL
  platelets: { min: 150, max: 450 },         // 10^3/μL
  hematocrit: { min: 36, max: 44 },          // %
  mcv: { min: 80, max: 100 },                // fL
  mch: { min: 27, max: 33 },                 // pg
  mchc: { min: 32, max: 36 },                // g/dL
  neutrophils: { min: 40, max: 60 },         // %
  lymphocytes: { min: 20, max: 40 },         // %
  monocytes: { min: 2, max: 8 },             // %
  eosinophils: { min: 1, max: 4 },           // %
  basophils: { min: 0.5, max: 1 }            // %
};

/**
 * Get reference ranges based on patient gender and age
 */
function getReferenceRanges(patient: Patient): BloodTestReferenceRanges {
  const baseRanges = patient.gender === 'M' ? maleReferenceRanges : femaleReferenceRanges;
  
  // Adjust ranges for elderly patients
  if (patient.age > 65) {
    return {
      ...baseRanges,
      hemoglobin: {
        min: baseRanges.hemoglobin.min - 0.5,
        max: baseRanges.hemoglobin.max - 0.5
      },
      wbc: {
        min: baseRanges.wbc.min,
        max: baseRanges.wbc.max - 0.5
      }
    };
  }
  
  return baseRanges;
}

/**
 * Check if a value is outside the reference range
 */
function checkIsAbnormal(value: number, range: Range): boolean {
  return value < range.min || value > range.max;
}

/**
 * Calculate abnormality confidence based on how far the value is from the range
 */
function calculateAbnormalConfidence(value: number, range: Range): number {
  if (value >= range.min && value <= range.max) {
    return 0; // Normal
  }
  
  // Calculate how far outside the range the value is
  const rangeWidth = range.max - range.min;
  let distanceFromRange = 0;
  
  if (value < range.min) {
    distanceFromRange = (range.min - value) / rangeWidth;
  } else {
    distanceFromRange = (value - range.max) / rangeWidth;
  }
  
  // Cap at 1.0 and ensure minimum confidence of 0.5 for any abnormal value
  return Math.min(0.5 + distanceFromRange, 1.0);
}

/**
 * Generate a single blood test for a patient
 */
export function generateBloodTest(
  patient: Patient, 
  testDate: string,
  baseValues?: Partial<BloodTest>
): BloodTest {
  const referenceRanges = getReferenceRanges(patient);
  
  // Generate values (either random or based on provided base values)
  const hemoglobin = formatNumber(baseValues?.hemoglobin || 
    randomInRange(referenceRanges.hemoglobin.min - 2, referenceRanges.hemoglobin.max + 2));
  
  const wbc = formatNumber(baseValues?.wbc || 
    randomInRange(referenceRanges.wbc.min - 2, referenceRanges.wbc.max + 3));
  
  const rbc = formatNumber(baseValues?.rbc || 
    randomInRange(referenceRanges.rbc.min - 1, referenceRanges.rbc.max + 1));
  
  const platelets = Math.round(baseValues?.platelets || 
    randomInRange(referenceRanges.platelets.min - 50, referenceRanges.platelets.max + 100));
  
  const hematocrit = formatNumber(baseValues?.hematocrit || 
    randomInRange(referenceRanges.hematocrit.min - 5, referenceRanges.hematocrit.max + 5));
  
  const mcv = formatNumber(baseValues?.mcv || 
    randomInRange(referenceRanges.mcv.min - 10, referenceRanges.mcv.max + 10));
  
  const mch = formatNumber(baseValues?.mch || 
    randomInRange(referenceRanges.mch.min - 5, referenceRanges.mch.max + 5));
  
  const mchc = formatNumber(baseValues?.mchc || 
    randomInRange(referenceRanges.mchc.min - 4, referenceRanges.mchc.max + 4));
  
  const neutrophils = formatNumber(baseValues?.neutrophils || 
    randomInRange(referenceRanges.neutrophils.min - 10, referenceRanges.neutrophils.max + 15));
  
  const lymphocytes = formatNumber(baseValues?.lymphocytes || 
    randomInRange(referenceRanges.lymphocytes.min - 5, referenceRanges.lymphocytes.max + 10));
  
  const monocytes = formatNumber(baseValues?.monocytes || 
    randomInRange(referenceRanges.monocytes.min - 1, referenceRanges.monocytes.max + 3));
  
  const eosinophils = formatNumber(baseValues?.eosinophils || 
    randomInRange(referenceRanges.eosinophils.min - 0.5, referenceRanges.eosinophils.max + 2));
  
  const basophils = formatNumber(baseValues?.basophils || 
    randomInRange(referenceRanges.basophils.min - 0.2, referenceRanges.basophils.max + 0.5));
  
  // Calculate abnormality flags
  const abnormalFlags: AbnormalFlags = {
    hemoglobin: checkIsAbnormal(hemoglobin, referenceRanges.hemoglobin),
    wbc: checkIsAbnormal(wbc, referenceRanges.wbc),
    rbc: checkIsAbnormal(rbc, referenceRanges.rbc),
    platelets: checkIsAbnormal(platelets, referenceRanges.platelets),
    hematocrit: checkIsAbnormal(hematocrit, referenceRanges.hematocrit),
    mcv: checkIsAbnormal(mcv, referenceRanges.mcv),
    mch: checkIsAbnormal(mch, referenceRanges.mch),
    mchc: checkIsAbnormal(mchc, referenceRanges.mchc),
    neutrophils: checkIsAbnormal(neutrophils, referenceRanges.neutrophils),
    lymphocytes: checkIsAbnormal(lymphocytes, referenceRanges.lymphocytes),
    monocytes: checkIsAbnormal(monocytes, referenceRanges.monocytes),
    eosinophils: checkIsAbnormal(eosinophils, referenceRanges.eosinophils),
    basophils: checkIsAbnormal(basophils, referenceRanges.basophils),
    isAbnormal: false, // Will be calculated below
    abnormalConfidence: 0 // Will be calculated below
  };
  
  // Calculate overall abnormality
  // Count only the actual metric flags, not the isAbnormal or abnormalConfidence properties
  const abnormalCount = [
    abnormalFlags.hemoglobin,
    abnormalFlags.wbc,
    abnormalFlags.rbc,
    abnormalFlags.platelets,
    abnormalFlags.hematocrit,
    abnormalFlags.mcv,
    abnormalFlags.mch,
    abnormalFlags.mchc,
    abnormalFlags.neutrophils,
    abnormalFlags.lymphocytes,
    abnormalFlags.monocytes,
    abnormalFlags.eosinophils,
    abnormalFlags.basophils
  ].filter(Boolean).length;
  
  const isAbnormal = abnormalCount >= 2; // Consider abnormal if 2+ metrics are outside range
  
  // Calculate confidence based on number and severity of abnormalities
  let confidenceSum = 0;
  let confidenceCount = 0;
  
  if (abnormalFlags.hemoglobin) {
    confidenceSum += calculateAbnormalConfidence(hemoglobin, referenceRanges.hemoglobin);
    confidenceCount++;
  }
  
  if (abnormalFlags.wbc) {
    confidenceSum += calculateAbnormalConfidence(wbc, referenceRanges.wbc);
    confidenceCount++;
  }
  
  if (abnormalFlags.platelets) {
    confidenceSum += calculateAbnormalConfidence(platelets, referenceRanges.platelets);
    confidenceCount++;
  }
  
  if (abnormalFlags.hematocrit) {
    confidenceSum += calculateAbnormalConfidence(hematocrit, referenceRanges.hematocrit);
    confidenceCount++;
  }
  
  // Calculate average confidence
  const abnormalConfidence = confidenceCount > 0 
    ? formatNumber(confidenceSum / confidenceCount) 
    : 0;
  
  abnormalFlags.isAbnormal = isAbnormal;
  abnormalFlags.abnormalConfidence = abnormalConfidence;
  
  return {
    testId: generateId('T', 10),
    patientId: patient.patientId,
    testDate,
    hemoglobin,
    wbc,
    rbc,
    platelets,
    hematocrit,
    mcv,
    mch,
    mchc,
    neutrophils,
    lymphocytes,
    monocytes,
    eosinophils,
    basophils,
    referenceRanges,
    abnormalFlags
  };
}

/**
 * Generate a series of blood tests for a patient over time
 */
export function generateBloodTestSeries(
  patient: Patient, 
  count: number, 
  monthsRange: number = 6,
  abnormalProbability: number = 0.3
): BloodTest[] {
  const tests: BloodTest[] = [];
  const dates: string[] = [];
  
  // Generate dates in chronological order
  for (let i = 0; i < count; i++) {
    dates.push(randomDateInPastMonths(monthsRange));
  }
  
  // Sort dates chronologically
  dates.sort();
  
  // Decide if this patient will have an abnormal trend
  const hasAbnormalTrend = randomBoolean(abnormalProbability);
  
  // If abnormal, decide which metric will trend abnormally
  let abnormalMetric: keyof Omit<BloodTest, 'testId' | 'patientId' | 'testDate' | 'referenceRanges' | 'abnormalFlags'> | null = null;
  
  if (hasAbnormalTrend) {
    const metrics = [
      'hemoglobin', 'wbc', 'rbc', 'platelets', 'hematocrit',
      'mcv', 'mch', 'mchc', 'neutrophils', 'lymphocytes'
    ];
    abnormalMetric = metrics[Math.floor(Math.random() * metrics.length)] as any;
  }
  
  // Generate base values for the first test
  let baseValues: Partial<BloodTest> = {};
  
  // Generate the series of tests
  for (let i = 0; i < count; i++) {
    // If this is an abnormal series, adjust the abnormal metric
    if (hasAbnormalTrend && abnormalMetric && i > 0) {
      const referenceRanges = getReferenceRanges(patient);
      const range = referenceRanges[abnormalMetric as keyof BloodTestReferenceRanges];
      
      // Decide direction of abnormality (high or low)
      const direction = randomBoolean() ? 1 : -1;
      
      // For later tests in the series, increase the abnormality
      const trendFactor = 0.05 * Math.min(i, 3); // Cap the trend factor
      
      // Get previous value
      const prevValue = (tests[i-1] as any)[abnormalMetric];
      
      // Calculate new value with trend
      let newValue;
      if (direction > 0) {
        // Trending high
        newValue = prevValue * (1 + trendFactor);
        // Ensure it eventually goes above range
        if (i >= count - 2) {
          newValue = Math.max(newValue, range.max * 1.1);
        }
      } else {
        // Trending low
        newValue = prevValue * (1 - trendFactor);
        // Ensure it eventually goes below range
        if (i >= count - 2) {
          newValue = Math.min(newValue, range.min * 0.9);
        }
      }
      
      baseValues = {
        ...baseValues,
        [abnormalMetric]: formatNumber(newValue)
      };
    }
    
    // Generate the test
    const test = generateBloodTest(patient, dates[i], baseValues);
    tests.push(test);
    
    // Use this test as the base for the next one (for continuity)
    baseValues = {
      hemoglobin: test.hemoglobin,
      wbc: test.wbc,
      rbc: test.rbc,
      platelets: test.platelets,
      hematocrit: test.hematocrit,
      mcv: test.mcv,
      mch: test.mch,
      mchc: test.mchc,
      neutrophils: test.neutrophils,
      lymphocytes: test.lymphocytes,
      monocytes: test.monocytes,
      eosinophils: test.eosinophils,
      basophils: test.basophils
    };
  }
  
  return tests;
}

/**
 * Determine if a patient's test series is abnormal
 */
export function determinePatientAbnormality(tests: BloodTest[]): {
  label: 'NORMAL' | 'ABNORMAL';
  confidence: number;
} {
  // Count abnormal tests
  const abnormalTests = tests.filter(test => test.abnormalFlags.isAbnormal);
  const abnormalRatio = abnormalTests.length / tests.length;
  
  // Calculate average confidence across abnormal tests
  const totalConfidence = abnormalTests.reduce(
    (sum, test) => sum + test.abnormalFlags.abnormalConfidence,
    0
  );
  
  const avgConfidence = abnormalTests.length > 0
    ? formatNumber(totalConfidence / abnormalTests.length)
    : 0;
  
  // Determine overall label
  // A patient is considered abnormal if:
  // 1. More than 30% of their tests are abnormal, OR
  // 2. Any test has a very high abnormality confidence (>0.8)
  // BUT we also want to respect the overall abnormalProbability setting
  
  // First, determine if this patient would be abnormal based on their tests
  const hasAbnormalTests = abnormalRatio >= 0.3 ||
    tests.some(test => test.abnormalFlags.abnormalConfidence > 0.8);
  
  // Then, apply a random factor to ensure we get the right distribution
  // This is a simplified approach - in a real system, the abnormality would be
  // determined purely by the test results and medical criteria
  const abnormalProbability = parseFloat(process.env.ABNORMAL_PROBABILITY || '0.3');
  const isAbnormal = hasAbnormalTests && Math.random() < abnormalProbability;
  
  return {
    label: isAbnormal ? 'ABNORMAL' : 'NORMAL',
    confidence: isAbnormal ? avgConfidence : 1 - avgConfidence
  };
}