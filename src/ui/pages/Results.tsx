/**
 * Results page component
 */
import React, { useEffect } from 'react';
import { Link } from '@tanstack/react-router';
import { useStore } from 'effector-react';
import { FaThumbsUp, FaThumbsDown } from 'react-icons/fa';
import {
  $predictionResults,
  $isLoading,
  $error,
  $topContributors,
  $validationMetrics,
  getModelInfoFx,
  validationThresholds,
  isMetricValid
} from '../stores/results';
import styles from './Results.module.css';

export function ResultsPage() {
  const results = useStore($predictionResults);
  const isLoading = useStore($isLoading);
  const error = useStore($error);
  const topContributors = useStore($topContributors);
  const validationMetrics = useStore($validationMetrics);
  
  // Fetch model info on component mount
  useEffect(() => {
    getModelInfoFx();
  }, []);
  
  // Empty handlers for thumbs up/down buttons
  const handleThumbsUp = () => {
    // No operation for now
    console.log('Thumbs up clicked');
  };
  
  const handleThumbsDown = () => {
    // No operation for now
    console.log('Thumbs down clicked');
  };
  
  if (isLoading) {
    return (
      <div className={`${styles.resultsPage} ${styles.loading}`}>
        <div className={styles.loadingSpinner}></div>
        <p>Loading results...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className={`${styles.resultsPage} ${styles.error}`}>
        <h2>Error</h2>
        <p className={styles.errorMessage}>{error}</p>
        <Link to="/test-entry" className={styles.primaryButton}>
          Back to Test Entry
        </Link>
      </div>
    );
  }
  
  if (!results) {
    return (
      <div className={`${styles.resultsPage} ${styles.noResults}`}>
        <h2>No Results Available</h2>
        <p>Please submit a test to see results.</p>
        <Link to="/test-entry" className={styles.primaryButton}>
          Go to Test Entry
        </Link>
      </div>
    );
  }
  
  return (
    <div className={styles.resultsPage}>
      <h2>Test Results Analysis</h2>
      
      <div className={styles.resultsContainer}>
        <div className={styles.resultsSummary}>
          <div className={`${styles.predictionCard} ${results.prediction === 'ABNORMAL' ? styles.abnormal : styles.normal}`}>
            <h3>Overall Prediction</h3>
            <div className={styles.predictionValue}>{results.prediction}</div>
            <div className={styles.predictionDetails}>
              <div className={styles.detailItem}>
                <span className={styles.detailLabel}>Probability:</span>
                <span className={styles.detailValue}>{(results.probability * 100).toFixed(1)}%</span>
              </div>
              <div className={styles.detailItem}>
                <span className={styles.detailLabel}>Confidence:</span>
                <span className={styles.detailValue}>{(results.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className={styles.detailItem}>
                <span className={styles.detailLabel}>Risk Score:</span>
                <span className={styles.detailValue}>{results.risk_score}/10</span>
              </div>
            </div>
          </div>
          
          <div className={styles.patientInfo}>
            <h3>Patient Information</h3>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Patient ID:</span>
              <span className={styles.infoValue}>{results.patientId}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Test Date:</span>
              <span className={styles.infoValue}>
                {new Date(results.timestamp).toLocaleDateString()}
              </span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Model Version:</span>
              <span className={styles.infoValue}>{results.model_version}</span>
            </div>
          </div>
        </div>
        
        <div className={styles.resultsDetails}>
          <div className={styles.contributorsSection}>
            <h3>Top Contributing Factors</h3>
            {topContributors.length === 0 ? (
              <p>No contributing factors available.</p>
            ) : (
              <table className={styles.contributorsTable}>
                <thead>
                  <tr>
                    <th>Feature</th>
                    <th>Value</th>
                    <th>Contribution</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {topContributors.map((contributor, index) => (
                    <tr key={index} className={contributor.isAbnormal ? styles.abnormal : styles.normal}>
                      <td>{contributor.feature}</td>
                      <td>{contributor.value.toFixed(2)}</td>
                      <td>{(contributor.contribution * 100).toFixed(1)}%</td>
                      <td>
                        <span className={`${styles.statusBadge} ${contributor.isAbnormal ? styles.abnormal : styles.normal}`}>
                          {contributor.isAbnormal ? 'Abnormal' : 'Normal'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
          
          <div className={styles.validationSection}>
            <h3>Model Validation Metrics</h3>
            {!validationMetrics ? (
              <p>Validation metrics not available.</p>
            ) : (
              <div className={styles.metricsGrid}>
                <div className={`${styles.metricCard} ${isMetricValid('accuracy', validationMetrics.accuracy) ? styles.valid : styles.invalid}`}>
                  <div className={styles.metricName}>Accuracy</div>
                  <div className={styles.metricValue}>{validationMetrics.accuracy.toFixed(2)}</div>
                  <div className={styles.metricThreshold}>
                    Threshold: {validationThresholds.accuracy}
                  </div>
                </div>
                
                <div className={`${styles.metricCard} ${isMetricValid('precision', validationMetrics.precision) ? styles.valid : styles.invalid}`}>
                  <div className={styles.metricName}>Precision</div>
                  <div className={styles.metricValue}>{validationMetrics.precision.toFixed(2)}</div>
                  <div className={styles.metricThreshold}>
                    Threshold: {validationThresholds.precision}
                  </div>
                </div>
                
                <div className={`${styles.metricCard} ${isMetricValid('recall', validationMetrics.recall) ? styles.valid : styles.invalid}`}>
                  <div className={styles.metricName}>Recall</div>
                  <div className={styles.metricValue}>{validationMetrics.recall.toFixed(2)}</div>
                  <div className={styles.metricThreshold}>
                    Threshold: {validationThresholds.recall}
                  </div>
                </div>
                
                <div className={`${styles.metricCard} ${isMetricValid('aucRoc', validationMetrics.aucRoc) ? styles.valid : styles.invalid}`}>
                  <div className={styles.metricName}>AUC-ROC</div>
                  <div className={styles.metricValue}>{validationMetrics.aucRoc.toFixed(2)}</div>
                  <div className={styles.metricThreshold}>
                    Threshold: {validationThresholds.aucRoc}
                  </div>
                </div>
                
                <div className={`${styles.metricCard} ${isMetricValid('f1Score', validationMetrics.f1Score) ? styles.valid : styles.invalid}`}>
                  <div className={styles.metricName}>F1 Score</div>
                  <div className={styles.metricValue}>{validationMetrics.f1Score.toFixed(2)}</div>
                  <div className={styles.metricThreshold}>
                    Threshold: {validationThresholds.f1Score}
                  </div>
                </div>
                
                <div className={`${styles.metricCard} ${isMetricValid('sensitivity', validationMetrics.sensitivity) ? styles.valid : styles.invalid}`}>
                  <div className={styles.metricName}>Sensitivity</div>
                  <div className={styles.metricValue}>{validationMetrics.sensitivity.toFixed(2)}</div>
                  <div className={styles.metricThreshold}>
                    Threshold: {validationThresholds.sensitivity}
                  </div>
                </div>
                
                <div className={`${styles.metricCard} ${isMetricValid('specificity', validationMetrics.specificity) ? styles.valid : styles.invalid}`}>
                  <div className={styles.metricName}>Specificity</div>
                  <div className={styles.metricValue}>{validationMetrics.specificity.toFixed(2)}</div>
                  <div className={styles.metricThreshold}>
                    Threshold: {validationThresholds.specificity}
                  </div>
                </div>
                
                <div className={`${styles.metricCard} ${isMetricValid('fairnessDelta', validationMetrics.fairnessDelta) ? styles.valid : styles.invalid}`}>
                  <div className={styles.metricName}>Fairness Δ</div>
                  <div className={styles.metricValue}>{validationMetrics.fairnessDelta.toFixed(2)}</div>
                  <div className={styles.metricThreshold}>
                    Threshold: &lt;{validationThresholds.fairnessDelta}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      <div className={styles.resultsActions}>
        <div className={styles.feedbackButtons}>
          <button
            onClick={handleThumbsUp}
            className={`${styles.feedbackButton} ${styles.thumbsUp}`}
            aria-label="Thumbs Up"
          >
            <FaThumbsUp /> Helpful
          </button>
          <button
            onClick={handleThumbsDown}
            className={`${styles.feedbackButton} ${styles.thumbsDown}`}
            aria-label="Thumbs Down"
          >
            <FaThumbsDown /> Not Helpful
          </button>
        </div>
        <Link to="/test-entry" className={styles.secondaryButton}>
          Enter New Test
        </Link>
      </div>
    </div>
  );
}