"""
Model training module for the Active Patient Follow-Up Alert Dashboard.

This module handles training machine learning models on the engineered features,
evaluating their performance, and saving the best model for inference.
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    precision_recall_curve, roc_curve
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Import local modules
from .preprocess import prepare_data
from .features import engineer_features


def prepare_training_data(
    data_dir: str = './data',
    test_size: float = 0.2,
    val_size: float = 0.2,
    random_state: int = 42
) -> Tuple[
    np.ndarray, np.ndarray, np.ndarray,
    np.ndarray, np.ndarray, np.ndarray,
    List[str], Dict[str, Any]
]:
    """
    Prepare data for model training, including train/val/test split.
    
    Args:
        data_dir: Directory containing patient JSON files
        test_size: Proportion of data to use for testing
        val_size: Proportion of training data to use for validation
        random_state: Random seed for reproducibility
        
    Returns:
        Tuple of (X_train, X_val, X_test, y_train, y_val, y_test, feature_names, metadata)
    """
    # Load and preprocess data
    latest_df, series_df = prepare_data(data_dir)
    
    # Engineer features
    features_df, selected_features = engineer_features(latest_df, series_df)
    
    # Create binary target (1 for ABNORMAL, 0 for NORMAL)
    y = (features_df['label'] == 'ABNORMAL').astype(int).values
    
    # Extract feature matrix
    X = features_df[selected_features].values
    
    # First split: training+validation and test
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Second split: training and validation
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, 
        test_size=val_size/(1-test_size),  # Adjust for the first split
        random_state=random_state,
        stratify=y_train_val
    )
    
    # Create metadata
    metadata = {
        'feature_names': selected_features,
        'target_name': 'abnormal',
        'target_values': ['NORMAL', 'ABNORMAL'],
        'data_shape': {
            'total': X.shape[0],
            'train': X_train.shape[0],
            'val': X_val.shape[0],
            'test': X_test.shape[0],
            'features': X.shape[1]
        },
        'class_distribution': {
            'total': {
                'NORMAL': int((y == 0).sum()),
                'ABNORMAL': int((y == 1).sum())
            },
            'train': {
                'NORMAL': int((y_train == 0).sum()),
                'ABNORMAL': int((y_train == 1).sum())
            },
            'val': {
                'NORMAL': int((y_val == 0).sum()),
                'ABNORMAL': int((y_val == 1).sum())
            },
            'test': {
                'NORMAL': int((y_test == 0).sum()),
                'ABNORMAL': int((y_test == 1).sum())
            }
        },
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"Data prepared for training:")
    print(f"  Training set: {X_train.shape[0]} samples")
    print(f"  Validation set: {X_val.shape[0]} samples")
    print(f"  Test set: {X_test.shape[0]} samples")
    print(f"  Features: {X_train.shape[1]}")
    
    return X_train, X_val, X_test, y_train, y_val, y_test, selected_features, metadata


def train_logistic_regression(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    feature_names: List[str],
    cv: int = 5
) -> Tuple[Pipeline, Dict[str, Any]]:
    """
    Train a logistic regression model with hyperparameter tuning.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        y_val: Validation labels
        feature_names: List of feature names
        cv: Number of cross-validation folds
        
    Returns:
        Tuple of (trained model pipeline, performance metrics)
    """
    print("\nTraining Logistic Regression model...")
    
    # Create pipeline with preprocessing and model
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', LogisticRegression(random_state=42, max_iter=1000))
    ])
    
    # Define hyperparameter grid
    param_grid = {
        'model__C': [0.001, 0.01, 0.1, 1, 10, 100],
        'model__penalty': ['l1', 'l2'],
        'model__solver': ['liblinear', 'saga'],
        'model__class_weight': [None, 'balanced']
    }
    
    # Create cross-validation strategy
    cv_strategy = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    
    # Perform grid search
    grid_search = GridSearchCV(
        pipeline, param_grid, cv=cv_strategy,
        scoring='roc_auc', n_jobs=-1, verbose=1
    )
    
    # Fit the model
    grid_search.fit(X_train, y_train)
    
    # Get the best model
    best_model = grid_search.best_estimator_
    
    # Evaluate on validation set
    y_val_pred = best_model.predict(X_val)
    y_val_prob = best_model.predict_proba(X_val)[:, 1]
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_val, y_val_pred),
        'precision': precision_score(y_val, y_val_pred),
        'recall': recall_score(y_val, y_val_pred),
        'f1': f1_score(y_val, y_val_pred),
        'roc_auc': roc_auc_score(y_val, y_val_prob),
        'confusion_matrix': confusion_matrix(y_val, y_val_pred).tolist(),
        'best_params': grid_search.best_params_,
        'cv_results': {
            'mean_test_score': float(grid_search.cv_results_['mean_test_score'][grid_search.best_index_]),
            'std_test_score': float(grid_search.cv_results_['std_test_score'][grid_search.best_index_])
        }
    }
    
    # Get feature importance (coefficients)
    if hasattr(best_model['model'], 'coef_'):
        coef = best_model['model'].coef_[0]
        feature_importance = dict(zip(feature_names, coef))
        metrics['feature_importance'] = feature_importance
    
    print(f"  Best parameters: {grid_search.best_params_}")
    print(f"  Validation accuracy: {metrics['accuracy']:.4f}")
    print(f"  Validation ROC AUC: {metrics['roc_auc']:.4f}")
    print(f"  Validation recall: {metrics['recall']:.4f}")
    
    return best_model, metrics


def train_random_forest(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    feature_names: List[str],
    cv: int = 5
) -> Tuple[Pipeline, Dict[str, Any]]:
    """
    Train a random forest model with hyperparameter tuning.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        y_val: Validation labels
        feature_names: List of feature names
        cv: Number of cross-validation folds
        
    Returns:
        Tuple of (trained model pipeline, performance metrics)
    """
    print("\nTraining Random Forest model...")
    
    # Create pipeline with preprocessing and model
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', RandomForestClassifier(random_state=42))
    ])
    
    # Define hyperparameter grid with stronger regularization to reduce overfitting
    param_grid = {
        'model__n_estimators': [100, 200, 300],  # More trees for better generalization
        'model__max_depth': [5, 10, 15, None],   # Limit depth to prevent overfitting
        'model__min_samples_split': [5, 10, 15], # Require more samples to split nodes
        'model__min_samples_leaf': [2, 4, 8],    # Require more samples in leaf nodes
        'model__max_features': ['sqrt', 'log2'], # Limit features to reduce overfitting
        'model__class_weight': [None, 'balanced', {0: 1, 1: 2}, {0: 1, 1: 3}]  # Prioritize recall for abnormal class
    }
    
    # Create cross-validation strategy
    cv_strategy = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    
    # Perform grid search
    grid_search = GridSearchCV(
        pipeline, param_grid, cv=cv_strategy,
        scoring='roc_auc', n_jobs=-1, verbose=1
    )
    
    # Fit the model
    grid_search.fit(X_train, y_train)
    
    # Get the best model
    best_model = grid_search.best_estimator_
    
    # Evaluate on validation set
    y_val_pred = best_model.predict(X_val)
    y_val_prob = best_model.predict_proba(X_val)[:, 1]
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_val, y_val_pred),
        'precision': precision_score(y_val, y_val_pred),
        'recall': recall_score(y_val, y_val_pred),
        'f1': f1_score(y_val, y_val_pred),
        'roc_auc': roc_auc_score(y_val, y_val_prob),
        'confusion_matrix': confusion_matrix(y_val, y_val_pred).tolist(),
        'best_params': grid_search.best_params_,
        'cv_results': {
            'mean_test_score': float(grid_search.cv_results_['mean_test_score'][grid_search.best_index_]),
            'std_test_score': float(grid_search.cv_results_['std_test_score'][grid_search.best_index_])
        }
    }
    
    # Get feature importance
    if hasattr(best_model['model'], 'feature_importances_'):
        feature_importance = dict(zip(feature_names, best_model['model'].feature_importances_))
        metrics['feature_importance'] = feature_importance
    
    print(f"  Best parameters: {grid_search.best_params_}")
    print(f"  Validation accuracy: {metrics['accuracy']:.4f}")
    print(f"  Validation ROC AUC: {metrics['roc_auc']:.4f}")
    print(f"  Validation recall: {metrics['recall']:.4f}")
    
    return best_model, metrics


def evaluate_model(
    model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_names: List[str],
    model_name: str
) -> Dict[str, Any]:
    """
    Evaluate a trained model on the test set.
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
        feature_names: List of feature names
        model_name: Name of the model
        
    Returns:
        Dictionary of performance metrics
    """
    print(f"\nEvaluating {model_name} on test set...")
    
    # Make predictions
    y_test_pred = model.predict(X_test)
    y_test_prob = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    metrics = {
        'model_name': model_name,
        'accuracy': accuracy_score(y_test, y_test_pred),
        'precision': precision_score(y_test, y_test_pred),
        'recall': recall_score(y_test, y_test_pred),
        'f1': f1_score(y_test, y_test_pred),
        'roc_auc': roc_auc_score(y_test, y_test_prob),
        'confusion_matrix': confusion_matrix(y_test, y_test_pred).tolist(),
        'classification_report': classification_report(y_test, y_test_pred, output_dict=True)
    }
    
    # Calculate ROC curve
    fpr, tpr, _ = roc_curve(y_test, y_test_prob)
    metrics['roc_curve'] = {
        'fpr': fpr.tolist(),
        'tpr': tpr.tolist()
    }
    
    # Calculate precision-recall curve
    precision, recall, _ = precision_recall_curve(y_test, y_test_prob)
    metrics['pr_curve'] = {
        'precision': precision.tolist(),
        'recall': recall.tolist()
    }
    
    print(f"  Test accuracy: {metrics['accuracy']:.4f}")
    print(f"  Test ROC AUC: {metrics['roc_auc']:.4f}")
    print(f"  Test recall: {metrics['recall']:.4f}")
    print(f"  Test precision: {metrics['precision']:.4f}")
    print(f"  Test F1 score: {metrics['f1']:.4f}")
    
    return metrics


def save_model(
    model: Any,
    metadata: Dict[str, Any],
    metrics: Dict[str, Any],
    model_dir: str = './model',
    model_name: str = 'abnormal_detection'
) -> str:
    """
    Save the trained model and its metadata.
    
    Args:
        model: Trained model
        metadata: Model metadata
        metrics: Performance metrics
        model_dir: Directory to save the model
        model_name: Base name for the model files
        
    Returns:
        Path to the saved model
    """
    # Create model directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    # Create a timestamp for versioning
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create model info
    model_info = {
        'name': model_name,
        'version': timestamp,
        'metadata': metadata,
        'metrics': metrics,
        'created_at': datetime.now().isoformat()
    }
    
    # Save model
    model_path = os.path.join(model_dir, f"{model_name}_{timestamp}.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # Save model info
    info_path = os.path.join(model_dir, f"{model_name}_{timestamp}_info.json")
    with open(info_path, 'w') as f:
        json.dump(model_info, f, indent=2)
    
    # Save current version info
    version_path = os.path.join(model_dir, 'version.txt')
    with open(version_path, 'w') as f:
        f.write(f"{model_name}_{timestamp}")
    
    print(f"\nModel saved to {model_path}")
    print(f"Model info saved to {info_path}")
    
    return model_path


def train_model(
    data_dir: str = './data',
    model_dir: str = './model',
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Main function to train and evaluate models.
    
    Args:
        data_dir: Directory containing patient JSON files
        model_dir: Directory to save the model
        random_state: Random seed for reproducibility
        
    Returns:
        Dictionary with training results
    """
    # Prepare data
    X_train, X_val, X_test, y_train, y_val, y_test, feature_names, metadata = prepare_training_data(
        data_dir=data_dir,
        random_state=random_state
    )
    
    # Train logistic regression model
    lr_model, lr_metrics = train_logistic_regression(
        X_train, y_train, X_val, y_val, feature_names
    )
    
    # Train random forest model
    rf_model, rf_metrics = train_random_forest(
        X_train, y_train, X_val, y_val, feature_names
    )
    
    # Evaluate models on test set
    lr_test_metrics = evaluate_model(lr_model, X_test, y_test, feature_names, 'LogisticRegression')
    rf_test_metrics = evaluate_model(rf_model, X_test, y_test, feature_names, 'RandomForest')
    
    # Combine metrics
    lr_metrics.update(lr_test_metrics)
    rf_metrics.update(rf_test_metrics)
    
    # Perform a simple temporal validation to help with model selection
    print("\nPerforming temporal validation for model selection...")
    
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
    
    # Train models on early data and evaluate on late data
    lr_model_temp = pickle.loads(pickle.dumps(lr_model))
    lr_model_temp.fit(X_early, y_early)
    lr_late_pred = lr_model_temp.predict(X_late)
    lr_temporal_recall = recall_score(y_late, lr_late_pred)
    
    rf_model_temp = pickle.loads(pickle.dumps(rf_model))
    rf_model_temp.fit(X_early, y_early)
    rf_late_pred = rf_model_temp.predict(X_late)
    rf_temporal_recall = recall_score(y_late, rf_late_pred)
    
    print(f"  Logistic Regression temporal recall: {lr_temporal_recall:.4f}")
    print(f"  Random Forest temporal recall: {rf_temporal_recall:.4f}")
    
    # Calculate a combined score that prioritizes temporal stability and recall
    # Formula: 0.5 * validation_recall + 0.5 * temporal_recall
    lr_combined_score = 0.5 * lr_metrics['recall'] + 0.5 * lr_temporal_recall
    rf_combined_score = 0.5 * rf_metrics['recall'] + 0.5 * rf_temporal_recall
    
    print(f"  Logistic Regression combined score: {lr_combined_score:.4f}")
    print(f"  Random Forest combined score: {rf_combined_score:.4f}")
    
    # Select the best model based on the combined score
    if lr_combined_score > rf_combined_score:
        best_model = lr_model
        best_metrics = lr_metrics
        best_name = 'LogisticRegression'
        print("\nLogistic Regression selected as the best model.")
    else:
        best_model = rf_model
        best_metrics = rf_metrics
        best_name = 'RandomForest'
        print("\nRandom Forest selected as the best model.")
    
    # Save the best model
    model_path = save_model(
        best_model,
        metadata,
        best_metrics,
        model_dir=model_dir,
        model_name=f"abnormal_detection_{best_name.lower()}"
    )
    
    # Return results
    results = {
        'best_model': {
            'name': best_name,
            'path': model_path,
            'metrics': best_metrics
        },
        'models': {
            'LogisticRegression': lr_metrics,
            'RandomForest': rf_metrics
        },
        'metadata': metadata
    }
    
    return results


if __name__ == "__main__":
    # Train and evaluate models
    results = train_model()
    
    # Print summary
    print("\nTraining complete!")
    print(f"Best model: {results['best_model']['name']}")
    print(f"  Accuracy: {results['best_model']['metrics']['accuracy']:.4f}")
    print(f"  ROC AUC: {results['best_model']['metrics']['roc_auc']:.4f}")
    print(f"  Recall: {results['best_model']['metrics']['recall']:.4f}")
    print(f"  Precision: {results['best_model']['metrics']['precision']:.4f}")
    print(f"  F1 Score: {results['best_model']['metrics']['f1']:.4f}")