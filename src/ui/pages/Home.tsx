/**
 * Home page component
 */
import React from 'react';
import { Link } from '@tanstack/react-router';
import styles from './Home.module.css';

export function HomePage() {
  return (
    <div className={styles.homePage}>
      <div className={styles.heroSection}>
        <h2>Active Patient Follow-Up Alert Dashboard</h2>
        <p>
          Enter blood test results to detect abnormalities and prioritize patient follow-ups.
        </p>
        <div className={styles.ctaButtons}>
          <Link to="/test-entry" className={styles.primaryButton}>
            Enter Test Results
          </Link>
        </div>
      </div>
      
      <div className={styles.infoSection}>
        <div className={styles.infoCard}>
          <h3>For Registered Nurses</h3>
          <p>
            This tool helps you quickly identify patients who may need follow-up
            based on their blood test results. The system uses machine learning
            to detect patterns that might indicate abnormalities.
          </p>
        </div>
        
        <div className={styles.infoCard}>
          <h3>How It Works</h3>
          <p>
            1. Enter the patient's blood test results<br />
            2. The system analyzes the results using a validated ML model<br />
            3. View the prediction and risk assessment<br />
            4. Use the information to prioritize patient follow-ups
          </p>
        </div>
        
        <div className={styles.infoCard}>
          <h3>Model Validation</h3>
          <p>
            Our model has been rigorously validated to ensure:
          </p>
          <ul>
            <li>High sensitivity (≥95%) for detecting abnormalities</li>
            <li>Strong overall performance (AUC-ROC ≥0.85)</li>
            <li>Fairness across demographic groups</li>
          </ul>
        </div>
      </div>
    </div>
  );
}