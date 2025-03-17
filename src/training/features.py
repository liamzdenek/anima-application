"""
Feature engineering module for the Active Patient Follow-Up Alert Dashboard.

This module handles creating features from the preprocessed patient data,
including derived features, temporal patterns, and feature selection.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from sklearn.feature_selection import SelectKBest, f_classif


def create_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create basic features from the preprocessed data.
    
    Args:
        df: DataFrame with preprocessed patient data
        
    Returns:
        DataFrame with basic features added
    """
    # Create a copy to avoid modifying the original
    features_df = df.copy()
    
    # List of test metrics to use as features
    test_metrics = [
        'hemoglobin', 'wbc', 'platelets', 'neutrophils', 
        'lymphocytes', 'rbc', 'mcv', 'mch'
    ]
    
    # Calculate deviation from reference range midpoint
    for metric in test_metrics:
        if metric in df.columns:
            min_col = f"{metric}Min"
            max_col = f"{metric}Max"
            
            if min_col in df.columns and max_col in df.columns:
                # Calculate midpoint of reference range
                midpoint = (df[min_col] + df[max_col]) / 2
                
                # Calculate deviation from midpoint (as percentage)
                features_df[f"{metric}_dev"] = (df[metric] - midpoint) / midpoint * 100
                
                # Calculate how far outside reference range (0 if within range)
                features_df[f"{metric}_out"] = np.maximum(
                    0, 
                    np.maximum(
                        df[min_col] - df[metric],  # Below min
                        df[metric] - df[max_col]   # Above max
                    )
                ) / midpoint * 100
    
    return features_df


def create_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create derived features that combine multiple metrics.
    
    Args:
        df: DataFrame with basic features
        
    Returns:
        DataFrame with derived features added
    """
    # Create a copy to avoid modifying the original
    features_df = df.copy()
    
    # Create neutrophil to lymphocyte ratio (inflammation marker)
    if 'neutrophils' in df.columns and 'lymphocytes' in df.columns:
        # Avoid division by zero
        features_df['nlr'] = df['neutrophils'] / df['lymphocytes'].replace(0, 0.001)
    
    # Create red cell distribution width to platelet ratio
    if 'rbc' in df.columns and 'platelets' in df.columns:
        features_df['rpr'] = df['rbc'] / df['platelets'].replace(0, 0.001) * 1000
    
    # Create mean corpuscular hemoglobin concentration
    if 'mch' in df.columns and 'mcv' in df.columns:
        features_df['mchc'] = df['mch'] / df['mcv'].replace(0, 0.001) * 100
    
    # Count number of abnormal values
    abnormal_count = 0
    for col in df.columns:
        if col.endswith('_out'):
            abnormal_count += (df[col] > 0).astype(int)
    
    features_df['abnormal_count'] = abnormal_count
    
    return features_df


def create_temporal_features(latest_df: pd.DataFrame, series_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create temporal features from time series data.
    
    Args:
        latest_df: DataFrame with latest test for each patient
        series_df: DataFrame with all tests for all patients
        
    Returns:
        DataFrame with temporal features added to latest_df
    """
    # Create a copy to avoid modifying the original
    features_df = latest_df.copy()
    
    # List of test metrics to analyze for trends
    test_metrics = [
        'hemoglobin', 'wbc', 'platelets', 'neutrophils', 
        'lymphocytes', 'rbc', 'mcv', 'mch'
    ]
    
    # Group by patient ID
    grouped = series_df.groupby('patientId')
    
    # For each patient, calculate temporal features
    for patient_id, patient_group in grouped:
        if len(patient_group) >= 2:  # Need at least 2 tests for trends
            # Sort by test date
            patient_group = patient_group.sort_values('testDate')
            
            # Get the patient's row in the features dataframe
            patient_idx = features_df.index[features_df['patientId'] == patient_id]
            
            if len(patient_idx) > 0:
                # Calculate trends for each metric
                for metric in test_metrics:
                    if metric in patient_group.columns:
                        # Calculate slope of the metric over time
                        values = patient_group[metric].values
                        
                        # Simple slope calculation (last - first) / count
                        if len(values) >= 2:
                            slope = (values[-1] - values[0]) / len(values)
                            features_df.loc[patient_idx, f"{metric}_trend"] = slope
                            
                            # Volatility (standard deviation)
                            features_df.loc[patient_idx, f"{metric}_volatility"] = np.std(values)
    
    # Fill missing trend values with 0 (no trend)
    for metric in test_metrics:
        trend_col = f"{metric}_trend"
        if trend_col in features_df.columns:
            features_df[trend_col] = features_df[trend_col].fillna(0)
        
        volatility_col = f"{metric}_volatility"
        if volatility_col in features_df.columns:
            features_df[volatility_col] = features_df[volatility_col].fillna(0)
    
    return features_df


def normalize_by_demographics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize features based on demographic factors (age, gender).
    
    Args:
        df: DataFrame with features
        
    Returns:
        DataFrame with demographically normalized features
    """
    # Create a copy to avoid modifying the original
    features_df = df.copy()
    
    # List of test metrics to normalize
    test_metrics = [
        'hemoglobin', 'wbc', 'platelets', 'neutrophils', 
        'lymphocytes', 'rbc', 'mcv', 'mch'
    ]
    
    # Normalize by age group
    if 'age' in df.columns:
        # Create age groups
        features_df['age_group'] = pd.cut(
            df['age'], 
            bins=[0, 18, 40, 60, 80, 120], 
            labels=['0-18', '19-40', '41-60', '61-80', '81+']
        )
        
        # For each age group and gender combination, normalize metrics
        for metric in test_metrics:
            if metric in df.columns:
                # Group by age group and gender
                grouped = features_df.groupby(['age_group', 'gender'], observed=False)
                
                # Calculate mean and std for each group
                group_stats = grouped[metric].agg(['mean', 'std']).reset_index()
                
                # Merge stats back to the main dataframe
                features_df = pd.merge(
                    features_df, 
                    group_stats, 
                    on=['age_group', 'gender'], 
                    how='left'
                )
                
                # Calculate z-score within demographic group
                features_df[f"{metric}_demo_norm"] = (
                    (features_df[metric] - features_df['mean']) / features_df['std'].replace(0, 1)
                )
                
                # Drop the temporary columns
                features_df = features_df.drop(['mean', 'std'], axis=1)
    
    return features_df


def select_features(df: pd.DataFrame, target_col: str = 'label', k: int = 20) -> Tuple[pd.DataFrame, List[str]]:
    """
    Select the most important features using statistical tests.
    
    Args:
        df: DataFrame with all features
        target_col: Column name for the target variable
        k: Number of features to select
        
    Returns:
        Tuple of (DataFrame with selected features, list of selected feature names)
    """
    # Create binary target (1 for ABNORMAL, 0 for NORMAL)
    y = (df[target_col] == 'ABNORMAL').astype(int)
    
    # Get numeric feature columns (exclude target and non-numeric columns)
    exclude_cols = [target_col, 'patientId', 'testDate', 'gender', 'age_group']
    feature_cols = [col for col in df.columns if col not in exclude_cols and df[col].dtype in ['int64', 'float64']]
    
    # Ensure we don't try to select more features than available
    k = min(k, len(feature_cols))
    
    # Get feature matrix and handle missing values
    X = df[feature_cols].copy()
    
    # Fill NaN values with column means
    X = X.fillna(X.mean())
    
    # Check if there are still any NaN values (e.g., if entire column was NaN)
    if X.isna().any().any():
        # Fill any remaining NaNs with 0
        X = X.fillna(0)
    
    # Select k best features
    selector = SelectKBest(f_classif, k=k)
    X_new = selector.fit_transform(X, y)
    
    # Get the selected feature names
    selected_mask = selector.get_support()
    selected_features = [feature_cols[i] for i in range(len(feature_cols)) if selected_mask[i]]
    
    # Create DataFrame with selected features
    selected_df = df[selected_features + [target_col, 'patientId']]
    
    print(f"Selected {len(selected_features)} features: {selected_features}")
    
    return selected_df, selected_features


def engineer_features(latest_df: pd.DataFrame, series_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Main function to engineer features for model training.
    
    Args:
        latest_df: DataFrame with latest test for each patient
        series_df: DataFrame with all tests for all patients
        
    Returns:
        Tuple of (DataFrame with engineered features, list of feature names)
    """
    # Create basic features
    features_df = create_basic_features(latest_df)
    
    # Create derived features
    features_df = create_derived_features(features_df)
    
    # Create temporal features
    features_df = create_temporal_features(features_df, series_df)
    
    # Normalize by demographics
    features_df = normalize_by_demographics(features_df)
    
    # Select the most important features
    selected_df, selected_features = select_features(features_df)
    
    return selected_df, selected_features


if __name__ == "__main__":
    # Test the feature engineering functions
    from preprocess import prepare_data
    
    # Load and preprocess data
    latest_df, series_df = prepare_data()
    
    # Engineer features
    features_df, selected_features = engineer_features(latest_df, series_df)
    
    print("\nEngineered features dataframe:")
    print(features_df.shape)
    print(features_df.columns.tolist())