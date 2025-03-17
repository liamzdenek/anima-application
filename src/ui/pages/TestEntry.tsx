/**
 * Test Entry page component
 */
import React, { useEffect } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useStore, useEvent } from 'effector-react';
import {
  $testForm,
  $formErrors,
  $isFormValid,
  updateField,
  resetForm,
  setDefaultRanges,
  submitTestFx,
  loadNormalTestData,
  loadAbnormalTestData
} from '../stores/test';
import { $isLoading, $error } from '../stores/results';
import styles from './TestEntry.module.css';

export function TestEntryPage() {
  const navigate = useNavigate();
  const formData = useStore($testForm);
  const formErrors = useStore($formErrors);
  const isFormValid = useStore($isFormValid);
  const isLoading = useStore($isLoading);
  const error = useStore($error);
  
  const handleUpdateField = useEvent(updateField);
  const handleResetForm = useEvent(resetForm);
  const handleSetDefaultRanges = useEvent(setDefaultRanges);
  const handleLoadNormalData = useEvent(loadNormalTestData);
  const handleLoadAbnormalData = useEvent(loadAbnormalTestData);
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isFormValid) return;
    
    try {
      await submitTestFx(formData);
      navigate({ to: '/results' });
    } catch (error) {
      console.error('Submission error:', error);
    }
  };
  
  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    // Handle numeric fields
    if (e.target.type === 'number') {
      handleUpdateField({
        field: name as keyof typeof formData,
        value: value === '' ? 0 : parseFloat(value),
      });
    } else {
      handleUpdateField({
        field: name as keyof typeof formData,
        value,
      });
    }
    
    // Set default ranges when gender is selected
    if (name === 'gender') {
      handleSetDefaultRanges({
        gender: value as 'M' | 'F',
        age: formData.age,
      });
    }
  };
  
  // Generate a random test ID on component mount
  useEffect(() => {
    const testId = `TEST-${Math.floor(Math.random() * 1000000)}`;
    handleUpdateField({ field: 'testId', value: testId });
  }, []);
  
  return (
    <div className={styles.testEntryPage}>
      <h2>Enter Blood Test Results</h2>
      
      {error && (
        <div className={styles.errorMessage}>
          <p>{error}</p>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className={styles.testForm}>
        <div className={styles.formSection}>
          <h3>Patient Information</h3>
          
          <div className={styles.formGroup}>
            <label htmlFor="patientId">Patient ID</label>
            <input
              type="text"
              id="patientId"
              name="patientId"
              value={formData.patientId}
              onChange={handleInputChange}
              required
            />
            {formErrors.patientId && (
              <div className={styles.fieldError}>{formErrors.patientId}</div>
            )}
          </div>
          
          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="age">Age</label>
              <input
                type="number"
                id="age"
                name="age"
                value={formData.age || ''}
                onChange={handleInputChange}
              />
            </div>
            
            <div className={styles.formGroup}>
              <label htmlFor="gender">Gender</label>
              <select
                id="gender"
                name="gender"
                value={formData.gender || ''}
                onChange={handleInputChange}
              >
                <option value="">Select</option>
                <option value="M">Male</option>
                <option value="F">Female</option>
              </select>
            </div>
          </div>
          
          <div className={styles.formGroup}>
            <label htmlFor="testDate">Test Date</label>
            <input
              type="date"
              id="testDate"
              name="testDate"
              value={formData.testDate}
              onChange={handleInputChange}
              required
            />
            {formErrors.testDate && (
              <div className={styles.fieldError}>{formErrors.testDate}</div>
            )}
          </div>
        </div>
        
        <div className={styles.formSection}>
          <h3>Complete Blood Count (CBC)</h3>
          
          {/* Hemoglobin */}
          <div className={styles.testFieldGroup}>
            <div className={styles.testFieldLabel}>
              <label htmlFor="hemoglobin">Hemoglobin (g/dL)</label>
            </div>
            <div className={styles.testFieldInputs}>
              <div className={styles.testFieldValue}>
                <input
                  type="number"
                  id="hemoglobin"
                  name="hemoglobin"
                  value={formData.hemoglobin || ''}
                  onChange={handleInputChange}
                  step="0.1"
                  required
                  placeholder={`${formData.hemoglobinMin || '12.0'} - ${formData.hemoglobinMax || '16.0'}`}
                />
                {formErrors.hemoglobin && (
                  <div className={styles.fieldError}>{formErrors.hemoglobin}</div>
                )}
              </div>
              <div className={styles.testFieldRange}>
                <input
                  type="number"
                  id="hemoglobinMin"
                  name="hemoglobinMin"
                  placeholder="Min"
                  value={formData.hemoglobinMin || ''}
                  onChange={handleInputChange}
                  step="0.1"
                />
                <span>-</span>
                <input
                  type="number"
                  id="hemoglobinMax"
                  name="hemoglobinMax"
                  placeholder="Max"
                  value={formData.hemoglobinMax || ''}
                  onChange={handleInputChange}
                  step="0.1"
                />
              </div>
            </div>
          </div>
          
          {/* WBC */}
          <div className={styles.testFieldGroup}>
            <div className={styles.testFieldLabel}>
              <label htmlFor="wbc">WBC (10^9/L)</label>
            </div>
            <div className={styles.testFieldInputs}>
              <div className={styles.testFieldValue}>
                <input
                  type="number"
                  id="wbc"
                  name="wbc"
                  value={formData.wbc || ''}
                  onChange={handleInputChange}
                  step="0.1"
                  required
                  placeholder={`${formData.wbcMin || '4.5'} - ${formData.wbcMax || '11.0'}`}
                />
                {formErrors.wbc && (
                  <div className={styles.fieldError}>{formErrors.wbc}</div>
                )}
              </div>
              <div className={styles.testFieldRange}>
                <input
                  type="number"
                  id="wbcMin"
                  name="wbcMin"
                  placeholder="Min"
                  value={formData.wbcMin || ''}
                  onChange={handleInputChange}
                  step="0.1"
                />
                <span>-</span>
                <input
                  type="number"
                  id="wbcMax"
                  name="wbcMax"
                  placeholder="Max"
                  value={formData.wbcMax || ''}
                  onChange={handleInputChange}
                  step="0.1"
                />
              </div>
            </div>
          </div>
          
          {/* Platelets */}
          <div className={styles.testFieldGroup}>
            <div className={styles.testFieldLabel}>
              <label htmlFor="platelets">Platelets (10^9/L)</label>
            </div>
            <div className={styles.testFieldInputs}>
              <div className={styles.testFieldValue}>
                <input
                  type="number"
                  id="platelets"
                  name="platelets"
                  value={formData.platelets || ''}
                  onChange={handleInputChange}
                  required
                  placeholder={`${formData.plateletsMin || '150'} - ${formData.plateletsMax || '450'}`}
                />
                {formErrors.platelets && (
                  <div className={styles.fieldError}>{formErrors.platelets}</div>
                )}
              </div>
              <div className={styles.testFieldRange}>
                <input
                  type="number"
                  id="plateletsMin"
                  name="plateletsMin"
                  placeholder="Min"
                  value={formData.plateletsMin || ''}
                  onChange={handleInputChange}
                />
                <span>-</span>
                <input
                  type="number"
                  id="plateletsMax"
                  name="plateletsMax"
                  placeholder="Max"
                  value={formData.plateletsMax || ''}
                  onChange={handleInputChange}
                />
              </div>
            </div>
          </div>
          
          {/* Neutrophils */}
          <div className={styles.testFieldGroup}>
            <div className={styles.testFieldLabel}>
              <label htmlFor="neutrophils">Neutrophils (10^9/L)</label>
            </div>
            <div className={styles.testFieldInputs}>
              <div className={styles.testFieldValue}>
                <input
                  type="number"
                  id="neutrophils"
                  name="neutrophils"
                  value={formData.neutrophils || ''}
                  onChange={handleInputChange}
                  step="0.1"
                  required
                  placeholder={`${formData.neutrophilsMin || '2.0'} - ${formData.neutrophilsMax || '7.5'}`}
                />
                {formErrors.neutrophils && (
                  <div className={styles.fieldError}>{formErrors.neutrophils}</div>
                )}
              </div>
              <div className={styles.testFieldRange}>
                <input
                  type="number"
                  id="neutrophilsMin"
                  name="neutrophilsMin"
                  placeholder="Min"
                  value={formData.neutrophilsMin || ''}
                  onChange={handleInputChange}
                  step="0.1"
                />
                <span>-</span>
                <input
                  type="number"
                  id="neutrophilsMax"
                  name="neutrophilsMax"
                  placeholder="Max"
                  value={formData.neutrophilsMax || ''}
                  onChange={handleInputChange}
                  step="0.1"
                />
              </div>
            </div>
          </div>
          
          {/* Lymphocytes */}
          <div className={styles.testFieldGroup}>
            <div className={styles.testFieldLabel}>
              <label htmlFor="lymphocytes">Lymphocytes (10^9/L)</label>
            </div>
            <div className={styles.testFieldInputs}>
              <div className={styles.testFieldValue}>
                <input
                  type="number"
                  id="lymphocytes"
                  name="lymphocytes"
                  value={formData.lymphocytes || ''}
                  onChange={handleInputChange}
                  step="0.1"
                  required
                  placeholder={`${formData.lymphocytesMin || '1.0'} - ${formData.lymphocytesMax || '4.5'}`}
                />
                {formErrors.lymphocytes && (
                  <div className={styles.fieldError}>{formErrors.lymphocytes}</div>
                )}
              </div>
              <div className={styles.testFieldRange}>
                <input
                  type="number"
                  id="lymphocytesMin"
                  name="lymphocytesMin"
                  placeholder="Min"
                  value={formData.lymphocytesMin || ''}
                  onChange={handleInputChange}
                  step="0.1"
                />
                <span>-</span>
                <input
                  type="number"
                  id="lymphocytesMax"
                  name="lymphocytesMax"
                  placeholder="Max"
                  value={formData.lymphocytesMax || ''}
                  onChange={handleInputChange}
                  step="0.1"
                />
              </div>
            </div>
          </div>
          
          {/* RBC */}
          <div className={styles.testFieldGroup}>
            <div className={styles.testFieldLabel}>
              <label htmlFor="rbc">RBC (10^12/L)</label>
            </div>
            <div className={styles.testFieldInputs}>
              <div className={styles.testFieldValue}>
                <input
                  type="number"
                  id="rbc"
                  name="rbc"
                  value={formData.rbc || ''}
                  onChange={handleInputChange}
                  step="0.1"
                  required
                  placeholder={`${formData.rbcMin || '4.0'} - ${formData.rbcMax || '5.5'}`}
                />
                {formErrors.rbc && (
                  <div className={styles.fieldError}>{formErrors.rbc}</div>
                )}
              </div>
              <div className={styles.testFieldRange}>
                <input
                  type="number"
                  id="rbcMin"
                  name="rbcMin"
                  placeholder="Min"
                  value={formData.rbcMin || ''}
                  onChange={handleInputChange}
                  step="0.1"
                />
                <span>-</span>
                <input
                  type="number"
                  id="rbcMax"
                  name="rbcMax"
                  placeholder="Max"
                  value={formData.rbcMax || ''}
                  onChange={handleInputChange}
                  step="0.1"
                />
              </div>
            </div>
          </div>
          
          {/* MCV */}
          <div className={styles.testFieldGroup}>
            <div className={styles.testFieldLabel}>
              <label htmlFor="mcv">MCV (fL)</label>
            </div>
            <div className={styles.testFieldInputs}>
              <div className={styles.testFieldValue}>
                <input
                  type="number"
                  id="mcv"
                  name="mcv"
                  value={formData.mcv || ''}
                  onChange={handleInputChange}
                  required
                  placeholder={`${formData.mcvMin || '80'} - ${formData.mcvMax || '100'}`}
                />
                {formErrors.mcv && (
                  <div className={styles.fieldError}>{formErrors.mcv}</div>
                )}
              </div>
              <div className={styles.testFieldRange}>
                <input
                  type="number"
                  id="mcvMin"
                  name="mcvMin"
                  placeholder="Min"
                  value={formData.mcvMin || ''}
                  onChange={handleInputChange}
                />
                <span>-</span>
                <input
                  type="number"
                  id="mcvMax"
                  name="mcvMax"
                  placeholder="Max"
                  value={formData.mcvMax || ''}
                  onChange={handleInputChange}
                />
              </div>
            </div>
          </div>
          
          {/* MCH */}
          <div className={styles.testFieldGroup}>
            <div className={styles.testFieldLabel}>
              <label htmlFor="mch">MCH (pg)</label>
            </div>
            <div className={styles.testFieldInputs}>
              <div className={styles.testFieldValue}>
                <input
                  type="number"
                  id="mch"
                  name="mch"
                  value={formData.mch || ''}
                  onChange={handleInputChange}
                  required
                  placeholder={`${formData.mchMin || '27'} - ${formData.mchMax || '33'}`}
                />
                {formErrors.mch && (
                  <div className={styles.fieldError}>{formErrors.mch}</div>
                )}
              </div>
              <div className={styles.testFieldRange}>
                <input
                  type="number"
                  id="mchMin"
                  name="mchMin"
                  placeholder="Min"
                  value={formData.mchMin || ''}
                  onChange={handleInputChange}
                />
                <span>-</span>
                <input
                  type="number"
                  id="mchMax"
                  name="mchMax"
                  placeholder="Max"
                  value={formData.mchMax || ''}
                  onChange={handleInputChange}
                />
              </div>
            </div>
          </div>
        </div>
        
        <div className={styles.formActions}>
          <div className={styles.demoButtons}>
            <button
              type="button"
              className={styles.secondaryButton}
              onClick={handleLoadNormalData}
            >
              Load Normal Demo
            </button>
            <button
              type="button"
              className={styles.secondaryButton}
              onClick={handleLoadAbnormalData}
            >
              Load Abnormal Demo
            </button>
          </div>
          <div>
            <button
              type="button"
              className={styles.secondaryButton}
              onClick={handleResetForm}
            >
              Reset
            </button>
            <button
              type="submit"
              className={styles.primaryButton}
              disabled={!isFormValid || isLoading}
            >
              {isLoading ? 'Processing...' : 'Submit Results'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}