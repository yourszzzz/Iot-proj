# Vibe Chat - EEG-based Device Control

This project processes EEG data to simulate device control based on brain activity patterns.

## Setup

1. **You're already in the correct virtual environment (.venv)** ✅
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Running the Project

### ✅ Working Version - Test with Sample Data:
```sh
python test_main.py
```
This downloads MNE sample data (~1.6GB) automatically and runs successfully.

### Alternative - Original main.py (same as test version):
```sh
python main.py
```

### ⚠️ BCI Dataset Version (may have compatibility issues):
```sh
python main_bci.py
```
This tries to use the BCI Competition IV Dataset but may fail due to numpy/GDF format compatibility issues.

## What Works Now

✅ **Dependencies installed** - numpy, mne, scipy, matplotlib  
✅ **Python environment configured** - using .venv  
✅ **Test version works** - uses MNE sample data  
✅ **Device simulation** - demonstrates EEG-based control logic  

## Project Structure
- `main.py` - Working version using MNE sample data
- `test_main.py` - Same working version (for clarity)
- `main_bci.py` - Original BCI dataset version (may have issues)
- `requirements.txt` - Python dependencies
- `data/BCICIV_2a_gdf/` - BCI dataset directory (has files but format issues)

## How It Works
The project simulates device control by:
1. Loading EEG data
2. Detecting event markers in the signal
3. Mapping different event codes to device actions:
   - Event 1: Device ON
   - Event 2: Device OFF  
   - Event 3: Device ACTION
   - Event 4: Device STOP

**Run `python test_main.py` or `python main.py` to see it in action!**
