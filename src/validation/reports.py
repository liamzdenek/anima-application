"""
Report generation module for the Active Patient Follow-Up Alert Dashboard.

This module handles generating comprehensive validation reports for model
validation results.
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix


def generate_validation_report(
    validation_results: Dict[str, Any],
    reports_dir: str = './reports',
    format: str = 'markdown'
) -> str:
    """
    Generate a comprehensive validation report.
    
    Args:
        validation_results: Dictionary with validation results
        reports_dir: Directory to save the report
        format: Report format ('markdown' or 'html')
        
    Returns:
        Path to the generated report
    """
    print("Generating validation report...")
    
    # Create reports directory if it doesn't exist
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(os.path.join(reports_dir, 'clinical'), exist_ok=True)
    
    # Get model info
    model_info = validation_results.get('model_info', {})
    model_name = model_info.get('name', 'unknown')
    model_version = model_info.get('version', 'unknown')
    
    # Create timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create report filename
    report_filename = f"validation_report_{model_version}_{timestamp}.md"
    report_path = os.path.join(reports_dir, 'clinical', report_filename)
    
    # Generate report content
    report_content = []
    
    # Add header
    report_content.append(f"# Model Validation Report: {model_name}")
    report_content.append(f"**Version:** {model_version}")
    report_content.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_content.append(f"**Validation Status:** {'PASSED' if validation_results.get('validation_passed', False) else 'FAILED'}")
    report_content.append("")
    
    # Add summary
    report_content.append("## Summary")
    report_content.append("")
    report_content.append("| Validation Check | Status | Details |")
    report_content.append("| --- | --- | --- |")
    
    # Overfitting
    overfitting = validation_results.get('overfitting', {})
    is_overfit = overfitting.get('is_overfit', True)
    report_content.append(f"| Overfitting | {'❌ FAILED' if is_overfit else '✅ PASSED'} | Severity: {overfitting.get('severity', 0):.4f} |")
    
    # Learning curve
    learning_curve = validation_results.get('learning_curve', {})
    learning_analysis = learning_curve.get('analysis', {})
    needs_more_data = learning_analysis.get('needs_more_data', False)
    still_learning = learning_analysis.get('still_learning', False)
    converged = learning_analysis.get('converged', False)
    report_content.append(f"| Learning Curve | {'⚠️ WARNING' if needs_more_data or still_learning else '✅ PASSED'} | Needs more data: {needs_more_data}, Still learning: {still_learning}, Converged: {converged} |")
    
    # Feature importance stability
    stability = validation_results.get('feature_importance_stability', {})
    is_stable = stability.get('stability', {}).get('is_stable', False)
    report_content.append(f"| Feature Stability | {'❌ FAILED' if not is_stable else '✅ PASSED'} | CV: {stability.get('stability', {}).get('average_cv', 0):.4f} |")
    
    # Temporal validation
    temporal = validation_results.get('temporal_validation', {})
    is_temporally_valid = temporal.get('is_temporally_valid', False)
    report_content.append(f"| Temporal Validation | {'❌ FAILED' if not is_temporally_valid else '✅ PASSED'} | Recall: {temporal.get('metrics', {}).get('recall', 0):.4f} |")
    
    # Clinical safety
    clinical = validation_results.get('clinical_safety', {})
    is_clinically_safe = clinical.get('is_clinically_safe', False)
    report_content.append(f"| Clinical Safety | {'❌ FAILED' if not is_clinically_safe else '✅ PASSED'} | Sensitivity: {clinical.get('optimal_sensitivity', 0):.4f}, NPV: {clinical.get('optimal_npv', 0):.4f} |")
    
    # Fairness
    fairness = validation_results.get('fairness', {})
    is_fair = fairness.get('is_fair', False)
    report_content.append(f"| Fairness | {'❌ FAILED' if not is_fair else '✅ PASSED'} | Age parity diff: {fairness.get('demographic_parity', {}).get('age_group', {}).get('max_difference', 0):.4f}, Gender parity diff: {fairness.get('demographic_parity', {}).get('gender', {}).get('max_difference', 0):.4f} |")
    
    report_content.append("")
    
    # Add detailed sections
    
    # Overfitting
    report_content.append("## Overfitting Analysis")
    report_content.append("")
    report_content.append("Comparison of training and test performance:")
    report_content.append("")
    report_content.append("| Metric | Training | Test | Difference |")
    report_content.append("| --- | --- | --- | --- |")
    
    train_metrics = overfitting.get('train_metrics', {})
    test_metrics = overfitting.get('test_metrics', {})
    metric_diffs = overfitting.get('metric_differences', {})
    
    for metric in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']:
        train_val = train_metrics.get(metric, 0)
        test_val = test_metrics.get(metric, 0)
        diff_val = metric_diffs.get(metric, 0)
        report_content.append(f"| {metric.upper()} | {train_val:.4f} | {test_val:.4f} | {diff_val:.4f} |")
    
    report_content.append("")
    report_content.append(f"**Overfitting detected:** {is_overfit}")
    report_content.append(f"**Severity:** {overfitting.get('severity', 0):.4f}")
    report_content.append("")
    
    # Learning curve
    report_content.append("## Learning Curve Analysis")
    report_content.append("")
    report_content.append("Analysis of model performance with increasing training data:")
    report_content.append("")
    report_content.append(f"**Needs more data:** {needs_more_data}")
    report_content.append(f"**Still learning:** {still_learning}")
    report_content.append(f"**Converged:** {converged}")
    report_content.append("")
    
    # Feature importance stability
    report_content.append("## Feature Importance Stability")
    report_content.append("")
    
    if stability.get('has_feature_importances', False):
        report_content.append("Top 10 features by importance:")
        report_content.append("")
        report_content.append("| Feature | Mean Importance | Std Dev | CV |")
        report_content.append("| --- | --- | --- | --- |")
        
        feature_importances = stability.get('feature_importances', [])
        for feature in feature_importances[:10]:
            report_content.append(f"| {feature['feature']} | {feature['mean_importance']:.4f} | {feature['std_importance']:.4f} | {feature['cv']:.4f} |")
        
        report_content.append("")
        report_content.append(f"**Stability:** {'Stable' if is_stable else 'Unstable'}")
        report_content.append(f"**Average CV:** {stability.get('stability', {}).get('average_cv', 0):.4f}")
    else:
        report_content.append("Feature importances not available for this model.")
    
    report_content.append("")
    
    # Temporal validation
    report_content.append("## Temporal Validation")
    report_content.append("")
    report_content.append("Performance when training on older data and testing on newer data:")
    report_content.append("")
    report_content.append("| Metric | Value |")
    report_content.append("| --- | --- |")
    
    temporal_metrics = temporal.get('metrics', {})
    for metric, value in temporal_metrics.items():
        report_content.append(f"| {metric.upper()} | {value:.4f} |")
    
    report_content.append("")
    report_content.append(f"**Early data size:** {temporal.get('early_data_size', 0)}")
    report_content.append(f"**Late data size:** {temporal.get('late_data_size', 0)}")
    report_content.append(f"**Temporally valid:** {is_temporally_valid}")
    report_content.append("")
    
    # Clinical safety
    report_content.append("## Clinical Safety Metrics")
    report_content.append("")
    report_content.append("Performance at optimal clinical threshold:")
    report_content.append("")
    report_content.append("| Metric | Value |")
    report_content.append("| --- | --- |")
    report_content.append(f"| Optimal Threshold | {clinical.get('optimal_threshold', 0.5):.4f} |")
    report_content.append(f"| Sensitivity | {clinical.get('optimal_sensitivity', 0):.4f} |")
    report_content.append(f"| Specificity | {clinical.get('optimal_specificity', 0):.4f} |")
    report_content.append(f"| PPV | {clinical.get('optimal_ppv', 0):.4f} |")
    report_content.append(f"| NPV | {clinical.get('optimal_npv', 0):.4f} |")
    report_content.append("")
    
    report_content.append("False negative analysis:")
    report_content.append("")
    report_content.append(f"**False negative count:** {clinical.get('false_negative_count', 0)}")
    report_content.append(f"**False negative rate:** {clinical.get('false_negative_rate', 0):.4f}")
    report_content.append(f"**Average false negative probability:** {clinical.get('avg_false_negative_prob', 0):.4f}")
    report_content.append(f"**Threshold distance:** {clinical.get('threshold_distance', 0):.4f}")
    report_content.append("")
    report_content.append(f"**Clinically safe:** {is_clinically_safe}")
    report_content.append("")
    
    # Fairness
    report_content.append("## Fairness Analysis")
    report_content.append("")
    report_content.append("### Demographic Parity")
    report_content.append("")
    report_content.append("Positive prediction rates across demographic groups:")
    report_content.append("")
    
    # Age groups
    report_content.append("#### Age Groups")
    report_content.append("")
    report_content.append("| Age Group | Count | Positive Rate | True Positive Rate | False Positive Rate |")
    report_content.append("| --- | --- | --- | --- | --- |")
    
    age_metrics = fairness.get('demographic_metrics', {}).get('age_group', {})
    for group, metrics in age_metrics.items():
        report_content.append(f"| {group} | {metrics.get('count', 0)} | {metrics.get('positive_rate', 0):.4f} | {metrics.get('true_positive_rate', 0):.4f} | {metrics.get('false_positive_rate', 0):.4f} |")
    
    report_content.append("")
    report_content.append(f"**Maximum difference:** {fairness.get('demographic_parity', {}).get('age_group', {}).get('max_difference', 0):.4f}")
    report_content.append(f"**Fair:** {fairness.get('demographic_parity', {}).get('age_group', {}).get('is_fair', False)}")
    report_content.append("")
    
    # Gender groups
    report_content.append("#### Gender Groups")
    report_content.append("")
    report_content.append("| Gender | Count | Positive Rate | True Positive Rate | False Positive Rate |")
    report_content.append("| --- | --- | --- | --- | --- |")
    
    gender_metrics = fairness.get('demographic_metrics', {}).get('gender', {})
    for group, metrics in gender_metrics.items():
        report_content.append(f"| {group} | {metrics.get('count', 0)} | {metrics.get('positive_rate', 0):.4f} | {metrics.get('true_positive_rate', 0):.4f} | {metrics.get('false_positive_rate', 0):.4f} |")
    
    report_content.append("")
    report_content.append(f"**Maximum difference:** {fairness.get('demographic_parity', {}).get('gender', {}).get('max_difference', 0):.4f}")
    report_content.append(f"**Fair:** {fairness.get('demographic_parity', {}).get('gender', {}).get('is_fair', False)}")
    report_content.append("")
    
    # Equal opportunity
    report_content.append("### Equal Opportunity")
    report_content.append("")
    report_content.append("True positive rates across demographic groups:")
    report_content.append("")
    report_content.append(f"**Age group maximum difference:** {fairness.get('equal_opportunity', {}).get('age_group', {}).get('max_difference', 0):.4f}")
    report_content.append(f"**Gender maximum difference:** {fairness.get('equal_opportunity', {}).get('gender', {}).get('max_difference', 0):.4f}")
    report_content.append("")
    report_content.append(f"**Overall fairness:** {is_fair}")
    report_content.append("")
    
    # Conclusion
    report_content.append("## Conclusion")
    report_content.append("")
    
    if validation_results.get('validation_passed', False):
        report_content.append("✅ **The model has passed all validation checks and is ready for deployment.**")
        report_content.append("")
        report_content.append("The model demonstrates:")
        report_content.append("- Good generalization (no overfitting)")
        report_content.append("- Temporal stability")
        report_content.append("- Clinical safety with high sensitivity")
        report_content.append("- Fairness across demographic groups")
    else:
        report_content.append("❌ **The model has failed one or more validation checks and requires further improvement.**")
        report_content.append("")
        report_content.append("Issues to address:")
        
        if is_overfit:
            report_content.append("- Overfitting: The model performs significantly better on training data than test data")
        
        if not is_temporally_valid:
            report_content.append("- Temporal instability: The model does not maintain performance on newer data")
        
        if not is_clinically_safe:
            report_content.append("- Clinical safety: The model does not meet the required sensitivity threshold")
        
        if not is_fair:
            report_content.append("- Fairness: The model shows significant disparities across demographic groups")
    
    # Write report to file
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_content))
    
    print(f"Validation report saved to {report_path}")
    
    return report_path


def generate_model_card(
    validation_results: Dict[str, Any],
    reports_dir: str = './reports'
) -> str:
    """
    Generate a model card for the validated model.
    
    Args:
        validation_results: Dictionary with validation results
        reports_dir: Directory to save the model card
        
    Returns:
        Path to the generated model card
    """
    print("Generating model card...")
    
    # Create reports directory if it doesn't exist
    os.makedirs(reports_dir, exist_ok=True)
    
    # Get model info
    model_info = validation_results.get('model_info', {})
    model_name = model_info.get('name', 'unknown')
    model_version = model_info.get('version', 'unknown')
    
    # Create model card filename
    card_filename = f"model_card_{model_version}.md"
    card_path = os.path.join(reports_dir, card_filename)
    
    # Generate model card content
    card_content = []
    
    # Add header
    card_content.append(f"# Model Card: {model_name}")
    card_content.append(f"**Version:** {model_version}")
    card_content.append(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}")
    card_content.append("")
    
    # Add model details
    card_content.append("## Model Details")
    card_content.append("")
    card_content.append(f"- **Name:** {model_name}")
    card_content.append(f"- **Version:** {model_version}")
    card_content.append(f"- **Type:** Binary classification")
    card_content.append(f"- **Task:** Abnormal blood test detection")
    card_content.append(f"- **Created:** {model_info.get('created_at', 'unknown')}")
    card_content.append("")
    
    # Add intended use
    card_content.append("## Intended Use")
    card_content.append("")
    card_content.append("This model is designed to identify patients with abnormal blood test results that require clinical follow-up. It is intended to be used as a decision support tool for healthcare providers, not as a replacement for clinical judgment.")
    card_content.append("")
    card_content.append("### Primary intended uses:")
    card_content.append("- Screening patients for potential abnormalities in blood test results")
    card_content.append("- Prioritizing patients for clinical follow-up")
    card_content.append("- Supporting clinical decision-making")
    card_content.append("")
    card_content.append("### Out-of-scope uses:")
    card_content.append("- Automated clinical decisions without human review")
    card_content.append("- Diagnosis of specific medical conditions")
    card_content.append("- Replacement for comprehensive clinical assessment")
    card_content.append("")
    
    # Add training data
    card_content.append("## Training Data")
    card_content.append("")
    card_content.append("The model was trained on synthetic blood test data that simulates realistic patterns of normal and abnormal results. The data includes:")
    card_content.append("")
    card_content.append("- Complete Blood Count (CBC) metrics")
    card_content.append("- Patient demographics (age, gender)")
    card_content.append("- Reference ranges for each test metric")
    card_content.append("- Binary labels (NORMAL/ABNORMAL)")
    card_content.append("")
    
    # Add performance metrics
    card_content.append("## Performance Metrics")
    card_content.append("")
    
    # Get clinical metrics
    clinical = validation_results.get('clinical_safety', {})
    
    card_content.append("### Overall Performance")
    card_content.append("")
    card_content.append("| Metric | Value |")
    card_content.append("| --- | --- |")
    card_content.append(f"| Accuracy | {clinical.get('accuracy', 0):.4f} |")
    card_content.append(f"| ROC AUC | {clinical.get('roc_auc', 0):.4f} |")
    card_content.append(f"| F1 Score | {clinical.get('f1', 0):.4f} |")
    card_content.append("")
    
    card_content.append("### Clinical Performance")
    card_content.append("")
    card_content.append("| Metric | Value |")
    card_content.append("| --- | --- |")
    card_content.append(f"| Sensitivity | {clinical.get('optimal_sensitivity', 0):.4f} |")
    card_content.append(f"| Specificity | {clinical.get('optimal_specificity', 0):.4f} |")
    card_content.append(f"| PPV | {clinical.get('optimal_ppv', 0):.4f} |")
    card_content.append(f"| NPV | {clinical.get('optimal_npv', 0):.4f} |")
    card_content.append("")
    
    # Add fairness metrics
    fairness = validation_results.get('fairness', {})
    
    card_content.append("## Fairness Considerations")
    card_content.append("")
    card_content.append("The model has been evaluated for fairness across demographic groups:")
    card_content.append("")
    
    # Age groups
    age_parity = fairness.get('demographic_parity', {}).get('age_group', {})
    age_opportunity = fairness.get('equal_opportunity', {}).get('age_group', {})
    
    card_content.append("### Age Groups")
    card_content.append("")
    card_content.append(f"- **Demographic Parity Difference:** {age_parity.get('max_difference', 0):.4f}")
    card_content.append(f"- **Equal Opportunity Difference:** {age_opportunity.get('max_difference', 0):.4f}")
    card_content.append("")
    
    # Gender groups
    gender_parity = fairness.get('demographic_parity', {}).get('gender', {})
    gender_opportunity = fairness.get('equal_opportunity', {}).get('gender', {})
    
    card_content.append("### Gender Groups")
    card_content.append("")
    card_content.append(f"- **Demographic Parity Difference:** {gender_parity.get('max_difference', 0):.4f}")
    card_content.append(f"- **Equal Opportunity Difference:** {gender_opportunity.get('max_difference', 0):.4f}")
    card_content.append("")
    
    # Add limitations
    card_content.append("## Limitations")
    card_content.append("")
    card_content.append("- The model was trained on synthetic data and may not capture all real-world patterns")
    card_content.append("- Performance may vary for patient populations not well-represented in the training data")
    card_content.append("- The model does not account for patient history or medications that may affect test results")
    card_content.append("- The model is designed for general screening and may miss rare or complex abnormalities")
    card_content.append("")
    
    # Add ethical considerations
    card_content.append("## Ethical Considerations")
    card_content.append("")
    card_content.append("- **Human oversight:** This model is designed to support, not replace, clinical decision-making")
    card_content.append("- **False negatives:** The model is optimized to minimize false negatives (missed abnormalities) at the cost of more false positives")
    card_content.append("- **Transparency:** Feature importance and decision factors are available to explain model predictions")
    card_content.append("- **Feedback loop:** The system includes mechanisms for clinicians to provide feedback on model predictions")
    card_content.append("")
    
    # Add usage guidelines
    card_content.append("## Usage Guidelines")
    card_content.append("")
    card_content.append("1. **Review all predictions:** All model predictions should be reviewed by qualified healthcare providers")
    card_content.append("2. **Consider context:** Patient history, medications, and other factors not included in the model should be considered")
    card_content.append("3. **Monitor performance:** Regular audits of model performance should be conducted in the clinical setting")
    card_content.append("4. **Provide feedback:** Users should provide feedback on incorrect predictions to improve the model")
    card_content.append("")
    
    # Write model card to file
    with open(card_path, 'w') as f:
        f.write('\n'.join(card_content))
    
    print(f"Model card saved to {card_path}")
    
    return card_path


if __name__ == "__main__":
    # This module is not meant to be run directly
    print("This module provides report generation for model validation.")
    print("Please use validate.py to run the full validation and generate reports.")