# Technical Context: Active Patient Follow-Up Alert Dashboard

## Technology Stack

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Routing**: TanStack Router
- **State Management**: Effector (store/event/effect pattern)
- **Styling**: CSS Modules (.module.css)
- **HTTP Client**: Native Fetch API

### Backend
- **Framework**: FastAPI (Python)
- **API Documentation**: OpenAPI/Swagger (built into FastAPI)
- **Server**: Uvicorn ASGI server
- **Validation**: Pydantic schemas

### Machine Learning
- **Language**: Python 3.8+
- **Core Libraries**: scikit-learn, pandas, numpy
- **Visualization**: matplotlib, seaborn
- **Model Serialization**: pickle/joblib
- **Validation Tools**: Custom validation suite

### Data Simulation
- **Language**: TypeScript
- **Runtime**: Node.js
- **Output Format**: JSON

## Development Environment

### Prerequisites
- Node.js 16+ with npm
- Python 3.8+ with pip
- Git

### Project Setup
```bash
# Clone repository
git clone <repository-url>
cd anima-application

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Install UI dependencies
cd src/ui
npm install
cd ../..
```

### Running the Application
```bash
# Generate simulated data
npx ts-node src/simulateData/cli.ts --patients 500

# Train and validate the model
python -m src.training.train
python -m src.validation.validate

# Start the complete application (API + UI)
./run_app.sh

# Or run components separately:
# Start only the API
python -m src.inference.app

# Start only the UI
cd src/ui
npm run dev
```

## Code Organization

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

## Code Style and Conventions

### TypeScript/React
- **Component Files**: PascalCase.tsx with matching .module.css
- **Utility Functions**: camelCase.ts
- **File Imports**: Group by external → internal → relative
- **Effects/Stores**: Defined in effectors.ts files
- **TypeScript**: Strict mode enabled
- **React Components**: Functional components with hooks

### Python
- **Module Structure**: Clear separation of concerns
- **Documentation**: Docstrings for all functions and classes
- **Type Hints**: Used throughout the codebase
- **Error Handling**: Try/catch with proper logging
- **Testing**: Unit tests for critical components

## Dependencies

### Frontend Dependencies
- React 18+
- TanStack Router
- Effector/Effector-React
- TypeScript
- Vite

### Backend Dependencies
- FastAPI
- Uvicorn
- Pydantic
- Python-Multipart (for file uploads)
- CORS middleware

### Machine Learning Dependencies
- scikit-learn
- pandas
- numpy
- matplotlib
- seaborn
- joblib

## Technical Constraints

### Performance Requirements
- **API Response Time**: < 500ms for prediction endpoints
- **UI Rendering**: < 100ms for initial load, < 50ms for updates
- **Model Inference**: < 200ms per prediction

### Security Considerations
- **CORS**: Configured for development, should be restricted in production
- **Input Validation**: All API inputs validated with Pydantic schemas
- **Error Handling**: No sensitive information in error responses

### Scalability Concerns
- **Stateless API**: Designed for horizontal scaling
- **Model Loading**: Currently loads model into memory, may need optimization for large models
- **Batch Processing**: Supports batch predictions for efficiency

## Development Workflow

### Version Control
- **Branching Strategy**: Feature branches with pull requests
- **Commit Style**: Conventional commits (feat, fix, docs, etc.)
- **Code Review**: Required for all changes

### Testing Strategy
- **Unit Tests**: For core functions and components
- **Integration Tests**: For API endpoints
- **Validation Tests**: For ML models
- **UI Tests**: Manual testing with demo data

### Deployment Considerations
- **Environment Variables**: Used for configuration
- **Docker Support**: Not implemented yet, but planned
- **CI/CD**: Not implemented yet, but planned

## Deployment Infrastructure

### AWS CDK Deployment

- **Frontend**: Static assets hosted in S3 and served through CloudFront
- **Backend**: FastAPI application running in AWS Lambda, exposed through API Gateway
- **Infrastructure as Code**: AWS CDK with TypeScript
- **Deployment Script**: Automated deployment with `deploy.sh`

### Environment Configuration

- **API Endpoint**: Configured at build time via environment variables
- **Lambda Configuration**: Python 3.9 runtime with 512MB memory
- **CloudFront**: HTTPS-only with optimized caching policy
- **S3**: Private bucket with CloudFront Origin Access Identity

## Future Technical Considerations

1. **Docker Containerization**: Package components for easier deployment
2. **Database Integration**: Replace file-based storage with proper database
3. **Authentication/Authorization**: Add user management for production use
4. **Advanced ML Models**: Explore deep learning approaches for better performance
5. **Real-time Updates**: Add WebSocket support for live updates
6. **CI/CD Pipeline**: Automate testing and deployment
7. **Multi-Region Deployment**: Improve availability and latency