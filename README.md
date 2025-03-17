# Active Patient Follow-Up Alert Dashboard

A system for detecting abnormal blood test results and alerting healthcare providers for timely patient follow-up.

## Project Overview

This project implements a machine learning-based system that analyzes blood test results to identify abnormal patterns and prioritize patient follow-ups. It consists of three main components:

1. **Training Module**: Python code for preprocessing data, engineering features, and training ML models
2. **Inference API**: FastAPI server for serving predictions from the trained model
3. **User Interface**: React application for RNs to enter test results and view predictions

## Directory Structure

```
.
├── data/                 # Simulated patient data
├── model/                # Trained model artifacts
├── reports/              # Validation reports
├── src/
│   ├── inference/        # Inference API (FastAPI)
│   ├── shared/           # Shared types and utilities
│   ├── simulateData/     # Data simulation tools
│   ├── training/         # Model training code
│   ├── ui/               # React user interface
│   └── validation/       # Model validation tools
├── run_app.sh            # Script to run the complete application
├── run_ml_pipeline.py    # Script to run the ML pipeline
└── run_ui.sh             # Script to run the UI only
```

## Getting Started

### Prerequisites

- Python 3.8+ with pip
- Node.js 16+ with npm

### Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Generate simulated data:
   ```bash
   npx ts-node src/simulateData/cli.ts --patients 500
   ```

3. Train the model:
   ```bash
   python -m src.training.train
   ```

4. Validate the model:
   ```bash
   python -m src.validation.validate
   ```

### Running the Application

To run the complete application (both API and UI):

```bash
./run_app.sh
```

To run only the UI:

```bash
./run_ui.sh
```

To run only the inference API:

```bash
python -m src.inference.app
```

## Components

### Training Module

The training module preprocesses patient data, engineers features, and trains machine learning models to detect abnormal blood test results. See [Training README](src/training/README.md) for details.

### Inference API

The inference API serves predictions from the trained model via a RESTful API. It provides endpoints for making predictions for individual patients or in batch. See [Inference README](src/inference/README.md) for details.

### User Interface

The UI allows Registered Nurses to enter blood test results and view model predictions. It displays the prediction result, confidence score, and validation metrics. See [UI README](src/ui/README.md) for details.

## License

This project is for demonstration purposes only.