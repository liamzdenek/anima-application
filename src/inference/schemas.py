"""
API schema definitions for the Active Patient Follow-Up Alert Dashboard.

This module defines the request and response schemas for the inference API.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class TestResult(BaseModel):
    """
    Schema for a single blood test result.
    """
    testId: str = Field(..., description="Unique identifier for the test")
    testDate: str = Field(..., description="Date of the test (ISO format)")
    hemoglobin: Optional[float] = Field(None, description="Hemoglobin level (g/dL)")
    hemoglobinMin: Optional[float] = Field(None, description="Minimum reference range for hemoglobin")
    hemoglobinMax: Optional[float] = Field(None, description="Maximum reference range for hemoglobin")
    wbc: Optional[float] = Field(None, description="White blood cell count (10^9/L)")
    wbcMin: Optional[float] = Field(None, description="Minimum reference range for WBC")
    wbcMax: Optional[float] = Field(None, description="Maximum reference range for WBC")
    platelets: Optional[float] = Field(None, description="Platelet count (10^9/L)")
    plateletsMin: Optional[float] = Field(None, description="Minimum reference range for platelets")
    plateletsMax: Optional[float] = Field(None, description="Maximum reference range for platelets")
    neutrophils: Optional[float] = Field(None, description="Neutrophil count (10^9/L)")
    neutrophilsMin: Optional[float] = Field(None, description="Minimum reference range for neutrophils")
    neutrophilsMax: Optional[float] = Field(None, description="Maximum reference range for neutrophils")
    lymphocytes: Optional[float] = Field(None, description="Lymphocyte count (10^9/L)")
    lymphocytesMin: Optional[float] = Field(None, description="Minimum reference range for lymphocytes")
    lymphocytesMax: Optional[float] = Field(None, description="Maximum reference range for lymphocytes")
    rbc: Optional[float] = Field(None, description="Red blood cell count (10^12/L)")
    rbcMin: Optional[float] = Field(None, description="Minimum reference range for RBC")
    rbcMax: Optional[float] = Field(None, description="Maximum reference range for RBC")
    mcv: Optional[float] = Field(None, description="Mean corpuscular volume (fL)")
    mcvMin: Optional[float] = Field(None, description="Minimum reference range for MCV")
    mcvMax: Optional[float] = Field(None, description="Maximum reference range for MCV")
    mch: Optional[float] = Field(None, description="Mean corpuscular hemoglobin (pg)")
    mchMin: Optional[float] = Field(None, description="Minimum reference range for MCH")
    mchMax: Optional[float] = Field(None, description="Maximum reference range for MCH")


class PatientData(BaseModel):
    """
    Schema for patient data.
    """
    patientId: str = Field(..., description="Unique identifier for the patient")
    age: Optional[int] = Field(None, description="Patient age in years")
    gender: Optional[str] = Field(None, description="Patient gender")
    tests: List[TestResult] = Field(..., description="List of blood test results")


class PredictionRequest(BaseModel):
    """
    Schema for prediction request.
    """
    patient: PatientData = Field(..., description="Patient data")


class FeatureContribution(BaseModel):
    """
    Schema for feature contribution to prediction.
    """
    feature: str = Field(..., description="Feature name")
    value: float = Field(..., description="Feature value")
    contribution: float = Field(..., description="Contribution to prediction")
    is_abnormal: bool = Field(..., description="Whether the feature is abnormal")


class PredictionResponse(BaseModel):
    """
    Schema for prediction response.
    """
    patientId: str = Field(..., description="Unique identifier for the patient")
    prediction: str = Field(..., description="Prediction label (NORMAL or ABNORMAL)")
    probability: float = Field(..., description="Probability of abnormality (0-1)")
    confidence: float = Field(..., description="Confidence score (0-1)")
    risk_score: int = Field(..., description="Risk score (1-10)")
    top_contributors: List[FeatureContribution] = Field(..., description="Top contributing features")
    model_version: str = Field(..., description="Model version used for prediction")
    timestamp: str = Field(..., description="Timestamp of prediction (ISO format)")


class BatchPredictionRequest(BaseModel):
    """
    Schema for batch prediction request.
    """
    patients: List[PatientData] = Field(..., description="List of patient data")


class BatchPredictionResponse(BaseModel):
    """
    Schema for batch prediction response.
    """
    predictions: List[PredictionResponse] = Field(..., description="List of predictions")
    model_version: str = Field(..., description="Model version used for predictions")
    timestamp: str = Field(..., description="Timestamp of predictions (ISO format)")


class ModelInfo(BaseModel):
    """
    Schema for model information.
    """
    name: str = Field(..., description="Model name")
    version: str = Field(..., description="Model version")
    created_at: str = Field(..., description="Model creation timestamp (ISO format)")
    metrics: Dict[str, Any] = Field(..., description="Model performance metrics")
    feature_importance: Optional[Dict[str, float]] = Field(None, description="Feature importance scores")


class HealthCheckResponse(BaseModel):
    """
    Schema for health check response.
    """
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether the model is loaded")
    model_version: Optional[str] = Field(None, description="Model version if loaded")