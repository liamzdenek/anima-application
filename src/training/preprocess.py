"""
Data preprocessing module for the Active Patient Follow-Up Alert Dashboard.

This module handles loading patient data from JSON files, cleaning the data,
and preparing it for feature engineering and model training.
"""

import os
import json
import glob
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional


def load_patient_data(data_dir: str = './data') -> List[Dict[str, Any]]:
    """
    Load all patient data from JSON files in the specified directory.
    
    Args:
        data_dir: Directory containing patient JSON files
        
    Returns:
        List of patient data dictionaries
    """
    patient_files = glob.glob(os.path.join(data_dir, 'patient-*.json'))
    patients_data = []
    
    for file in patient_files:
        try:
            with open(file, 'r') as f:
                patient_data = json.load(f)
                patients_data.append(patient_data)
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    print(f"Loaded {len(patients_data)} patient records")
    return patients_data


def extract_latest_tests(patients_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Extract the most recent test for each patient and convert to DataFrame.
    
    Args:
        patients_data: List of patient data dictionaries
        
    Returns:
        DataFrame with one row per patient, containing latest test values
    """
    latest_tests = []
    
    for patient in patients_data:
        # Sort tests by date and get the most recent
        if 'tests' in patient and patient['tests']:
            sorted_tests = sorted(patient['tests'], key=lambda x: x.get('testDate', ''))
            latest_test = sorted_tests[-1]
            
            # Create a record with patient info and test results
            record = {
                'patientId': patient.get('patientId', ''),
                'age': patient.get('age', 0),
                'gender': patient.get('gender', ''),
                'testDate': latest_test.get('testDate', ''),
                'label': patient.get('label', 'NORMAL'),
                'confidence': patient.get('confidence', 0.0)
            }
            
            # Add all test metrics
            for key, value in latest_test.items():
                if key not in ['testDate', 'testId', 'referenceRanges', 'abnormalFlags']:
                    record[key] = value
            
            # Add reference ranges
            if 'referenceRanges' in latest_test:
                for metric, range_values in latest_test['referenceRanges'].items():
                    record[f"{metric}Min"] = range_values.get('min', 0)
                    record[f"{metric}Max"] = range_values.get('max', 0)
            
            latest_tests.append(record)
    
    return pd.DataFrame(latest_tests)


def extract_test_series(patients_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Extract all tests for all patients and convert to a time series DataFrame.
    
    Args:
        patients_data: List of patient data dictionaries
        
    Returns:
        DataFrame with multiple rows per patient, one for each test
    """
    all_tests = []
    
    for patient in patients_data:
        patient_id = patient.get('patientId', '')
        age = patient.get('age', 0)
        gender = patient.get('gender', '')
        label = patient.get('label', 'NORMAL')
        confidence = patient.get('confidence', 0.0)
        
        # Process each test for this patient
        if 'tests' in patient and patient['tests']:
            for test in patient['tests']:
                # Create a record with patient info and test results
                record = {
                    'patientId': patient_id,
                    'age': age,
                    'gender': gender,
                    'testDate': test.get('testDate', ''),
                    'label': label,
                    'confidence': confidence
                }
                
                # Add all test metrics
                for key, value in test.items():
                    if key not in ['testDate', 'testId', 'referenceRanges', 'abnormalFlags']:
                        record[key] = value
                
                # Add reference ranges
                if 'referenceRanges' in test:
                    for metric, range_values in test['referenceRanges'].items():
                        record[f"{metric}Min"] = range_values.get('min', 0)
                        record[f"{metric}Max"] = range_values.get('max', 0)
                
                all_tests.append(record)
    
    return pd.DataFrame(all_tests)


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in the dataset.
    
    Args:
        df: DataFrame with patient test data
        
    Returns:
        DataFrame with missing values handled
    """
    # Check for missing values
    missing_count = df.isnull().sum()
    print(f"Missing values before handling:\n{missing_count[missing_count > 0]}")
    
    # For numeric columns, fill with median
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna(df[col].median())
    
    # For categorical columns, fill with mode
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        if df[col].isnull().sum() > 0 and col != 'patientId':
            df[col] = df[col].fillna(df[col].mode()[0])
    
    # Check if any missing values remain
    missing_count = df.isnull().sum()
    if missing_count.sum() > 0:
        print(f"Missing values after handling:\n{missing_count[missing_count > 0]}")
    
    return df


def normalize_test_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize test values based on reference ranges.
    
    Args:
        df: DataFrame with patient test data
        
    Returns:
        DataFrame with normalized test values added
    """
    # List of test metrics to normalize
    test_metrics = [
        'hemoglobin', 'wbc', 'platelets', 'neutrophils', 
        'lymphocytes', 'rbc', 'mcv', 'mch'
    ]
    
    # Create normalized versions of each metric
    for metric in test_metrics:
        if metric in df.columns:
            # Check if reference ranges are in the data
            min_col = f"{metric}Min"
            max_col = f"{metric}Max"
            
            if min_col in df.columns and max_col in df.columns:
                # Normalize based on reference range
                df[f"{metric}_norm"] = (df[metric] - df[min_col]) / (df[max_col] - df[min_col])
            else:
                # If no reference range, use z-score normalization
                df[f"{metric}_norm"] = (df[metric] - df[metric].mean()) / df[metric].std()
    
    return df


def prepare_data(data_dir: str = './data') -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Main function to prepare data for model training.
    
    Args:
        data_dir: Directory containing patient JSON files
        
    Returns:
        Tuple of (latest_tests_df, time_series_df)
    """
    # Load patient data
    patients_data = load_patient_data(data_dir)
    
    # Extract latest tests and all tests
    latest_tests_df = extract_latest_tests(patients_data)
    time_series_df = extract_test_series(patients_data)
    
    # Handle missing values
    latest_tests_df = handle_missing_values(latest_tests_df)
    time_series_df = handle_missing_values(time_series_df)
    
    # Normalize test values
    latest_tests_df = normalize_test_values(latest_tests_df)
    time_series_df = normalize_test_values(time_series_df)
    
    return latest_tests_df, time_series_df


if __name__ == "__main__":
    # Test the preprocessing functions
    latest_df, series_df = prepare_data()
    
    print("\nLatest tests dataframe:")
    print(latest_df.shape)
    print(latest_df.columns.tolist())
    
    print("\nTime series dataframe:")
    print(series_df.shape)
    print(series_df.columns.tolist())