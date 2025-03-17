# Project Intelligence: Active Patient Follow-Up Alert Dashboard

## Critical Implementation Paths

1. **Data Flow Architecture**
   - The system follows a clear data flow: Simulation → Training → Validation → Inference → UI → Feedback
   - Each component has well-defined inputs and outputs
   - Type definitions in `src/shared/types.ts` are the source of truth for data structures

2. **Model Validation Requirements**
   - Models MUST pass all validation checks before deployment
   - Clinical safety metrics (sensitivity ≥ 0.95) take precedence over other metrics
   - Fairness across demographic groups is a non-negotiable requirement

3. **UI Component Structure**
   - React components follow a clear hierarchy with pages at the top level
   - State management uses Effector with stores defined in `src/ui/stores/`
   - Form validation happens at the store level, not in components

4. **API Integration Pattern**
   - Frontend communicates with backend via the API client in `src/ui/api/client.ts`
   - All API requests include error handling and loading states
   - Response types match the schemas defined in `src/inference/schemas.py`

## User Preferences and Workflow

1. **Development Workflow**
   - Start the API and UI separately during development for faster iteration
   - Use the demo data loading buttons for quick testing
   - Check validation reports after model training to ensure requirements are met

2. **Code Organization Preferences**
   - Keep related functionality in the same directory
   - Use clear, descriptive naming for files and functions
   - Document complex algorithms and business logic

3. **Testing Strategy**
   - Focus on integration tests for critical paths
   - Use synthetic data for comprehensive test coverage
   - Validate model performance on edge cases

## Project-Specific Patterns

1. **Feature Engineering Pattern**
   - Extract basic features directly from test values
   - Create derived features based on reference ranges
   - Include temporal features when multiple tests are available
   - Select features based on clinical relevance and statistical significance

2. **Validation Reporting Pattern**
   - Generate comprehensive validation reports with all metrics
   - Include visualizations for key performance indicators
   - Provide clear pass/fail indicators for each validation check
   - Document model cards for transparency

3. **Active Learning Pattern**
   - Collect binary feedback (correct/incorrect) from users
   - Store feedback with prediction details for context
   - Periodically retrain models with accumulated feedback
   - Track performance improvements over time

4. **Error Handling Pattern**
   - Use try/catch blocks for all external operations
   - Provide user-friendly error messages in the UI
   - Log detailed error information for debugging
   - Implement graceful degradation when components fail

## Known Challenges

1. **Synthetic Data Limitations**
   - Synthetic data may not capture all real-world patterns
   - Reference ranges vary across different labs and populations
   - Some abnormalities are only apparent in the context of patient history

2. **Model Generalization**
   - Models trained on synthetic data may not generalize to real clinical data
   - Performance metrics should be interpreted with caution
   - Regular retraining with real data (when available) is recommended

3. **Clinical Context**
   - The system does not have access to complete patient history
   - Some abnormalities require clinical context beyond lab values
   - The system should be used as a decision support tool, not a replacement for clinical judgment

4. **UI Complexity**
   - The form becomes unwieldy with many test fields
   - Mobile responsiveness is challenging with complex forms
   - Balance between comprehensive data collection and usability

## Evolution of Project Decisions

1. **Model Selection Criteria**
   - Initially focused on overall accuracy
   - Evolved to prioritize sensitivity (minimize false negatives)
   - Now using a combined metric that balances sensitivity and temporal stability

2. **Validation Approach**
   - Started with basic train/test split
   - Added cross-validation for more robust evaluation
   - Now includes temporal validation and fairness metrics

3. **UI Design**
   - Initially focused on functionality over aesthetics
   - Evolved to include more intuitive data entry
   - Now emphasizing clinical workflow integration

4. **Feedback Mechanism**
   - Started with simple binary feedback
   - Planning to evolve to more detailed feedback with reason codes
   - Future direction includes implicit feedback based on user actions

## Tool Usage Patterns

1. **Data Generation**
   ```bash
   # Generate 500 patients with 30% abnormal results
   npx ts-node src/simulateData/cli.ts --patients 500 --abnormal 0.3
   ```

2. **Model Training**
   ```bash
   # Train model with default settings
   python -m src.training.train
   
   # Train model with custom settings
   python -m src.training.train --data-dir ./custom_data --random-state 123
   ```

3. **Running the Application**
   ```bash
   # Start complete application
   ./run_app.sh
   
   # Start API only
   python -m src.inference.app
   
   # Start UI only
   cd src/ui && npm run dev