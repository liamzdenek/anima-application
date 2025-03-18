"""
FastAPI server for the Active Patient Follow-Up Alert Dashboard.

This module provides a REST API for making predictions using the trained model.
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import local modules using absolute imports for Lambda
import schemas
import model_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Abnormal Lab Results API",
    description="API for detecting abnormal lab results and prioritizing patient follow-ups",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize the API on startup.
    """
    logger.info("Starting Abnormal Lab Results API")
    
    # Check if model is loaded
    if not model_handler.model_handler.is_model_loaded():
        logger.warning("Model not loaded. API will return errors for prediction endpoints.")
    else:
        model_info = model_handler.model_handler.get_model_info()
        logger.info(f"Model loaded: {model_info.get('name')} v{model_info.get('version')}")


@app.get("/", tags=["General"])
async def root():
    """
    Root endpoint.
    """
    return {
        "message": "Abnormal Lab Results API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=schemas.HealthCheckResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint.
    """
    is_loaded = model_handler.model_handler.is_model_loaded()
    model_version = None
    
    if is_loaded:
        model_info = model_handler.model_handler.get_model_info()
        model_version = model_info.get('version')
    
    return {
        "status": "healthy",
        "model_loaded": is_loaded,
        "model_version": model_version
    }


@app.get("/model-info", response_model=schemas.ModelInfo, tags=["Model"])
async def get_model_info():
    """
    Get information about the loaded model.
    """
    if not model_handler.model_handler.is_model_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    model_info = model_handler.model_handler.get_model_info()
    
    return {
        "name": model_info.get('name', 'unknown'),
        "version": model_info.get('version', 'unknown'),
        "created_at": model_info.get('created_at', 'unknown'),
        "metrics": model_info.get('metrics', {}),
        "feature_importance": model_info.get('feature_importance', {})
    }


@app.post("/predict", response_model=schemas.PredictionResponse, tags=["Prediction"])
async def predict(request: schemas.PredictionRequest):
    """
    Make a prediction for a single patient.
    """
    if not model_handler.model_handler.is_model_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert request to dictionary
        patient_data = request.patient.dict()
        
        # Make prediction
        result = model_handler.model_handler.predict(patient_data)
        
        # Convert to response model
        response = schemas.PredictionResponse(
            patientId=result['patientId'],
            prediction=result['prediction'],
            probability=result['probability'],
            confidence=result['confidence'],
            risk_score=result['risk_score'],
            top_contributors=result['top_contributors'],
            model_version=result['model_version'],
            timestamp=result['timestamp']
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch-predict", response_model=schemas.BatchPredictionResponse, tags=["Prediction"])
async def batch_predict(request: schemas.BatchPredictionRequest):
    """
    Make predictions for multiple patients.
    """
    if not model_handler.model_handler.is_model_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert request to list of dictionaries
        patients_data = [patient.dict() for patient in request.patients]
        
        # Make predictions
        results = model_handler.model_handler.batch_predict(patients_data)
        
        # Convert to response model
        predictions = []
        for result in results:
            if 'error' in result:
                # Skip errors
                continue
            
            prediction = schemas.PredictionResponse(
                patientId=result['patientId'],
                prediction=result['prediction'],
                probability=result['probability'],
                confidence=result['confidence'],
                risk_score=result['risk_score'],
                top_contributors=result['top_contributors'],
                model_version=result['model_version'],
                timestamp=result['timestamp']
            )
            predictions.append(prediction)
        
        response = schemas.BatchPredictionResponse(
            predictions=predictions,
            model_version=model_handler.model_handler.get_model_info().get('version', 'unknown'),
            timestamp=datetime.now().isoformat()
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error making batch predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reload-model", tags=["Model"])
async def reload_model():
    """
    Reload the model from disk.
    """
    success = model_handler.model_handler.load_model()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reload model")
    
    return {
        "message": "Model reloaded successfully",
        "model_info": model_handler.model_handler.get_model_info()
    }


@app.get("/example-request", tags=["Development"])
async def get_example_request():
    """
    Get an example prediction request.
    """
    example = {
        "patient": {
            "patientId": "P-123456",
            "age": 45,
            "gender": "female",
            "tests": [
                {
                    "testId": "CBC-123",
                    "testDate": "2025-03-15T10:30:00Z",
                    "hemoglobin": 12.5,
                    "hemoglobinMin": 12.0,
                    "hemoglobinMax": 16.0,
                    "wbc": 7.5,
                    "wbcMin": 4.5,
                    "wbcMax": 11.0,
                    "platelets": 250,
                    "plateletsMin": 150,
                    "plateletsMax": 450,
                    "neutrophils": 4.2,
                    "neutrophilsMin": 2.0,
                    "neutrophilsMax": 7.5,
                    "lymphocytes": 2.1,
                    "lymphocytesMin": 1.0,
                    "lymphocytesMax": 4.5,
                    "rbc": 4.7,
                    "rbcMin": 4.0,
                    "rbcMax": 5.5,
                    "mcv": 90,
                    "mcvMin": 80,
                    "mcvMax": 100,
                    "mch": 30,
                    "mchMin": 27,
                    "mchMax": 33
                }
            ]
        }
    }
    
    return example


def start():
    """
    Start the FastAPI server.
    """
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Start server
    uvicorn.run("app_lambda:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    # Start the server
    start()