# Exoplanet AI - NASA Space Apps Challenge 2025

> **A World Away: Hunting for Exoplanets with AI**

An advanced AI/ML system for exoplanet detection and classification using NASA's Kepler and TESS mission data.

![NASA Space Apps Challenge](https://img.shields.io/badge/NASA-Space%20Apps%20Challenge-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![React](https://img.shields.io/badge/React-18-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)

## Features

### AI/ML Models
- **Ensemble Architecture**: Combines 5 state-of-the-art algorithms:
  - XGBoost (25% weight)
  - LightGBM (25% weight)  
  - CatBoost (20% weight)
  - Random Forest (15% weight)
  - Neural Network with Attention (15% weight)

- **Advanced Preprocessing**:
  - Feature engineering (radius ratios, transit duty cycles, habitability indicators)
  - SMOTE/undersampling for class imbalance
  - Standardization and missing value imputation

- **Model Explainability**:
  - SHAP values for prediction explanations
  - Feature importance rankings
  - Model consensus visualization

### Web Interface
- **Dashboard**: Real-time model metrics and data visualizations
- **Train Model**: Configure and train on Kepler/TESS datasets
- **Predict**: Interactive parameter sliders with preset configurations
- **Upload Data**: Batch classify CSV files with drag-and-drop
- **Explore**: 3D interactive visualization of confirmed exoplanets
- **Dataset Explorer**: Browse NASA exoplanet archive data

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd exoplanet-ai/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd exoplanet-ai/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## Usage

### 1. Train the Model

1. Navigate to the "Train Model" tab
2. Select dataset (Kepler or TESS)
3. Configure test split and balancing method
4. Click "Start Training"
5. Wait for training to complete (~2-5 minutes)

### 2. Make Predictions

**Single Prediction:**
1. Go to "Predict" tab
2. Use sliders to set transit parameters or select a preset
3. Click "Classify Exoplanet"
4. View prediction with confidence scores and explanations

**Batch Prediction:**
1. Go to "Upload Data" tab
2. Drag & drop a CSV file with transit observations
3. View classification results and summary statistics

### 3. Explore Exoplanets

- Use the 3D viewer to explore confirmed exoplanets
- Click planets to view detailed properties
- Filter by habitability potential

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/model/status` | GET | Get model status and metrics |
| `/api/model/train` | POST | Train the ensemble model |
| `/api/predict` | POST | Single prediction |
| `/api/predict/batch` | POST | Batch predictions |
| `/api/predict/upload` | POST | Upload CSV for classification |
| `/api/model/features` | GET | Get feature importance |
| `/api/data/statistics` | GET | Dataset statistics |
| `/api/exoplanets/confirmed` | GET | List confirmed exoplanets |

## Data Sources

- [Kepler KOI](https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=cumulative) - Kepler Objects of Interest
- [TESS TOI](https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=TOI) - TESS Objects of Interest
- [K2 Candidates](https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=k2pandc) - K2 Mission Candidates

## Project Structure

```
exoplanet-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   ├── data_pipeline.py  # Data fetching and preprocessing
│   │   ├── models.py         # ML models (ensemble + neural network)
│   │   └── explainability.py # SHAP and feature explanations
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── pages/        # Page components
│   │   │   ├── ui/           # Reusable UI components
│   │   │   ├── Header.tsx
│   │   │   └── StarField.tsx
│   │   ├── lib/
│   │   │   ├── api.ts        # API client
│   │   │   └── utils.ts      # Utility functions
│   │   ├── store/
│   │   │   └── useStore.ts   # Zustand state management
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

## Technologies Used

### Backend
- **FastAPI** - Modern Python web framework
- **XGBoost, LightGBM, CatBoost** - Gradient boosting frameworks
- **PyTorch** - Neural network with attention mechanism
- **scikit-learn** - ML utilities and preprocessing
- **SHAP** - Model explainability
- **pandas, numpy** - Data processing

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Recharts** - Data visualization
- **Three.js / React Three Fiber** - 3D visualization
- **Framer Motion** - Animations
- **Zustand** - State management

## Performance

Expected model performance after training on Kepler KOI dataset:

| Metric | Score |
|--------|-------|
| Accuracy | ~90-95% |
| F1 Score (macro) | ~85-90% |
| ROC AUC | ~0.95+ |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- NASA Exoplanet Archive for providing the data
- NASA Space Apps Challenge for the inspiration
- Google's AstroNet for research foundation

---

**Built with ❤️ for NASA Space Apps Challenge 2025**
