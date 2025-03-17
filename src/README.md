# Active Patient Follow-Up Alert Dashboard - ML Component

This directory contains the machine learning components for the Active Patient Follow-Up Alert Dashboard, which detects abnormal blood test results and prioritizes patients for clinical follow-up.

## Project Structure

The ML component is organized into the following modules:

```
src/
├── training/           # Model training
│   ├── preprocess.py   # Data preprocessing
│   ├── features.py     # Feature engineering
│   └── train.py        # Model training and evaluation
├── validation/         # Model validation
│   ├── validate.py     # Validation checks
│   ├── metrics.py      # Clinical metrics
│   └── reports.py      # Report generation
├── inference/          # Inference API
│   ├── app.py          # FastAPI server
│   ├── model_handler.py # Model loading and prediction
│   └── schemas.py      # API schemas
├── shared/             # Shared utilities
│   └── types.ts        # TypeScript type definitions
└── simulateData/       # Data simulation (TypeScript)
    ├── index.ts        # Main data generator
    └── cli.ts          # Command-line interface
```

## Workflow

The ML system follows this workflow:

1. **Data Generation**: Generate synthetic blood test data using the TypeScript simulator
2. **Model Training**: Train machine learning models to detect abnormal results
3. **Model Validation**: Validate models for clinical safety and fairness
4. **Inference API**: Serve predictions via a REST API for the frontend

## Getting Started

### Prerequisites

- Node.js and npm (for data simulation)
- Python 3.8+ (for ML components)
- Required Python packages: `pip install -r requirements.txt`

### Step 1: Generate Data

```bash
# Generate synthetic patient data
npx ts-node src/simulateData/cli.ts --patients 1000
```

### Step 2: Train Model

```bash
# Train the model
python -m src.training.train
```

### Step 3: Validate Model

```bash
# Validate the model
python -m src.validation.validate

# Generate validation report
python -m src.validation.reports
```

### Step 4: Start Inference API

```bash
# Start the API server
python -m src.inference.app
```

## Integration with Frontend

The inference API provides endpoints that can be called from the React frontend:

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

## Model Details

The system trains multiple model types:

- **Logistic Regression**: Provides interpretable results with feature coefficients
- **Random Forest**: Offers robust performance with feature importance

Models are evaluated based on:

- **ROC AUC**: Overall discriminative ability
- **Sensitivity**: Ability to detect truly abnormal cases (critical for clinical safety)
- **Specificity**: Ability to correctly identify normal cases
- **Precision**: Proportion of predicted abnormal cases that are truly abnormal

## Active Learning Loop

The system supports an active learning loop where clinician feedback can be used to improve the model:

1. Model makes predictions on new patient data
2. Clinicians provide feedback on predictions (correct/incorrect)
3. Feedback is stored for future model retraining
4. Model is periodically retrained with new feedback

## Directory Details

For more information about each component, see the README files in the respective directories:

- [Training Module](./training/README.md)
- [Validation Module](./validation/README.md)
- [Inference API](./inference/README.md)
- [Data Simulator](./simulateData/README.md)