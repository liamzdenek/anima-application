# Model Validation Module

This module handles validating trained machine learning models for the Active Patient Follow-Up Alert Dashboard to ensure they meet clinical requirements and are not overfit.

## Overview

The validation module consists of three main components:

1. **Validation Core** (`validate.py`): Runs comprehensive validation checks on trained models
2. **Clinical Metrics** (`metrics.py`): Calculates clinical safety and fairness metrics
3. **Report Generation** (`reports.py`): Generates validation reports and model cards

## Prerequisites

Before running the validation module, ensure you have:

1. Trained a model using the training module:
   ```bash
   python -m src.training.train
   ```

2. Installed the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Validation

To validate a model with default settings:

```bash
python -m src.validation.validate
```

This will:
1. Load the latest trained model from the `./model` directory
2. Run a comprehensive suite of validation checks
3. Save validation results to the `./reports/metrics` directory

### Generating Reports

To generate a comprehensive validation report:

```bash
python -m src.validation.reports
```

This will:
1. Load the latest validation results
2. Generate a markdown report in the `./reports/clinical` directory
3. Create a model card for documentation

### Validation Checks

The validation module performs the following checks:

#### 1. Overfitting Detection
- Compares training and test performance
- Analyzes learning curves
- Checks for feature importance stability

#### 2. Temporal Validation
- Trains on older data and tests on newer data
- Ensures model performance is stable over time

#### 3. Clinical Safety Metrics
- Calculates sensitivity, specificity, PPV, and NPV
- Optimizes decision threshold for clinical use
- Analyzes false negatives (missed abnormal cases)

#### 4. Fairness Analysis
- Checks for demographic parity across age and gender groups
- Ensures equal opportunity across demographic groups
- Identifies potential biases in the model

## Validation Requirements

For a model to pass validation, it must meet the following requirements:

1. **No significant overfitting**: Training-test performance gap below threshold
2. **Temporal stability**: Good performance on newer data
3. **Clinical safety**: Sensitivity ≥ 0.95, NPV ≥ 0.9
4. **Fairness**: No significant disparities across demographic groups

## Example

```bash
# Train model
python -m src.training.train

# Validate model
python -m src.validation.validate

# Generate validation report
python -m src.validation.reports
```

## Output

The validation process produces the following outputs:

1. **Validation Results**: JSON file with detailed validation metrics
2. **Validation Report**: Markdown report with analysis and recommendations
3. **Model Card**: Documentation of model capabilities and limitations

## Next Steps

After successful validation, you can:

1. Deploy the model using the inference API
2. Integrate the model with the frontend dashboard
3. Monitor model performance in production