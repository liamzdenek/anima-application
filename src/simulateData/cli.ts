#!/usr/bin/env node
/**
 * Command-line interface for blood test data generation
 * 
 * This script provides a CLI for generating synthetic blood test data
 * with customizable parameters.
 * 
 * Usage:
 *   npx ts-node src/simulateData/cli.ts [options]
 * 
 * Options:
 *   --patients <number>     Number of patients to generate (default: 100)
 *   --min-tests <number>    Minimum tests per patient (default: 3)
 *   --max-tests <number>    Maximum tests per patient (default: 8)
 *   --months <number>       Time range in months (default: 6)
 *   --abnormal <number>     Probability of abnormal results (0-1, default: 0.3)
 *   --output <path>         Output directory (default: ./data)
 *   --help                  Show help
 */

import * as fs from 'fs';
import * as path from 'path';
import { generateDataset } from './index';

// Parse command line arguments
function parseArgs(): Record<string, any> {
  const args: Record<string, any> = {
    patients: 350,
    minTests: 3,
    maxTests: 8,
    months: 6,
    abnormal: 0.3,
    output: path.resolve(process.cwd(), 'data'),
    help: false
  };
  
  const argv = process.argv.slice(2);
  
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    
    switch (arg) {
      case '--patients':
        args.patients = parseInt(argv[++i], 10);
        break;
      case '--min-tests':
        args.minTests = parseInt(argv[++i], 10);
        break;
      case '--max-tests':
        args.maxTests = parseInt(argv[++i], 10);
        break;
      case '--months':
        args.months = parseInt(argv[++i], 10);
        break;
      case '--abnormal':
        args.abnormal = parseFloat(argv[++i]);
        break;
      case '--output':
        args.output = path.resolve(process.cwd(), argv[++i]);
        break;
      case '--help':
        args.help = true;
        break;
      default:
        console.warn(`Unknown argument: ${arg}`);
    }
  }
  
  return args;
}

// Display help message
function showHelp(): void {
  console.log(`
Blood Test Data Generator

Generate synthetic blood test data for the Active Patient Follow-Up Alert Dashboard.

Usage:
  npx ts-node src/simulateData/cli.ts [options]

Options:
  --patients <number>     Number of patients to generate (default: 350)
  --min-tests <number>    Minimum tests per patient (default: 3)
  --max-tests <number>    Maximum tests per patient (default: 8)
  --months <number>       Time range in months (default: 6)
  --abnormal <number>     Probability of abnormal results (0-1, default: 0.3)
  --output <path>         Output directory (default: ./data)
  --help                  Show this help message
  `);
}

// Validate arguments
function validateArgs(args: Record<string, any>): boolean {
  if (args.patients < 1) {
    console.error('Error: Number of patients must be at least 1');
    return false;
  }
  
  if (args.minTests < 1) {
    console.error('Error: Minimum tests must be at least 1');
    return false;
  }
  
  if (args.maxTests < args.minTests) {
    console.error('Error: Maximum tests must be greater than or equal to minimum tests');
    return false;
  }
  
  if (args.months < 1) {
    console.error('Error: Time range must be at least 1 month');
    return false;
  }
  
  if (args.abnormal < 0 || args.abnormal > 1) {
    console.error('Error: Abnormal probability must be between 0 and 1');
    return false;
  }
  
  return true;
}

// Main function
function main(): void {
  const args = parseArgs();
  
  if (args.help) {
    showHelp();
    return;
  }
  
  if (!validateArgs(args)) {
    process.exit(1);
  }
  
  // Override default configuration
  process.env.PATIENT_COUNT = args.patients.toString();
  process.env.MIN_TESTS = args.minTests.toString();
  process.env.MAX_TESTS = args.maxTests.toString();
  process.env.TIME_RANGE = args.months.toString();
  process.env.ABNORMAL_PROBABILITY = args.abnormal.toString();
  process.env.OUTPUT_DIR = args.output;
  
  // Run data generation
  generateDataset();
}

// Run the CLI
main();