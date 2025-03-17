"""
Model handler module for the Active Patient Follow-Up Alert Dashboard.

This module handles loading and using the trained model for inference.
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelHandler:
    """
    Handler for loading and using the trained model.
    """
    
    def __init__(self, model_dir: str = './model'):
        """
        Initialize the model handler.
        
        Args:
            model_dir: Directory containing model files
        """
        self.model_dir = model_dir
        self.model = None
        self.model_info = None
        self.feature_names = None
        self.threshold = 0.5  # Default threshold
        
        # Try to load the model
        self.load_model()
    
    def load_model(self) -> bool:
        """
        Load the latest trained model and its metadata.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            # Read the current version
            version_path = os.path.join(self.model_dir, 'version.txt')
            if not os.path.exists(version_path):
                logger.error(f"Version file not found at {version_path}")
                return False
            
            with open(version_path, 'r') as f:
                model_version = f.read().strip()
            
            # Load the model
            model_path = os.path.join(self.model_dir, f"{model_version}.pkl")
            if not os.path.exists(model_path):
                logger.error(f"Model file not found at {model_path}")
                return False
            
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load the metadata
            info_path = os.path.join(self.model_dir, f"{model_version}_info.json")
            if not os.path.exists(info_path):
                logger.error(f"Model info file not found at {info_path}")
                return False
            
            with open(info_path, 'r') as f:
                self.model_info = json.load(f)
            
            # Get feature names
            self.feature_names = self.model_info.get('metadata', {}).get('feature_names', [])
            
            # Get optimal threshold from clinical metrics
            metrics = self.model_info.get('metrics', {})
            if 'optimal_threshold' in metrics:
                self.threshold = metrics['optimal_threshold']
            
            logger.info(f"Loaded model {model_version}")
            logger.info(f"Using threshold: {self.threshold}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def is_model_loaded(self) -> bool:
        """
        Check if the model is loaded.
        
        Returns:
            True if model is loaded, False otherwise
        """
        return self.model is not None and self.feature_names is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        if not self.is_model_loaded():
            return {
                'error': 'Model not loaded'
            }
        
        return {
            'name': self.model_info.get('name', 'unknown'),
            'version': self.model_info.get('version', 'unknown'),
            'created_at': self.model_info.get('created_at', 'unknown'),
            'metrics': self.model_info.get('metrics', {}),
            'feature_names': self.feature_names,
            'threshold': self.threshold
        }
    
    def preprocess_patient_data(self, patient_data: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Preprocess patient data for prediction.
        
        Args:
            patient_data: Dictionary with patient data
            
        Returns:
            Tuple of (feature vector, feature dictionary)
        """
        # Extract patient info
        patient_id = patient_data.get('patientId', '')
        age = patient_data.get('age', 0)
        gender = patient_data.get('gender', '')
        
        # Get the most recent test
        tests = patient_data.get('tests', [])
        if not tests:
            raise ValueError("No test data provided")
        
        # Sort tests by date and get the most recent
        sorted_tests = sorted(tests, key=lambda x: x.get('testDate', ''))
        latest_test = sorted_tests[-1]
        
        # Create feature dictionary
        feature_dict = {
            'patientId': patient_id,
            'age': age,
            'gender': gender,
            'testDate': latest_test.get('testDate', '')
        }
        
        # Add test metrics
        for key, value in latest_test.items():
            if key not in ['testDate', 'testId']:
                feature_dict[key] = value
        
        # Create feature vector
        # This is a simplified version - in a real implementation,
        # we would need to apply the same feature engineering as in training
        feature_vector = []
        for feature in self.feature_names:
            if feature in feature_dict:
                feature_vector.append(feature_dict[feature])
            else:
                # If feature is missing, use a default value (0)
                feature_vector.append(0)
        
        return np.array(feature_vector).reshape(1, -1), feature_dict
    
    def predict(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a prediction for a patient.
        
        Args:
            patient_data: Dictionary with patient data
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_model_loaded():
            raise RuntimeError("Model not loaded")
        
        try:
            # Preprocess patient data
            X, feature_dict = self.preprocess_patient_data(patient_data)
            
            # Make prediction
            y_prob = self.model.predict_proba(X)[0, 1]
            y_pred = 1 if y_prob >= self.threshold else 0
            
            # Convert to label
            prediction = 'ABNORMAL' if y_pred == 1 else 'NORMAL'
            
            # Calculate risk score (1-10)
            risk_score = min(10, max(1, int(y_prob * 10) + 1))
            
            # Calculate confidence
            # For probabilities close to 0 or 1, confidence is high
            # For probabilities close to 0.5, confidence is low
            confidence = 2 * abs(y_prob - 0.5)
            
            # Get feature contributions
            # This is a simplified version - in a real implementation,
            # we would use SHAP values or other explainability methods
            top_contributors = self.get_feature_contributions(X, feature_dict)
            
            # Create prediction result
            result = {
                'patientId': patient_data.get('patientId', ''),
                'prediction': prediction,
                'probability': float(y_prob),
                'confidence': float(confidence),
                'risk_score': risk_score,
                'top_contributors': top_contributors,
                'model_version': self.model_info.get('version', 'unknown'),
                'timestamp': datetime.now().isoformat()
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise
    
    def get_feature_contributions(
        self, X: np.ndarray, feature_dict: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get feature contributions to the prediction.
        
        Args:
            X: Feature vector
            feature_dict: Dictionary with feature values
            
        Returns:
            List of dictionaries with feature contributions
        """
        # This is a simplified version - in a real implementation,
        # we would use SHAP values or other explainability methods
        
        # Get feature importances from model
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            importances = self.model.coef_[0]
        else:
            # If model doesn't have feature importances, use uniform values
            importances = np.ones(len(self.feature_names)) / len(self.feature_names)
        
        # Calculate contributions
        contributions = []
        for i, feature in enumerate(self.feature_names):
            # Skip non-numeric features
            if feature in ['patientId', 'gender', 'testDate']:
                continue
            
            # Get feature value
            value = X[0, i] if i < X.shape[1] else 0
            
            # Get feature importance
            importance = importances[i] if i < len(importances) else 0
            
            # Calculate contribution
            contribution = abs(value * importance)
            
            # Check if abnormal
            is_abnormal = False
            if feature in feature_dict:
                # Check if feature has reference ranges
                min_key = f"{feature}Min"
                max_key = f"{feature}Max"
                if min_key in feature_dict and max_key in feature_dict:
                    min_val = feature_dict[min_key]
                    max_val = feature_dict[max_key]
                    is_abnormal = value < min_val or value > max_val
            
            contributions.append({
                'feature': feature,
                'value': float(value),
                'contribution': float(contribution),
                'is_abnormal': is_abnormal
            })
        
        # Sort by contribution and get top 5
        contributions.sort(key=lambda x: x['contribution'], reverse=True)
        return contributions[:5]
    
    def batch_predict(self, patients_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Make predictions for multiple patients.
        
        Args:
            patients_data: List of dictionaries with patient data
            
        Returns:
            List of dictionaries with prediction results
        """
        if not self.is_model_loaded():
            raise RuntimeError("Model not loaded")
        
        results = []
        for patient_data in patients_data:
            try:
                result = self.predict(patient_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Error predicting for patient {patient_data.get('patientId', '')}: {e}")
                # Add error result
                results.append({
                    'patientId': patient_data.get('patientId', ''),
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return results


# Singleton instance
model_handler = ModelHandler()


if __name__ == "__main__":
    # Test the model handler
    handler = ModelHandler()
    
    if handler.is_model_loaded():
        print("Model loaded successfully")
        print(f"Model info: {handler.get_model_info()}")
    else:
        print("Failed to load model")