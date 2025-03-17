#!/usr/bin/env python
"""
Run the complete ML pipeline for the Active Patient Follow-Up Alert Dashboard.

This script runs the entire ML pipeline:
1. Generate synthetic data (if needed)
2. Train the model
3. Validate the model
4. Generate validation reports
5. Start the inference API

Usage:
    python run_ml_pipeline.py [--skip-data-gen] [--skip-training] [--skip-validation] [--skip-api]
"""

import os
import sys
import argparse
import subprocess
import time
from datetime import datetime


def log(message):
    """Print a timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_command(command, description):
    """Run a shell command and log the output."""
    log(f"Starting: {description}")
    log(f"Command: {command}")
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line.strip())
        
        process.wait()
        
        if process.returncode == 0:
            log(f"Completed: {description}")
            return True
        else:
            log(f"Failed: {description} (Exit code: {process.returncode})")
            return False
    
    except Exception as e:
        log(f"Error: {e}")
        return False


def generate_data(patient_count=1000, abnormal_prob=0.3):
    """Generate synthetic patient data."""
    command = f"npx ts-node src/simulateData/cli.ts --patients {patient_count} --abnormal {abnormal_prob}"
    return run_command(command, "Data Generation")


def train_model():
    """Train the machine learning model."""
    command = "python -m src.training.train"
    return run_command(command, "Model Training")


def validate_model():
    """Validate the trained model."""
    command = "python -m src.validation.validate"
    return run_command(command, "Model Validation")


def generate_reports():
    """Generate validation reports."""
    # Import the reports module and generate reports
    try:
        log("Starting: Report Generation")
        from src.validation.reports import generate_validation_report, generate_model_card
        
        # Load the latest validation results
        import glob
        import json
        
        reports_dir = './reports/metrics'
        validation_files = glob.glob(os.path.join(reports_dir, 'validation_*.json'))
        
        if not validation_files:
            log("No validation results found")
            return False
        
        # Get the most recent validation file
        latest_file = max(validation_files, key=os.path.getctime)
        
        with open(latest_file, 'r') as f:
            validation_results = json.load(f)
        
        # Generate reports
        report_path = generate_validation_report(validation_results)
        card_path = generate_model_card(validation_results)
        
        log(f"Generated validation report: {report_path}")
        log(f"Generated model card: {card_path}")
        log("Completed: Report Generation")
        return True
    
    except Exception as e:
        log(f"Error generating reports: {e}")
        return False


def start_api():
    """Start the inference API."""
    command = "python -m src.inference.app"
    return run_command(command, "Inference API")


def main():
    """Run the complete ML pipeline."""
    parser = argparse.ArgumentParser(description="Run the ML pipeline")
    parser.add_argument("--skip-data-gen", action="store_true", help="Skip data generation")
    parser.add_argument("--skip-training", action="store_true", help="Skip model training")
    parser.add_argument("--skip-validation", action="store_true", help="Skip model validation")
    parser.add_argument("--skip-reports", action="store_true", help="Skip report generation")
    parser.add_argument("--skip-api", action="store_true", help="Skip starting the API")
    parser.add_argument("--patient-count", type=int, default=1000, help="Number of patients to generate")
    parser.add_argument("--abnormal-prob", type=float, default=0.3, help="Probability of abnormal results")
    
    args = parser.parse_args()
    
    log("Starting ML Pipeline")
    
    # Create necessary directories
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./model", exist_ok=True)
    os.makedirs("./reports/metrics", exist_ok=True)
    os.makedirs("./reports/clinical", exist_ok=True)
    
    # Run pipeline steps
    success = True
    
    if not args.skip_data_gen:
        success = generate_data(args.patient_count, args.abnormal_prob)
        if not success:
            log("Data generation failed, but continuing with pipeline")
    
    if success and not args.skip_training:
        success = train_model()
        if not success:
            log("Model training failed")
            return 1
    
    if success and not args.skip_validation:
        success = validate_model()
        if not success:
            log("Model validation failed")
            return 1
    
    if success and not args.skip_reports:
        success = generate_reports()
        if not success:
            log("Report generation failed")
            # Continue anyway, this is not critical
    
    if success and not args.skip_api:
        success = start_api()
        if not success:
            log("API startup failed")
            return 1
    
    log("ML Pipeline completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())