# Model Inference API

This module provides a REST API for serving predictions from the trained abnormal blood test detection model for the Active Patient Follow-Up Alert Dashboard.

## Overview

The inference API consists of three main components:

1. **API Server** (`app.py`): FastAPI server that handles HTTP requests
2. **Model Handler** (`model_handler.py`): Loads and uses the trained model
3. **API Schemas** (`schemas.py`): Defines request and response data structures

## Prerequisites

Before running the inference API, ensure you have:

1. Trained and validated a model using the training module:
   ```bash
   python -m src.training.train
   python -m src.validation.validate
   ```

2. Installed the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the API Server

To start the API server with default settings:

```bash
python -m src.inference.app
```

This will:
1. Load the latest trained model from the `./model` directory
2. Start a FastAPI server on port 8000
3. Expose endpoints for making predictions

You can then access the API documentation at http://localhost:8000/docs

### API Endpoints

The API provides the following endpoints:

- **GET /** - Root endpoint with basic information
- **GET /health** - Health check endpoint
- **GET /model-info** - Information about the loaded model
- **POST /predict** - Make a prediction for a single patient
- **POST /batch-predict** - Make predictions for multiple patients
- **POST /reload-model** - Reload the model from disk
- **GET /example-request** - Get an example prediction request

### Making Predictions

#### Single Patient Prediction

To make a prediction for a single patient, send a POST request to the `/predict` endpoint:

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

#### Batch Prediction

To make predictions for multiple patients at once, use the `/batch-predict` endpoint:

1. Create a JSON file with multiple patient records:

```json
{
  "patients": [
    {
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
    },
    {
      "patientId": "P-789012",
      "age": 65,
      "gender": "male",
      "tests": [
        {
          "testId": "CBC-456",
          "testDate": "2025-03-16T14:45:00Z",
          "hemoglobin": 18.5,
          "hemoglobinMin": 13.5,
          "hemoglobinMax": 17.5,
          "wbc": 12.0,
          "wbcMin": 4.5,
          "wbcMax": 11.0,
          "platelets": 140,
          "plateletsMin": 150,
          "plateletsMax": 450,
          "neutrophils": 8.0,
          "neutrophilsMin": 2.0,
          "neutrophilsMax": 7.5,
          "lymphocytes": 3.5,
          "lymphocytesMin": 1.0,
          "lymphocytesMax": 4.5,
          "rbc": 6.0,
          "rbcMin": 4.5,
          "rbcMax": 5.9,
          "mcv": 85,
          "mcvMin": 80,
          "mcvMax": 100,
          "mch": 28,
          "mchMin": 27,
          "mchMax": 33
        }
      ]
    }
  ]
}
```

2. Send the batch request:

```bash
curl -X POST -H "Content-Type: application/json" -d @batch_request.json http://localhost:8000/batch-predict
```

### Response Format

The API returns predictions in the following format:

```json
{
  "patientId": "P-123456",
  "prediction": "ABNORMAL",
  "probability": 0.85,
  "confidence": 0.7,
  "risk_score": 9,
  "top_contributors": [
    {
      "feature": "hemoglobin",
      "value": 12.5,
      "contribution": 0.35,
      "is_abnormal": false
    },
    ...
  ],
  "model_version": "20250315_123456",
  "timestamp": "2025-03-17T10:30:00Z"
}
```

## Configuration

The API can be configured using environment variables:

- `PORT` - Port to run the API server on (default: 8000)
- `MODEL_DIR` - Directory containing model files (default: ./model)

## Integration with Frontend

The API is designed to be easily integrated with the React frontend:

```typescript
// Example frontend integration
async function getPrediction(patientId: string, testData: any) {
  const response = await fetch('http://localhost:8000/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      patient: {
        patientId,
        ...testData
      }
    })
  });
  
  return await response.json();
}
```

## Deployment

For production deployment, consider:

1. Using a production ASGI server like Gunicorn
2. Setting up proper authentication and HTTPS
3. Configuring CORS for your specific frontend domain
4. Implementing rate limiting and request validation

Example production startup:

```bash
gunicorn src.inference.app:app -k uvicorn.workers.UvicornWorker -w 4 --bind 0.0.0.0:8000