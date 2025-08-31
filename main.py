import numpy as np
import mne

print("Testing EEG processing with MNE sample data...")

# Use MNE's built-in sample data (downloads automatically)
sample_data_folder = mne.datasets.sample.data_path()
sample_data_raw_file = sample_data_folder / 'MEG' / 'sample' / 'sample_audvis_filt-0-40_raw.fif'

print(f"Loading data from: {sample_data_raw_file}")

# Load the sample EEG data
raw = mne.io.read_raw_fif(sample_data_raw_file, preload=True)

# Extract event markers
events = mne.find_events(raw, stim_channel='STI 014')
print(f"Found {len(events)} events")

# Print the first few detected events
print("First 10 events:\n", events[:10])

# Simulate device ON/OFF control based on event codes:
print("\nSimulating device control:")
for i, e in enumerate(events[:20]):  # First 20 events for demo
    event_code = e[2]
    timestamp = e[0]
    
    if event_code == 1:
        print(f"Event {i+1}: Device ON (auditory left) - timestamp: {timestamp}")
    elif event_code == 2:
        print(f"Event {i+1}: Device OFF (auditory right) - timestamp: {timestamp}")
    elif event_code == 3:
        print(f"Event {i+1}: Device ACTION (visual left) - timestamp: {timestamp}")
    elif event_code == 4:
        print(f"Event {i+1}: Device STOP (visual right) - timestamp: {timestamp}")
    else:
        print(f"Event {i+1}: Other event (code: {event_code}) - timestamp: {timestamp}")

print("\nEEG processing test completed successfully!")