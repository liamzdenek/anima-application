"""
Model validation module for the Active Patient Follow-Up Alert Dashboard.

This module handles validating trained models to ensure they meet clinical
requirements and are not overfit.
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    precision_recall_curve, roc_curve
)
from sklearn.utils import resample

# Import local modules
from ..training.preprocess import prepare_data
from ..training.features import engineer_features
from .metrics import (
    calculate_clinical_safety_metrics,
    calculate_fairness_metrics
)


def load_model_and_metadata(model_dir: str = './model') -> Tuple[Any, Dict[str, Any]]:
    """
    Load the latest trained model and its metadata.
    
    Args:
        model_dir: Directory containing model files
        
    Returns:
        Tuple of (model, metadata)
    """
    # Read the current version
    version_path = os.path.join(model_dir, 'version.txt')
    if not os.path.exists(version_path):
        raise FileNotFoundError(f"Version file not found at {version_path}")
    
    with open(version_path, 'r') as f:
        model_version = f.read().strip()
    
    # Load the model
    model_path = os.path.join(model_dir, f"{model_version}.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    # Load the metadata
    info_path = os.path.join(model_dir, f"{model_version}_info.json")
    if not os.path.exists(info_path):
        raise FileNotFoundError(f"Model info file not found at {info_path}")
    
    with open(info_path, 'r') as f:
        metadata = json.load(f)
    
    print(f"Loaded model {model_version}")
    return model, metadata


def check_overfitting(
    model: Any,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray
) -> Dict[str, Any]:
    """
    Check for overfitting by comparing training and test performance.
    
    Args:
        model: Trained model
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        
    Returns:
        Dictionary with overfitting metrics
    """
    print("Checking for overfitting...")
    
    # Get predictions
    y_train_pred = model.predict(X_train)
    y_train_prob = model.predict_proba(X_train)[:, 1]
    
    y_test_pred = model.predict(X_test)
    y_test_prob = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    train_metrics = {
        'accuracy': accuracy_score(y_train, y_train_pred),
        'precision': precision_score(y_train, y_train_pred),
        'recall': recall_score(y_train, y_train_pred),
        'f1': f1_score(y_train, y_train_pred),
        'roc_auc': roc_auc_score(y_train, y_train_prob)
    }
    
    test_metrics = {
        'accuracy': accuracy_score(y_test, y_test_pred),
        'precision': precision_score(y_test, y_test_pred),
        'recall': recall_score(y_test, y_test_pred),
        'f1': f1_score(y_test, y_test_pred),
        'roc_auc': roc_auc_score(y_test, y_test_prob)
    }
    
    # Calculate differences
    metric_diffs = {
        key: train_metrics[key] - test_metrics[key]
        for key in train_metrics.keys()
    }
    
    # Check for significant overfitting
    # A difference > 0.15 in any metric suggests overfitting
    is_overfit = any(diff > 0.15 for diff in metric_diffs.values())
    
    # Calculate severity
    severity = sum(diff for diff in metric_diffs.values() if diff > 0) / len(metric_diffs)
    
    overfitting_result = {
        'is_overfit': is_overfit,
        'severity': severity,
        'train_metrics': train_metrics,
        'test_metrics': test_metrics,
        'metric_differences': metric_diffs
    }
    
    print(f"  Overfitting detected: {is_overfit}")
    print(f"  Severity: {severity:.4f}")
    print(f"  Metric differences: {metric_diffs}")
    
    return overfitting_result


def analyze_learning_curve(
    model: Any,
    X: np.ndarray,
    y: np.ndarray,
    cv: int = 5
) -> Dict[str, Any]:
    """
    Analyze learning curve to check for sample size sensitivity.
    
    Args:
        model: Trained model (clone will be used)
        X: Feature matrix
        y: Target vector
        cv: Number of cross-validation folds
        
    Returns:
        Dictionary with learning curve analysis
    """
    print("Analyzing learning curve...")
    
    # Define cross-validation strategy
    cv_strategy = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    
    # Calculate learning curve
    train_sizes = np.linspace(0.1, 1.0, 10)
    train_sizes, train_scores, test_scores = learning_curve(
        model, X, y, cv=cv_strategy, train_sizes=train_sizes,
        scoring='roc_auc', n_jobs=-1
    )
    
    # Calculate mean and std
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    test_std = np.std(test_scores, axis=1)
    
    # Check if model improves with more data
    # If test score at max samples is significantly better than at 50% samples,
    # then model would benefit from more data
    needs_more_data = (test_mean[-1] - test_mean[len(test_mean) // 2]) > 0.05
    
    # Check if model is still learning
    # If the slope of the last segment of the learning curve is still positive,
    # then model is still learning
    still_learning = (test_mean[-1] - test_mean[-2]) > 0.01
    
    # Check for convergence
    # If train and test scores are close at max samples, model has converged
    converged = abs(train_mean[-1] - test_mean[-1]) < 0.05
    
    learning_curve_result = {
        'train_sizes': train_sizes.tolist(),
        'train_mean': train_mean.tolist(),
        'train_std': train_std.tolist(),
        'test_mean': test_mean.tolist(),
        'test_std': test_std.tolist(),
        'analysis': {
            'needs_more_data': needs_more_data,
            'still_learning': still_learning,
            'converged': converged
        }
    }
    
    print(f"  Needs more data: {needs_more_data}")
    print(f"  Still learning: {still_learning}")
    print(f"  Converged: {converged}")
    
    return learning_curve_result


def analyze_feature_importance_stability(
    model: Any,
    X: np.ndarray,
    y: np.ndarray,
    feature_names: List[str],
    n_iterations: int = 100
) -> Dict[str, Any]:
    """
    Analyze feature importance stability using bootstrap resampling.
    
    Args:
        model: Trained model
        X: Feature matrix
        y: Target vector
        feature_names: List of feature names
        n_iterations: Number of bootstrap iterations
        
    Returns:
        Dictionary with feature importance stability analysis
    """
    print("Analyzing feature importance stability...")
    
    # Check if model has feature importances
    if not hasattr(model, 'feature_importances_') and not hasattr(model, 'coef_'):
        print("  Model does not have feature importances")
        return {
            'has_feature_importances': False
        }
    
    # Get feature importances
    if hasattr(model, 'feature_importances_'):
        get_importance = lambda m: m.feature_importances_
    else:
        get_importance = lambda m: m.coef_[0]
    
    # Initialize arrays to store bootstrap results
    n_features = len(feature_names)
    all_importances = np.zeros((n_iterations, n_features))
    
    # Perform bootstrap resampling
    for i in range(n_iterations):
        # Create bootstrap sample
        X_boot, y_boot = resample(X, y, random_state=i)
        
        # Clone and fit model
        model_clone = pickle.loads(pickle.dumps(model))
        model_clone.fit(X_boot, y_boot)
        
        # Get feature importances
        importances = get_importance(model_clone)
        all_importances[i, :] = importances
    
    # Calculate mean and std of feature importances
    mean_importances = np.mean(all_importances, axis=0)
    std_importances = np.std(all_importances, axis=0)
    
    # Calculate coefficient of variation (CV) for each feature
    # CV = std / mean, but avoid division by zero
    cv_importances = np.zeros(n_features)
    for i in range(n_features):
        if abs(mean_importances[i]) > 1e-10:
            cv_importances[i] = std_importances[i] / abs(mean_importances[i])
        else:
            cv_importances[i] = 0
    
    # Create feature importance data
    feature_importance_data = []
    for i in range(n_features):
        feature_importance_data.append({
            'feature': feature_names[i],
            'mean_importance': float(mean_importances[i]),
            'std_importance': float(std_importances[i]),
            'cv': float(cv_importances[i])
        })
    
    # Sort by absolute mean importance
    feature_importance_data.sort(key=lambda x: abs(x['mean_importance']), reverse=True)
    
    # Check stability
    # If the average CV is high, feature importances are unstable
    avg_cv = np.mean(cv_importances)
    is_stable = avg_cv < 0.5
    
    stability_result = {
        'has_feature_importances': True,
        'feature_importances': feature_importance_data,
        'stability': {
            'average_cv': float(avg_cv),
            'is_stable': is_stable
        }
    }
    
    print(f"  Feature importance stability: {is_stable}")
    print(f"  Average coefficient of variation: {avg_cv:.4f}")
    
    return stability_result


def perform_temporal_validation(
    model: Any,
    data_dir: str = './data'
) -> Dict[str, Any]:
    """
    Perform temporal validation by training on older data and testing on newer data.
    
    Args:
        model: Trained model
        data_dir: Directory containing patient JSON files
        
    Returns:
        Dictionary with temporal validation results
    """
    print("Performing temporal validation...")
    
    # Load and preprocess data
    latest_df, series_df = prepare_data(data_dir)
    
    # Convert testDate to datetime
    latest_df['testDate'] = pd.to_datetime(latest_df['testDate'])
    
    # Sort by test date
    latest_df = latest_df.sort_values('testDate')
    
    # Split into early and late data (60% early, 40% late)
    split_idx = int(len(latest_df) * 0.6)
    early_df = latest_df.iloc[:split_idx]
    late_df = latest_df.iloc[split_idx:]
    
    print(f"  Early data: {len(early_df)} samples")
    print(f"  Late data: {len(late_df)} samples")
    
    # Engineer features for early and late data
    early_features_df, early_feature_names = engineer_features(early_df, series_df)
    late_features_df, late_feature_names = engineer_features(late_df, series_df)
    
    # Ensure both datasets have the same features
    common_features = list(set(early_feature_names) & set(late_feature_names))
    
    # Create target variables
    y_early = (early_features_df['label'] == 'ABNORMAL').astype(int).values
    y_late = (late_features_df['label'] == 'ABNORMAL').astype(int).values
    
    # Create feature matrices
    X_early = early_features_df[common_features].values
    X_late = late_features_df[common_features].values
    
    # Train model on early data
    model_clone = pickle.loads(pickle.dumps(model))
    model_clone.fit(X_early, y_early)
    
    # Evaluate on late data
    y_late_pred = model_clone.predict(X_late)
    y_late_prob = model_clone.predict_proba(X_late)[:, 1]
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_late, y_late_pred),
        'precision': precision_score(y_late, y_late_pred),
        'recall': recall_score(y_late, y_late_pred),
        'f1': f1_score(y_late, y_late_pred),
        'roc_auc': roc_auc_score(y_late, y_late_prob)
    }
    
    # Check if temporal performance is acceptable
    # Recall should be at least 0.85 for clinical safety
    is_temporally_valid = metrics['recall'] >= 0.85
    
    temporal_result = {
        'is_temporally_valid': is_temporally_valid,
        'metrics': metrics,
        'early_data_size': len(early_df),
        'late_data_size': len(late_df)
    }
    
    print(f"  Temporal validation passed: {is_temporally_valid}")
    print(f"  Recall on newer data: {metrics['recall']:.4f}")
    print(f"  ROC AUC on newer data: {metrics['roc_auc']:.4f}")
    
    return temporal_result


def validate_model(
    model_dir: str = './model',
    data_dir: str = './data',
    reports_dir: str = './reports'
) -> Dict[str, Any]:
    """
    Main function to validate a trained model.
    
    Args:
        model_dir: Directory containing model files
        data_dir: Directory containing patient JSON files
        reports_dir: Directory to save validation reports
        
    Returns:
        Dictionary with validation results
    """
    # Create reports directory if it doesn't exist
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(os.path.join(reports_dir, 'metrics'), exist_ok=True)
    os.makedirs(os.path.join(reports_dir, 'clinical'), exist_ok=True)
    
    # Load model and metadata
    model, metadata = load_model_and_metadata(model_dir)
    
    # Load and preprocess data
    latest_df, series_df = prepare_data(data_dir)
    
    # Engineer features
    features_df, feature_names = engineer_features(latest_df, series_df)
    
    # Create target variable
    y = (features_df['label'] == 'ABNORMAL').astype(int).values
    
    # Create feature matrix
    X = features_df[feature_names].values
    
    # Split data into train and test sets
    # Use the same random state as in training
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Check for overfitting
    overfitting_result = check_overfitting(model, X_train, y_train, X_test, y_test)
    
    # Analyze learning curve
    learning_curve_result = analyze_learning_curve(model, X, y)
    
    # Analyze feature importance stability
    stability_result = analyze_feature_importance_stability(model, X, y, feature_names)
    
    # Perform temporal validation
    temporal_result = perform_temporal_validation(model, data_dir)
    
    # Calculate clinical safety metrics
    clinical_result = calculate_clinical_safety_metrics(model, X_test, y_test, features_df)
    
    # Calculate fairness metrics
    fairness_result = calculate_fairness_metrics(model, features_df, feature_names)
    
    # Combine all validation results
    validation_results = {
        'model_info': {
            'name': metadata.get('name', 'unknown'),
            'version': metadata.get('version', 'unknown'),
            'created_at': metadata.get('created_at', 'unknown')
        },
        'overfitting': overfitting_result,
        'learning_curve': learning_curve_result,
        'feature_importance_stability': stability_result,
        'temporal_validation': temporal_result,
        'clinical_safety': clinical_result,
        'fairness': fairness_result,
        'timestamp': datetime.now().isoformat()
    }
    
    # Check if model passes all validation criteria
    validation_passed = (
        not overfitting_result['is_overfit'] and
        temporal_result['is_temporally_valid'] and
        clinical_result['is_clinically_safe'] and
        fairness_result['is_fair']
    )
    
    validation_results['validation_passed'] = validation_passed
    
    # Save validation results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_path = os.path.join(
        reports_dir, 'metrics',
        f"validation_{metadata.get('version', 'unknown')}_{timestamp}.json"
    )
    
    # Convert numpy types to Python native types for JSON serialization
    def convert_to_serializable(obj):
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, (np.bool_)):
            return bool(obj)
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        else:
            return obj
    
    # Convert validation results to serializable format
    serializable_results = convert_to_serializable(validation_results)
    
    with open(results_path, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"\nValidation {'passed' if validation_passed else 'failed'}")
    print(f"Validation results saved to {results_path}")
    
    return validation_results


if __name__ == "__main__":
    # Validate the trained model
    validation_results = validate_model()
    
    # Print summary
    print("\nValidation summary:")
    print(f"  Passed: {validation_results['validation_passed']}")
    print(f"  Overfitting: {validation_results['overfitting']['is_overfit']}")
    print(f"  Temporal validity: {validation_results['temporal_validation']['is_temporally_valid']}")
    print(f"  Clinical safety: {validation_results['clinical_safety']['is_clinically_safe']}")
    print(f"  Fairness: {validation_results['fairness']['is_fair']}")