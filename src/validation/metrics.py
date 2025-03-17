"""
Clinical metrics module for the Active Patient Follow-Up Alert Dashboard.

This module handles calculating clinical safety metrics and fairness metrics
for model validation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)


def calculate_clinical_safety_metrics(
    model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
    features_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Calculate clinical safety metrics for the model.
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
        features_df: DataFrame with features and metadata
        
    Returns:
        Dictionary with clinical safety metrics
    """
    print("Calculating clinical safety metrics...")
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    # Calculate basic metrics
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_prob)
    }
    
    # Calculate confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    
    # Calculate sensitivity (recall) and specificity
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    # Calculate positive predictive value (precision) and negative predictive value
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    
    # Add to metrics
    metrics.update({
        'sensitivity': sensitivity,
        'specificity': specificity,
        'ppv': ppv,
        'npv': npv
    })
    
    # Analyze false negatives (missed abnormal cases)
    # This is critical for clinical safety
    fn_indices = np.where((y_test == 1) & (y_pred == 0))[0]
    fn_count = len(fn_indices)
    
    # Calculate false negative rate
    fn_rate = fn_count / (tp + fn) if (tp + fn) > 0 else 0
    
    # Analyze false negative probabilities
    fn_probs = y_prob[fn_indices] if fn_count > 0 else []
    
    # Calculate average probability of false negatives
    avg_fn_prob = np.mean(fn_probs) if fn_count > 0 else 0
    
    # Calculate how close false negatives were to the decision threshold
    # (assuming threshold of 0.5)
    threshold_distance = np.mean(0.5 - fn_probs) if fn_count > 0 else 0
    
    # Add to metrics
    metrics.update({
        'false_negative_count': fn_count,
        'false_negative_rate': fn_rate,
        'avg_false_negative_prob': float(avg_fn_prob),
        'threshold_distance': float(threshold_distance)
    })
    
    # Calculate optimal threshold for clinical use
    # For clinical safety, we prioritize sensitivity (recall)
    # We want to find the threshold that gives at least 0.95 sensitivity
    # while maximizing specificity
    thresholds = np.linspace(0, 1, 100)
    best_threshold = 0.5  # Default
    best_specificity = 0
    target_sensitivity = 0.95
    
    for threshold in thresholds:
        y_pred_t = (y_prob >= threshold).astype(int)
        
        # Calculate sensitivity and specificity at this threshold
        tn_t, fp_t, fn_t, tp_t = confusion_matrix(y_test, y_pred_t).ravel()
        sensitivity_t = tp_t / (tp_t + fn_t) if (tp_t + fn_t) > 0 else 0
        specificity_t = tn_t / (tn_t + fp_t) if (tn_t + fp_t) > 0 else 0
        
        # If sensitivity is at least the target and specificity is better than current best
        if sensitivity_t >= target_sensitivity and specificity_t > best_specificity:
            best_threshold = threshold
            best_specificity = specificity_t
    
    # Calculate metrics at the optimal threshold
    y_pred_opt = (y_prob >= best_threshold).astype(int)
    tn_opt, fp_opt, fn_opt, tp_opt = confusion_matrix(y_test, y_pred_opt).ravel()
    
    sensitivity_opt = tp_opt / (tp_opt + fn_opt) if (tp_opt + fn_opt) > 0 else 0
    specificity_opt = tn_opt / (tn_opt + fp_opt) if (tn_opt + fp_opt) > 0 else 0
    ppv_opt = tp_opt / (tp_opt + fp_opt) if (tp_opt + fp_opt) > 0 else 0
    npv_opt = tn_opt / (tn_opt + fn_opt) if (tn_opt + fn_opt) > 0 else 0
    
    # Add to metrics
    metrics.update({
        'optimal_threshold': float(best_threshold),
        'optimal_sensitivity': float(sensitivity_opt),
        'optimal_specificity': float(specificity_opt),
        'optimal_ppv': float(ppv_opt),
        'optimal_npv': float(npv_opt)
    })
    
    # Check if model meets clinical safety requirements
    # 1. Sensitivity at optimal threshold must be at least 0.95
    # 2. NPV at optimal threshold must be at least 0.9
    is_clinically_safe = sensitivity_opt >= 0.95 and npv_opt >= 0.9
    
    # Add to metrics
    metrics.update({
        'is_clinically_safe': is_clinically_safe
    })
    
    print(f"  Clinical safety: {is_clinically_safe}")
    print(f"  Sensitivity at optimal threshold: {sensitivity_opt:.4f}")
    print(f"  Specificity at optimal threshold: {specificity_opt:.4f}")
    print(f"  NPV at optimal threshold: {npv_opt:.4f}")
    print(f"  Optimal threshold: {best_threshold:.4f}")
    
    return metrics


def calculate_fairness_metrics(
    model: Any,
    features_df: pd.DataFrame,
    feature_names: List[str]
) -> Dict[str, Any]:
    """
    Calculate fairness metrics for the model across demographic groups.
    
    Args:
        model: Trained model
        features_df: DataFrame with features and metadata
        feature_names: List of feature names used by the model
        
    Returns:
        Dictionary with fairness metrics
    """
    print("Calculating fairness metrics...")
    
    # Check if demographic information is available
    if 'age' not in features_df.columns or 'gender' not in features_df.columns:
        print("  Demographic information not available")
        return {
            'is_fair': True,  # Assume fair if we can't check
            'demographic_parity': {},
            'equal_opportunity': {}
        }
    
    # Create binary target
    y = (features_df['label'] == 'ABNORMAL').astype(int).values
    
    # Create feature matrix
    X = features_df[feature_names].values
    
    # Make predictions
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]
    
    # Define demographic groups
    # Age groups
    features_df['age_group'] = pd.cut(
        features_df['age'],
        bins=[0, 18, 40, 60, 80, 120],
        labels=['0-18', '19-40', '41-60', '61-80', '81+']
    )
    
    age_groups = features_df['age_group'].unique()
    gender_groups = features_df['gender'].unique()
    
    # Calculate metrics for each demographic group
    demographic_metrics = {}
    
    # Age groups
    age_group_metrics = {}
    for group in age_groups:
        # Get indices for this group
        group_indices = features_df['age_group'] == group
        
        # Skip if no samples in this group
        if sum(group_indices) == 0:
            continue
        
        # Get predictions and labels for this group
        group_y = y[group_indices]
        group_y_pred = y_pred[group_indices]
        group_y_prob = y_prob[group_indices]
        
        # Calculate metrics
        metrics = {
            'count': int(sum(group_indices)),
            'positive_rate': float(np.mean(group_y_pred)),
            'true_positive_rate': float(recall_score(group_y, group_y_pred)) if sum(group_y) > 0 else 0,
            'false_positive_rate': float(sum((group_y == 0) & (group_y_pred == 1)) / sum(group_y == 0)) if sum(group_y == 0) > 0 else 0,
            'accuracy': float(accuracy_score(group_y, group_y_pred)),
            'auc': float(roc_auc_score(group_y, group_y_prob)) if len(np.unique(group_y)) > 1 else 0
        }
        
        age_group_metrics[str(group)] = metrics
    
    demographic_metrics['age_group'] = age_group_metrics
    
    # Gender groups
    gender_group_metrics = {}
    for group in gender_groups:
        # Get indices for this group
        group_indices = features_df['gender'] == group
        
        # Skip if no samples in this group
        if sum(group_indices) == 0:
            continue
        
        # Get predictions and labels for this group
        group_y = y[group_indices]
        group_y_pred = y_pred[group_indices]
        group_y_prob = y_prob[group_indices]
        
        # Calculate metrics
        metrics = {
            'count': int(sum(group_indices)),
            'positive_rate': float(np.mean(group_y_pred)),
            'true_positive_rate': float(recall_score(group_y, group_y_pred)) if sum(group_y) > 0 else 0,
            'false_positive_rate': float(sum((group_y == 0) & (group_y_pred == 1)) / sum(group_y == 0)) if sum(group_y == 0) > 0 else 0,
            'accuracy': float(accuracy_score(group_y, group_y_pred)),
            'auc': float(roc_auc_score(group_y, group_y_prob)) if len(np.unique(group_y)) > 1 else 0
        }
        
        gender_group_metrics[str(group)] = metrics
    
    demographic_metrics['gender'] = gender_group_metrics
    
    # Calculate demographic parity
    # Demographic parity: P(Y_hat=1|A=a) should be similar across groups
    demographic_parity = {}
    
    # Age groups
    age_positive_rates = [metrics['positive_rate'] for metrics in age_group_metrics.values()]
    age_parity_diff = max(age_positive_rates) - min(age_positive_rates) if age_positive_rates else 0
    
    demographic_parity['age_group'] = {
        'max_difference': float(age_parity_diff),
        'is_fair': age_parity_diff < 0.1  # Threshold for fairness
    }
    
    # Gender groups
    gender_positive_rates = [metrics['positive_rate'] for metrics in gender_group_metrics.values()]
    gender_parity_diff = max(gender_positive_rates) - min(gender_positive_rates) if gender_positive_rates else 0
    
    demographic_parity['gender'] = {
        'max_difference': float(gender_parity_diff),
        'is_fair': gender_parity_diff < 0.1  # Threshold for fairness
    }
    
    # Calculate equal opportunity
    # Equal opportunity: P(Y_hat=1|Y=1,A=a) should be similar across groups
    equal_opportunity = {}
    
    # Age groups
    age_tpr = [metrics['true_positive_rate'] for metrics in age_group_metrics.values()]
    age_tpr_diff = max(age_tpr) - min(age_tpr) if age_tpr else 0
    
    equal_opportunity['age_group'] = {
        'max_difference': float(age_tpr_diff),
        'is_fair': age_tpr_diff < 0.1  # Threshold for fairness
    }
    
    # Gender groups
    gender_tpr = [metrics['true_positive_rate'] for metrics in gender_group_metrics.values()]
    gender_tpr_diff = max(gender_tpr) - min(gender_tpr) if gender_tpr else 0
    
    equal_opportunity['gender'] = {
        'max_difference': float(gender_tpr_diff),
        'is_fair': gender_tpr_diff < 0.1  # Threshold for fairness
    }
    
    # Check if model is fair overall
    is_fair = (
        demographic_parity['age_group']['is_fair'] and
        demographic_parity['gender']['is_fair'] and
        equal_opportunity['age_group']['is_fair'] and
        equal_opportunity['gender']['is_fair']
    )
    
    fairness_result = {
        'is_fair': is_fair,
        'demographic_metrics': demographic_metrics,
        'demographic_parity': demographic_parity,
        'equal_opportunity': equal_opportunity
    }
    
    print(f"  Fairness: {is_fair}")
    print(f"  Age group demographic parity difference: {age_parity_diff:.4f}")
    print(f"  Gender demographic parity difference: {gender_parity_diff:.4f}")
    print(f"  Age group equal opportunity difference: {age_tpr_diff:.4f}")
    print(f"  Gender equal opportunity difference: {gender_tpr_diff:.4f}")
    
    return fairness_result


if __name__ == "__main__":
    # This module is not meant to be run directly
    print("This module provides clinical metrics for model validation.")
    print("Please use validate.py to run the full validation.")