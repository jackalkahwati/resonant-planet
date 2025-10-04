# Modulus Biosignature Integration - Debug Status

**Date**: October 3, 2025  
**Status**: ✅ Modulus API Healthy | 🔧 Dataset-Specific 500 Errors Under Investigation

---

## ✅ What's Working

### 1. Modulus API is Healthy and Operational
- **Endpoint**: `http://localhost:8000/solve_v2`
- **Status**: Responding correctly to test queries
- **Example Test**:
  ```bash
  curl -X POST http://localhost:8000/solve_v2 \
    -H "Content-Type: application/json" \
    -d '{"question": "What is 47 + 23?"}'
  # Response: {"answer": "70", "confidence": 1.0}
  ```

### 2. Biosignature Workflow is Functional
- **Test Case**: `earth_like_with_life.csv`
  - CO2: 280 ppm, CH4: 1.0 ppm
  - Successfully computed: `log10(CO2/CH4) = 2.447`
  - Confidence: 1.0
- **Integration**: The `ModulusBiosignatureWorkflow` class correctly:
  - Loads atmospheric snapshots from CSV
  - Constructs chemistry questions
  - Calls Modulus API
  - Parses responses

### 3. Small Batch Processing Works
- **Tested**: 2 files in `assets/spectra/test_subset/`
  - `earth_like_with_life.csv` ✅
  - `mars_like_no_life.csv` ✅
- **Result**: Both processed successfully with no 500 errors
- **Metrics Computed**:
  - `log10_CO2_CH4`: Chemical disequilibrium index
  - `greenhouse_temperature_offset`: Thermal disequilibrium

---

## 🔧 Known Issue

### The Problem
- **Original Error**: 500 Internal Server Error from Modulus
- **Context**: Occurred during batch processing of heavier spectra datasets
- **Cause**: Dataset-specific, not a general API failure

### What Triggers 500 Errors (Hypotheses)
1. **Invalid Data Values**:
   - NaN or negative gas mixing ratios
   - Extremely large/small values causing overflow
   - Missing required fields (CO2/CH4)

2. **Malformed Questions**:
   - Very long problem descriptions
   - Special characters in planet names
   - Unusual temperature or flux values

3. **Timeout Issues**:
   - Complex calculations exceeding timeout
   - Large number of simultaneous requests

---

## 📋 Debugging Tools Created

### 1. Enhanced Batch Scanner
**File**: `backend/scripts/debug_batch_scan.py`

**Features**:
- ✅ Per-file detailed logging
- ✅ Data validation (checks for NaN, negative, invalid values)
- ✅ Full error tracebacks with context
- ✅ Retry logic with attempt counting
- ✅ Summary report with success/failure breakdown
- ✅ JSON output with both results and errors

**Usage**:
```bash
cd backend
PYTHONPATH=$(pwd) python scripts/debug_batch_scan.py assets/spectra/DIRECTORY \
    --timeout 90 \
    --retries 2 \
    --output results.json
```

### 2. Data Validation
**File**: `backend/core/biosignature_ingest.py`

**Validated**:
- Loads CSV with fallback heuristics for missing data
- Synthesizes CO2/CH4 from transit depth if not provided
- Handles missing temperature fields gracefully

---

## 🎯 Next Steps (When Ready to Continue)

### Phase 1: Identify Problem Datasets (5-10 minutes)

Run targeted scans on high-value subsets:

```bash
cd backend

# 1. Published JWST data (most important)
PYTHONPATH=$(pwd) python scripts/debug_batch_scan.py assets/spectra/published_real \
    --timeout 90 --retries 2 --output published_scan.json

# 2. Real JWST observations
PYTHONPATH=$(pwd) python scripts/debug_batch_scan.py assets/spectra/jwst_real \
    --timeout 90 --retries 2 --output jwst_scan.json

# 3. Kepler candidates
PYTHONPATH=$(pwd) python scripts/debug_batch_scan.py assets/spectra/kepler \
    --timeout 90 --retries 2 --output kepler_scan.json
```

**Expected Outcome**: 
- Identify which specific file(s) cause 500 errors
- Get full traceback and question text for failed cases

### Phase 2: Fix Problem Datasets (15-30 minutes)

Once identified, address failures by:

1. **Inspect the problematic CSV**:
   ```bash
   cat assets/spectra/PATH/TO/PROBLEM_FILE.csv | head -20
   ```

2. **Check the generated question** (from debug log):
   - Look for unusual formatting
   - Verify PPM values are reasonable
   - Check for special characters

3. **Apply fixes**:
   - **Option A**: Sanitize the input data
   - **Option B**: Add pre-flight validation
   - **Option C**: Adjust question template for edge cases
   - **Option D**: Skip problematic datasets with fallback values

### Phase 3: Full Batch Processing (10-20 minutes)

Run the complete scan with confidence:

```bash
cd backend

# Run in background with full logging
PYTHONPATH=$(pwd) nohup python scripts/debug_batch_scan.py assets/spectra \
    --timeout 120 \
    --retries 3 \
    --output full_biosignature_results.json \
    > batch_scan_full.log 2>&1 &

# Monitor progress
tail -f batch_scan_full.log

# Check when done
cat full_biosignature_results.json | jq '.summary'
```

**Expected Results**:
- JSON file with biosignature metrics for all planets
- Success rate > 90% (some synthetic data may legitimately fail)
- Clear list of any remaining problem files

### Phase 4: Analysis & Visualization (30 minutes)

Create comparison reports:

```python
import json

# Load results
with open('full_biosignature_results.json') as f:
    data = json.load(f)

# Find strong biosignature candidates
candidates = [
    r for r in data['results']
    if r.get('success') and 
    any(m['value'] > THRESHOLD for m in r['modulus'])
]

# Compare with literature
for candidate in candidates:
    print(f"{candidate['planet']}: {candidate['modulus']}")
```

---

## 📊 Current Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Modulus API | ✅ Healthy | Responding on port 8000 |
| Biosignature Workflow | ✅ Working | Tested on demo files |
| Small Batch (2 files) | ✅ Success | No errors |
| Full Dataset Scan | 🔧 Pending | Need to identify problem files |
| Debug Tools | ✅ Ready | Enhanced scanner available |

---

## 🔍 Quick Diagnostic Commands

### Check Modulus Health
```bash
curl http://localhost:8000/v2/health
```

### Test Single File
```bash
cd backend
PYTHONPATH=$(pwd) python3 -c "
from pathlib import Path
from core.biosignature_ingest import load_atmospheric_snapshot
from core.biosignature_modulus_workflow import ModulusBiosignatureWorkflow

workflow = ModulusBiosignatureWorkflow(base_url='http://localhost:8000', timeout=60)
snapshot = load_atmospheric_snapshot(Path('assets/spectra/FILENAME.csv'))
result = workflow.run_composite_analysis(snapshot)
print(result)
"
```

### Count Total Datasets
```bash
find backend/assets/spectra -name "*.csv" | wc -l
```

### List Dataset Categories
```bash
find backend/assets/spectra -type d -mindepth 1 -maxdepth 1
```

---

## 💡 Recommendations

### For Production Deployment

1. **Add Request Validation**: Pre-validate all PPM values and temperatures before sending to Modulus
2. **Implement Circuit Breaker**: Stop batch after N consecutive failures
3. **Cache Results**: Store Modulus responses to avoid re-computation
4. **Fallback Heuristics**: Use simplified chemistry models when Modulus unavailable
5. **Monitoring**: Track success rate, average latency, error types

### For Scientific Accuracy

1. **Verify Synthetic Data**: Some CSVs may have placeholder values that aren't chemically realistic
2. **Literature Cross-Check**: Compare Modulus results with published biosignature assessments
3. **Uncertainty Quantification**: Propagate Modulus confidence scores through final biosignature scores
4. **False Positive Analysis**: Test on known abiotic atmospheres (Venus, Mars, hot Jupiters)

---

## 📝 Log Files

- `/tmp/modulus_api.log` - Modulus server logs
- `backend/batch_scan.log` - Most recent batch scan output
- `backend/*_scan.json` - Structured results with success/failure data

---

## 🎯 Goal

Once debugging is complete, you'll have:

✅ A robust biosignature detection pipeline  
✅ Modulus-powered chemistry validation for all exoplanet datasets  
✅ Comparison with literature biosignature assessments  
✅ Prioritized candidate list for follow-up observations  
✅ Publication-ready analysis of disequilibrium signatures  

**The foundation is solid. We just need to identify and handle the edge cases causing those 500 errors.**


