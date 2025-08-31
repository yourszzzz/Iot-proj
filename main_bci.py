import os
import numpy as np
import mne
import warnings

# Set MNE data cache outside the repo to prevent files in workspace
mne_data_path = "/tmp/mne_data"
os.makedirs(mne_data_path, exist_ok=True)
os.environ.setdefault("MNE_DATA", mne_data_path)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

print("Loading BCI Competition IV Dataset 2a...")

# Load the BCI dataset
try:
    data_file = 'data/BCICIV_2a_gdf/A01T.gdf'
    raw = mne.io.read_raw_gdf(data_file, preload=True, verbose=False)
    print(f"Loaded data from: {data_file}")
    
    # Extract event markers
    events = mne.find_events(raw, verbose=False)
    print(f"Found {len(events)} events")
    
    # Print the first few detected events
    print("First 10 events:\n", events[:10])
    
    # Simulate device ON/OFF control based on event codes:
    print("\nSimulating device control:")
    for i, e in enumerate(events[:20]):  # First 20 events for demo
        event_code = e[2]
        timestamp = e[0]
        
        if event_code == 769:  # Left hand motor imagery
            print(f"Event {i+1}: Device ON (left hand) - timestamp: {timestamp}")
        elif event_code == 770:  # Right hand motor imagery  
            print(f"Event {i+1}: Device OFF (right hand) - timestamp: {timestamp}")
        elif event_code == 771:  # Feet motor imagery
            print(f"Event {i+1}: Device ACTION (feet) - timestamp: {timestamp}")
        elif event_code == 772:  # Tongue motor imagery
            print(f"Event {i+1}: Device STOP (tongue) - timestamp: {timestamp}")
        else:
            print(f"Event {i+1}: Other event (code: {event_code}) - timestamp: {timestamp}")
            
except FileNotFoundError:
    print("ERROR: BCI dataset not found!")
    print("Please download the BCI Competition IV Dataset 2a from:")
    print("http://www.bbci.de/competition/iv/")
    print("Extract A01T.gdf to data/BCICIV_2a_gdf/")
    print("")
    print("Alternatively, run test_main.py for a working demo with sample data.")
    
except Exception as e:
    print(f"Error loading data: {e}")
    print("Note: This may be due to compatibility issues with the GDF format.")
    print("Try running the test version: python test_main.py")

print("\nEEG processing test completed!")
