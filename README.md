# Active Patient Follow-Up Alert Dashboard

A lightweight web application that simulates an automated alert system for abnormal lab results. The dashboard displays a list of patients flagged for follow-up, with risk scores derived from a machine learning model that can be refined through user feedback—implementing an active learning loop.

## Project Overview

The Active Patient Follow-Up Alert Dashboard is designed to help healthcare providers identify and prioritize patients with abnormal lab results that require clinical follow-up. The system uses machine learning to analyze blood test results, assign risk scores, and provide explanations for its predictions.

## Features

- Abnormal lab result detection
- Risk score calculation
- Explanation of contributing factors
- Active learning through user feedback
- Synthetic data generation for testing
- AWS deployment using CDK

## Getting Started

### Prerequisites

- Node.js 16+ with npm
- Python 3.8+ with pip
- Git
- AWS CLI (for deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd anima-application
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Node.js dependencies:
   ```bash
   npm install
   ```

4. Install UI dependencies:
   ```bash
   cd src/ui
   npm install
   cd ../..
   ```

### Running the Application Locally

1. Generate simulated data:
   ```bash
   npx ts-node src/simulateData/cli.ts --patients 500
   ```

2. Train and validate the model:
   ```bash
   python -m src.training.train
   python -m src.validation.validate
   ```

3. Start the complete application (API + UI):
   ```bash
   ./run_app.sh
   ```

   Or run components separately:

   Start only the API:
   ```bash
   python -m src.inference.app
   ```

   Start only the UI:
   ```bash
   cd src/ui
   npm run dev
   ```

### Deploying to AWS

The application can be deployed to AWS using the AWS Cloud Development Kit (CDK):

1. Configure AWS CLI:
   ```bash
   aws configure
   ```

2. Deploy the application:
   ```bash
   ./deploy.sh
   ```

This will:
- Deploy the backend to AWS Lambda and API Gateway
- Deploy the frontend to S3 and CloudFront
- Output the URLs for accessing the deployed application

## Project Structure

```
.
├── cdk/                  # AWS CDK infrastructure code
├── data/                 # Simulated patient data
├── memory-bank/          # Project documentation
├── model/                # Trained model artifacts
├── reports/              # Validation reports
├── src/
│   ├── inference/        # Inference API (FastAPI)
│   ├── shared/           # Shared types and utilities
│   ├── simulateData/     # Data simulation tools
│   ├── training/         # Model training code
│   ├── ui/               # React user interface
│   └── validation/       # Model validation tools
├── deploy.sh             # Script to deploy to AWS
├── run_app.sh            # Script to run the complete application
├── run_ml_pipeline.py    # Script to run the ML pipeline
└── run_ui.sh             # Script to run the UI only
```

## AWS Architecture

The application is deployed to AWS with the following architecture:

- **Frontend**: Static assets hosted in S3 and served through CloudFront
- **Backend**: FastAPI application running in AWS Lambda, exposed through API Gateway
- **Infrastructure**: Defined using AWS CDK in TypeScript

## License

This project is licensed under the MIT License - see the LICENSE file for details.