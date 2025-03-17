# RN Blood Test Interface

A user interface for Registered Nurses to enter blood test results and view model predictions for the Active Patient Follow-Up Alert Dashboard.

## Technology Stack

- **Build Tool**: Vite
- **Framework**: React 18+
- **Language**: TypeScript
- **Routing**: TanStack Router
- **State Management**: Effector
- **Styling**: CSS Modules

## Project Structure

```
src/ui/
├── components/           # Reusable UI components
├── pages/                # Page components
├── api/                  # API integration
├── stores/               # Effector stores
├── routes.tsx            # TanStack Router configuration
├── App.tsx               # Main application component
└── main.tsx              # Entry point
```

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

1. Navigate to the UI directory:
   ```bash
   cd src/ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Development

1. Start the development server:
   ```bash
   npm run dev
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

### Building for Production

1. Build the application:
   ```bash
   npm run build
   ```

2. Preview the production build:
   ```bash
   npm run preview
   ```

## Integration with Backend

The UI connects to the FastAPI backend running on `http://localhost:8000`. Make sure the inference API is running before using the UI.

To start the inference API:

```bash
python -m src.inference.app
```

## Features

- **Test Entry Form**: Input form for entering blood test results
- **Results Display**: View prediction results with confidence scores
- **Validation Metrics**: Display model validation metrics
- **Responsive Design**: Works on desktop and tablet devices

## API Endpoints Used

- `POST /predict`: Submit test results and get predictions
- `GET /model-info`: Get information about the current model