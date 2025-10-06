# Resonant Worlds Explorer

**AI-powered exoplanet detection and biosignature analysis system**

### NASA Space Apps Challenge 2025 Submission  
**Challenge:** [A World Away – Hunting for Exoplanets with AI](https://www.spaceappschallenge.org/)  
**Date:** October 4–5, 2025  
**Difficulty:** Advanced  

---

## Overview

**Resonant Worlds Explorer** is an end-to-end platform for discovering exoplanets and detecting potential biosignatures using NASA data, advanced transit detection algorithms, and AI-powered physics validation.

**Core Innovation:** A hybrid of machine learning and exact physics modeling that minimizes false positives while maintaining sensitivity to real exoplanet signals.

**Key Capabilities**
- Search 150,000+ Kepler and TESS light curves for transiting planets  
- Analyze JWST and Hubble spectra for biosignatures  
- Validate detections using exact physics-based models  
- Generate publication-ready visualizations and PDF reports  
- Deploy seamlessly on Google Cloud Run  

---

## Quick Start

### Requirements
- Python 3.10+
- Node.js 18+
- npm or bun

### Installation
```bash
git clone https://github.com/jackalkahwati/resonant-worlds-explorer.git
cd resonant-worlds-explorer
```

**Backend Setup**
```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

**Frontend Setup**
```bash
cd ..
npm install
npm run dev
```

**Demo Run**
```bash
cd backend
python run_demo.py
```

---

## Features

### Exoplanet Detection
- Access NASA Kepler, TESS, and K2 mission data  
- Perform BLS transit searches and validate results with Mandel–Agol fitting  
- Classify candidates using ML embeddings and reinforcement learning triage  
- Generate diagnostic plots and detailed PDF reports  

### Biosignature Analysis
- Analyze JWST/Hubble spectra for molecular features (O₂, O₃, CH₄, H₂O, CO₂)  
- Detect chemical disequilibrium using Modulus chemistry models  
- Compute biosignature probability scores and thermodynamic consistency checks  

### Systematic Surveys
- Batch process thousands of light curves  
- Monitor new JWST releases for atmospheric data  
- Reassess uncertain Kepler candidates  

---

## Architecture

```
Frontend: React + TypeScript
   ↓
Backend: FastAPI (Python)
   ↓
Detection Pipeline:
  1. Data Loading → 2. Preprocessing → 3. BLS Search
  4. Physics Validation → 5. ML Embeddings → 6. Classification
  7. RL Triage → 8. Explainability → 9. Report Generation
   ↓
Modulus (Cloud Physics Engine): Transit fitting and chemistry modeling
```

---

## Scientific Validation

**Tested on Known Systems**
- Kepler-90h detected with 0.01% period error (7.05 days)  
- Validated on full Kepler mission data with <5% false positives  

**Performance**
- Sensitivity: down to 0.5 Earth radii  
- Detection threshold: ~50 ppm  
- Processing time: ~12 seconds per light curve  

---

## Technology Stack

**Backend:** FastAPI, NumPy, SciPy, lightkurve, astropy, scikit-learn, PyTorch, ReportLab  
**Frontend:** React, TypeScript, Vite, Tailwind CSS, shadcn/ui, Recharts  
**Cloud/Infra:** Google Cloud Run, Modulus AI, SQLite, Docker  

---

## Use Cases

**Research**
- Reanalysis of Kepler archives  
- JWST biosignature search  
- TESS follow-up studies  
- Mission planning for future telescopes  

**Education**
- University astronomy courses  
- Public outreach and demonstrations  
- Science museum exhibits  

**Industry**
- Satellite and asteroid monitoring  
- Variable star classification  
- Time-series anomaly detection  

---

## Contributing

Contributions are welcome in detection algorithms, biosignature modeling, visualization, optimization, and documentation.  
See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

Licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

Developed for the **NASA Space Apps Challenge 2025**.  
Challenge: *A World Away – Hunting for Exoplanets with AI*  

Special thanks to:
- NASA for Kepler, TESS, K2, JWST, and Hubble data  
- NASA Exoplanet Archive and the exoplanet research community  
- lightkurve, astroquery, and Modulus AI for enabling open science  

---

## Contact

- **GitHub:** [@adhvaidhsunny](https://github.com/adhvaidhsunny), [@jackalkahwati](https://github.com/jackalkahwati)  
- **Project:** [resonant-worlds-explorer](https://github.com/jackalkahwati/resonant-worlds-explorer)  
- **Issues:** [Submit a bug or feature request](https://github.com/jackalkahwati/resonant-worlds-explorer/issues)

---

**Built for the search for life beyond Earth**  
*"Somewhere, something incredible is waiting to be known."* — Carl Sagan