# Data Sources Guide - Finding Real Exoplanets

## 📊 Current Status

### ✅ What Works Now

**Demo Data (Included)**:
- ✓ `kepler_tp.csv` - Synthetic true positive transit
- ✓ `kepler_fp.csv` - Synthetic false positive (eclipsing binary)
- ✓ CSV file upload via API
- ✓ Full detection pipeline functional

### ❌ What's Not Connected Yet

**Live NASA Data**:
- ✗ Kepler mission archive (MAST)
- ✗ TESS mission data
- ✗ K2 mission data
- ✗ Automatic target querying

## 🚀 How to Connect to Real NASA Data

### Option 1: Lightkurve Library (Recommended)

**What is it**: Python package for downloading and analyzing Kepler/TESS data

**Installation**:
```bash
pip install lightkurve
```

**Integration Steps**:

1. **Add to `backend/requirements.txt`**:
```
lightkurve>=2.4.0
```

2. **Create `backend/core/data_sources.py`**:
```python
import lightkurve as lk
import numpy as np

def fetch_kepler_lightcurve(target_id: str):
    """
    Fetch light curve from Kepler archive.
    
    Parameters
    ----------
    target_id : str
        Kepler ID (e.g., 'KIC 8462852')
    
    Returns
    -------
    tuple
        (time, flux, flux_err) arrays
    """
    # Search for target
    search_result = lk.search_lightcurve(target_id, mission='Kepler')
    
    if len(search_result) == 0:
        raise ValueError(f"No data found for {target_id}")
    
    # Download first available quarter
    lc = search_result[0].download()
    
    # Remove NaN values
    lc = lc.remove_nans()
    
    # Normalize
    lc = lc.normalize()
    
    # Extract arrays
    time = lc.time.value  # Days
    flux = lc.flux.value  # Normalized
    flux_err = lc.flux_err.value if lc.flux_err is not None else np.ones_like(flux) * 0.001
    
    return time, flux, flux_err


def fetch_tess_lightcurve(target_id: str):
    """Fetch TESS light curve."""
    search_result = lk.search_lightcurve(target_id, mission='TESS')
    
    if len(search_result) == 0:
        raise ValueError(f"No TESS data found for {target_id}")
    
    lc = search_result[0].download()
    lc = lc.remove_nans().normalize()
    
    return lc.time.value, lc.flux.value, lc.flux_err.value


def search_targets(coordinates=None, radius=None, mission='Kepler'):
    """
    Search for targets in a region.
    
    Parameters
    ----------
    coordinates : str
        Sky coordinates (e.g., '19h50m47s +40d03m47s')
    radius : float
        Search radius in arcseconds
    mission : str
        'Kepler', 'TESS', or 'K2'
    
    Returns
    -------
    list
        List of target IDs
    """
    if coordinates:
        results = lk.search_lightcurve(coordinates, radius=radius, mission=mission)
    else:
        # Example: search for high-priority Kepler targets
        results = lk.search_lightcurve('KIC*', mission=mission)
    
    return [str(r.target_name) for r in results[:100]]  # Limit to 100
```

3. **Update `backend/api/routes/datasets.py`**:
```python
from core.data_sources import fetch_kepler_lightcurve, fetch_tess_lightcurve, search_targets

@router.get("/search")
async def search_nasa_targets(
    mission: str = "Kepler",
    coordinates: Optional[str] = None,
    radius: float = 120.0
):
    """Search for targets in NASA archives."""
    try:
        targets = search_targets(coordinates, radius, mission)
        return {"targets": targets, "count": len(targets)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-nasa")
async def fetch_nasa_data(target_id: str, mission: str = "Kepler"):
    """Fetch light curve from NASA archive."""
    try:
        if mission.lower() == 'kepler':
            time, flux, flux_err = fetch_kepler_lightcurve(target_id)
        elif mission.lower() == 'tess':
            time, flux, flux_err = fetch_tess_lightcurve(target_id)
        else:
            raise ValueError(f"Unsupported mission: {mission}")
        
        # Save to temporary file
        import uuid
        dataset_id = str(uuid.uuid4())
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        filepath = upload_dir / f"{dataset_id}.csv"
        np.savetxt(filepath, np.column_stack([time, flux, flux_err]), 
                   delimiter=',', header='time,flux,flux_err', comments='')
        
        return {
            "dataset_id": dataset_id,
            "target_id": target_id,
            "mission": mission,
            "num_points": len(time),
            "time_span_days": float(time.max() - time.min())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Option 2: MAST API (Direct)

**What is it**: Barbara A. Mikulski Archive for Space Telescopes - official NASA archive

**Installation**:
```bash
pip install astroquery
```

**Example Code**:
```python
from astroquery.mast import Observations

def fetch_via_mast(target_name: str):
    """Fetch using MAST API directly."""
    obs = Observations.query_criteria(
        target_name=target_name,
        obs_collection=['Kepler'],
        dataproduct_type=['timeseries']
    )
    
    if len(obs) == 0:
        raise ValueError(f"No observations found for {target_name}")
    
    # Download data products
    products = Observations.get_product_list(obs[0])
    manifest = Observations.download_products(products[0])
    
    # Parse FITS file
    from astropy.io import fits
    with fits.open(manifest['Local Path'][0]) as hdul:
        data = hdul[1].data
        time = data['TIME']
        flux = data['PDCSAP_FLUX']
        flux_err = data['PDCSAP_FLUX_ERR']
    
    return time, flux, flux_err
```

## 🎯 Quick Start with Real Data

### Using Lightkurve (Easiest)

```python
# In backend directory
pip install lightkurve

# Test script
python3 << EOF
import lightkurve as lk

# Fetch Kepler-90 (8-planet system)
lc = lk.search_lightcurve('KIC 11442793', mission='Kepler', quarter=10).download()
lc = lc.remove_nans().normalize()

# Save as CSV
import numpy as np
data = np.column_stack([lc.time.value, lc.flux.value, lc.flux_err.value])
np.savetxt('kepler90_real.csv', data, delimiter=',', header='time,flux,flux_err', comments='')

print(f"Downloaded {len(lc)} points for Kepler-90")
print("Saved to kepler90_real.csv")
EOF
```

Then upload via API or frontend!

## 📋 Real Exoplanet Targets to Try

### Confirmed Planets (Good for Testing)

| Target ID | Name | Period | Depth | Notes |
|-----------|------|--------|-------|-------|
| KIC 11442793 | Kepler-90i | 14.45d | 9000 ppm | Earth-size in 8-planet system |
| KIC 10593626 | Kepler-452b | 384.8d | 300 ppm | Earth's cousin |
| KIC 8462852 | Tabby's Star | - | Variable | Famous dimming events |
| TIC 307210830 | TOI-700d | 37.4d | 1000 ppm | TESS habitable zone planet |

### How to Fetch Them

```python
import lightkurve as lk

# Kepler-90i
lc = lk.search_lightcurve('KIC 11442793', quarter=10).download()

# Kepler-452b  
lc = lk.search_lightcurve('KIC 10593626', quarter=10).download()

# TESS planet
lc = lk.search_lightcurve('TIC 307210830', mission='TESS').download()
```

## 🔧 Implementation Checklist

To fully connect to NASA data:

- [ ] Install lightkurve: `pip install lightkurve`
- [ ] Create `core/data_sources.py` (see above)
- [ ] Add routes in `api/routes/datasets.py`:
  - [ ] `GET /api/datasets/search` - Search NASA archives
  - [ ] `POST /api/datasets/fetch-nasa` - Fetch light curve
- [ ] Update frontend `src/pages/Detect.tsx`:
  - [ ] Add "Search NASA Archive" tab
  - [ ] Add target ID search field
  - [ ] Add mission selector (Kepler/TESS/K2)
- [ ] Test with known planets
- [ ] Document new endpoints

## 🌟 After Integration

**You'll be able to**:
1. Search Kepler/TESS archives by target ID or coordinates
2. Download light curves directly from NASA
3. Run detection on real mission data
4. Compare results to confirmed planet catalog
5. Potentially discover new candidates!

## ⚠️ Important Notes

**Current Limitations**:
- Mock physics in Modulus adapter (works but simplified)
- Heuristic classifier (needs training on labeled data)
- No multi-planet search yet (would find strongest signal only)

**For Real Discovery**:
1. Replace mock Modulus with full physics
2. Train classifier on ExoFOP-vetted candidates
3. Add multi-planet iterative search
4. Cross-reference with confirmed planets database

## 📚 Resources

- **Lightkurve**: https://docs.lightkurve.org
- **MAST Portal**: https://mast.stsci.edu
- **Kepler Archive**: https://archive.stsci.edu/kepler
- **TESS Archive**: https://archive.stsci.edu/tess
- **ExoFOP**: https://exofop.ipac.caltech.edu

## 🚀 Next Steps

**Quick Win** (30 minutes):
```bash
pip install lightkurve
# Create data_sources.py (copy from above)
# Add one new route for fetching
# Test with Kepler-90i
```

**Full Integration** (2-3 hours):
- Complete data_sources.py
- Add all new routes
- Update frontend with search UI
- Test with 10+ confirmed planets

**Production Ready** (1-2 days):
- Replace mock physics
- Train real classifier
- Add planet catalog cross-check
- Implement multi-planet search

---

**Bottom Line**: 
- ✅ Pipeline works now with CSV files
- ✅ Can upload any Kepler/TESS CSV manually
- ❌ Not yet auto-fetching from NASA
- 🚀 Easy to add with lightkurve!
