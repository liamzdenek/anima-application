# Model Training Module

This module handles training machine learning models to detect abnormal blood test results for the Active Patient Follow-Up Alert Dashboard.

## Overview

The training module consists of three main components:

1. **Data Preprocessing** (`preprocess.py`): Loads and preprocesses patient data from JSON files
2. **Feature Engineering** (`features.py`): Creates features from the preprocessed data
3. **Model Training** (`train.py`): Trains and evaluates machine learning models

## Prerequisites

Before running the training module, ensure you have:

1. Generated synthetic patient data using the data simulator:
   ```bash
   npx ts-node src/simulateData/cli.ts --patients 500
   ```

2. Installed the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Training

To train a model with default settings:

```bash
python -m src.training.train
```

This will:
1. Load patient data from the `./data` directory
2. Preprocess the data and engineer features
3. Train multiple model types (Logistic Regression and Random Forest)
4. Evaluate models and select the best one
5. Save the model to the `./model` directory

### Advanced Options

You can customize the training process by modifying parameters in `train.py`:

```python
# Example: Custom training with specific parameters
results = train_model(
    data_dir='./custom_data',
    model_dir='./custom_model',
    random_state=123
)
```

## Model Validation

After training, you should validate the model using the validation module:

```bash
python -m src.validation.validate
```

This will run a comprehensive validation suite to ensure the model:
- Is not overfit
- Performs well on temporal data
- Meets clinical safety requirements
- Is fair across demographic groups

## Output

The training process produces the following outputs:

1. **Trained Model**: Saved as a pickle file in the `./model` directory
2. **Model Metadata**: JSON file with model information and metrics
3. **Version Tracking**: A `version.txt` file indicating the current model version

## Example

```bash
# Generate data
npx ts-node src/simulateData/cli.ts --patients 1000 --abnormal 0.3

# Train model
python -m src.training.train

# Validate model
python -m src.validation.validate

# Generate validation report
python -m src.validation.reports
```

## Next Steps

After successful training and validation, you can:

1. Use the inference API to make predictions
2. Integrate the model with the frontend dashboard
3. Implement the feedback loop for active learning