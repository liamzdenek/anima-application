# Blood Test Data Simulator

This module generates synthetic blood test data for the Active Patient Follow-Up Alert Dashboard project. The generated data is designed to be used for training and testing the abnormality detection and risk scoring algorithms.

## Overview

The data simulator creates a dataset of patients with realistic blood test results over time. Some patients will have abnormal test results that would require follow-up in a clinical setting. The data is labeled for machine learning purposes, with each patient marked as either "NORMAL" or "ABNORMAL" along with a confidence score.

## Data Generation Process

1. **Patient Generation**: Creates synthetic patient profiles with realistic demographics (age, gender) and medical history.

2. **Blood Test Generation**: For each patient, generates a series of blood tests over a configurable time period (default: 6 months).
   - Tests include common Complete Blood Count (CBC) metrics
   - Reference ranges are adjusted based on patient demographics
   - Some patients will have abnormal trends in their test results

3. **Abnormality Detection**: Each test result is analyzed against reference ranges to flag abnormal values.
   - Individual metrics are marked as normal or abnormal
   - An overall abnormality flag is set based on multiple factors
   - A confidence score (0-1) is calculated for the abnormality prediction

4. **Data Labeling**: Each patient is labeled as "NORMAL" or "ABNORMAL" based on their test history.
   - Labels include a confidence score for use in ML training
   - This simulates the ground truth for supervised learning

## Generated Data Structure

The data is output as JSON files in the `./data/` directory:

- One file per patient: `patient-{ID}.json`
- A summary file: `summary.json` with dataset statistics

Each patient file contains:
- Patient demographics
- Complete test history with all metrics
- Reference ranges for each test
- Abnormality flags for each metric
- Overall patient label (NORMAL/ABNORMAL)

## Usage

### Basic Usage

To generate data with default settings:

```bash
npx ts-node src/simulateData/index.ts
```

### CLI Options

For more control, use the CLI script:

```bash
npx ts-node src/simulateData/cli.ts [options]
```

Options:
- `--patients <number>`: Number of patients to generate (default: 350)
- `--min-tests <number>`: Minimum tests per patient (default: 3)
- `--max-tests <number>`: Maximum tests per patient (default: 8)
- `--months <number>`: Time range in months (default: 6)
- `--abnormal <number>`: Probability of abnormal results (0-1, default: 0.3)
- `--output <path>`: Output directory (default: ./data)

### Programmatic Usage

You can also import and use the generator in your code:

```typescript
import { generateDataset } from './simulateData';

// Set environment variables to configure the generator
process.env.PATIENT_COUNT = '500';
process.env.ABNORMAL_PROBABILITY = '0.4';

// Generate the dataset
generateDataset();
```

## Data for ML Training

The generated data is structured to be easily used for training machine learning models:

1. **Features**: Blood test metrics (hemoglobin, WBC, etc.)
2. **Labels**: NORMAL/ABNORMAL classification with confidence scores
3. **Time Series**: Multiple tests per patient allow for time-series analysis
4. **Balanced Classes**: Configurable abnormal probability ensures balanced training data

For Python-based ML training, the JSON files can be easily loaded and processed using pandas:

```python
import pandas as pd
import json
import glob

# Load all patient files
patient_files = glob.glob('data/patient-*.json')
patients_data = []

for file in patient_files:
    with open(file, 'r') as f:
        patients_data.append(json.load(f))

# Create features and labels
features = []
labels = []

for patient in patients_data:
    # Extract features from the most recent test
    latest_test = sorted(patient['tests'], key=lambda x: x['testDate'])[-1]
    
    # Create feature vector
    feature_vector = [
        latest_test['hemoglobin'],
        latest_test['wbc'],
        latest_test['platelets'],
        # ... other metrics
    ]
    
    features.append(feature_vector)
    labels.append(1 if patient['label'] == 'ABNORMAL' else 0)

# Convert to numpy arrays for ML
import numpy as np
X = np.array(features)
y = np.array(labels)

# Now ready for training
```

## Future Enhancements

Potential improvements to the data simulator:

1. Add more specific disease patterns (e.g., anemia, infection)
2. Include more lab test types beyond CBC
3. Generate correlated abnormalities that would appear in specific conditions
4. Add medication effects on test results
5. Include more detailed patient demographics and risk factors