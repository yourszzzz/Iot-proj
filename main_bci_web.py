#!/usr/bin/env python3
"""
EEG-based IoT Control System with Real BCI Data
Uses BCI Competition IV Dataset 2a for real brain-computer interface control
"""

import os
import numpy as np
import mne
import warnings
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time
import json

# Set MNE data cache outside the repo to prevent files in workspace
mne_data_path = "/tmp/mne_data"
os.makedirs(mne_data_path, exist_ok=True)
os.environ.setdefault("MNE_DATA", mne_data_path)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eeg_iot_control_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

class BCIDataProcessor:
    def __init__(self):
        self.raw_data = None
        self.events = None
        self.event_id = None
        self.sampling_rate = 250  # BCI Competition IV Dataset 2a sampling rate
        self.channels = []
        self.current_sample = 0
        self.is_running = False
        
    def load_bci_data(self):
        """Load the real BCI Competition IV Dataset 2a"""
        try:
            data_file = 'data/BCICIV_2a_gdf/A01T.gdf'
            print(f"Loading BCI data from: {data_file}")
            
            self.raw_data = mne.io.read_raw_gdf(data_file, preload=True, verbose=False)
            self.events, self.event_id = mne.events_from_annotations(self.raw_data, verbose=False)
            
            # Get channel names and data
            self.channels = self.raw_data.ch_names
            self.sampling_rate = self.raw_data.info['sfreq']
            
            print(f"Loaded {len(self.events)} events from real BCI data")
            print(f"Channels: {len(self.channels)} ({self.channels[:8]}...)")
            print(f"Sampling rate: {self.sampling_rate} Hz")
            print(f"Event types: {self.event_id}")
            
            return True
            
        except Exception as e:
            print(f"Error loading BCI data: {e}")
            return False
    
    def get_current_eeg_sample(self):
        """Get current EEG sample from real data"""
        if self.raw_data is None:
            return None
            
        # Get data from specific channels (first 8 EEG channels)
        n_samples = self.raw_data.n_times
        if self.current_sample >= n_samples:
            self.current_sample = 0  # Loop back to beginning
            
        # Extract data for current sample
        data, _ = self.raw_data[:8, self.current_sample:self.current_sample+1]
        self.current_sample += 1
        
        return data.flatten() * 1e6  # Convert to microvolts
    
    def check_for_events(self):
        """Check if current sample has a motor imagery event"""
        if self.events is None:
            return None
            
        # Find events near current sample (within 125 samples = 0.5 seconds)
        tolerance = 125
        current_events = self.events[
            (self.events[:, 0] >= self.current_sample - tolerance) & 
            (self.events[:, 0] <= self.current_sample + tolerance)
        ]
        
        if len(current_events) > 0:
            event_code = current_events[0][2]
            # Map event codes: 7=left hand, 8=right hand, 9=feet, 10=tongue
            if event_code == 7:  # 769 - Left hand
                return {'action': 'device_on', 'type': 'left_hand', 'device': 'Light Bulb'}
            elif event_code == 8:  # 770 - Right hand
                return {'action': 'device_off', 'type': 'right_hand', 'device': 'Light Bulb'}
            elif event_code == 9:  # 771 - Feet
                return {'action': 'device_on', 'type': 'feet', 'device': 'Tube Light'}
            elif event_code == 10:  # 772 - Tongue
                return {'action': 'device_off', 'type': 'tongue', 'device': 'Fan'}
                
        return None

class IoTDeviceController:
    def __init__(self):
        self.devices = {
            'Light Bulb': {'status': False, 'location': 'Living Room'},
            'Tube Light': {'status': False, 'location': 'Kitchen'},
            'Fan': {'status': False, 'location': 'Bedroom'}
        }
        
    def toggle_device(self, device_name, action=None):
        if device_name in self.devices:
            if action == 'device_on':
                self.devices[device_name]['status'] = True
            elif action == 'device_off':
                self.devices[device_name]['status'] = False
            else:
                self.devices[device_name]['status'] = not self.devices[device_name]['status']
            return True
        return False
        
    def get_status(self):
        return self.devices

# Global instances
bci_processor = BCIDataProcessor()
device_controller = IoTDeviceController()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('device_status', device_controller.get_status())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('toggle_device')
def handle_toggle_device(data):
    device_name = data['device']
    if device_controller.toggle_device(device_name):
        socketio.emit('device_status', device_controller.get_status())
        socketio.emit('activity_log', {
            'timestamp': time.strftime('%H:%M:%S'),
            'message': f"Manual toggle: {device_name} {'ON' if device_controller.devices[device_name]['status'] else 'OFF'}"
        })

def real_time_eeg_processing():
    """Real-time EEG processing thread using actual BCI data"""
    print("Starting real-time EEG processing with real BCI data...")
    
    if not bci_processor.load_bci_data():
        print("Failed to load BCI data, exiting...")
        return
        
    bci_processor.is_running = True
    
    while bci_processor.is_running:
        try:
            # Get current EEG sample
            eeg_sample = bci_processor.get_current_eeg_sample()
            if eeg_sample is not None:
                # Emit EEG data to frontend
                socketio.emit('eeg_data', {
                    'timestamp': time.time(),
                    'channels': eeg_sample.tolist()
                })
                
                # Check for motor imagery events
                event = bci_processor.check_for_events()
                if event:
                    print(f"Detected motor imagery: {event}")
                    
                    # Control devices based on BCI event
                    device_name = event['device']
                    action = event['action']
                    
                    if device_controller.toggle_device(device_name, action):
                        socketio.emit('device_status', device_controller.get_status())
                        socketio.emit('activity_log', {
                            'timestamp': time.strftime('%H:%M:%S'),
                            'message': f"BCI Control ({event['type']}): {device_name} {'ON' if action == 'device_on' else 'OFF'}"
                        })
                        socketio.emit('bci_event', {
                            'type': event['type'],
                            'action': action,
                            'device': device_name
                        })
            
            # Sleep to simulate real-time processing (4ms = 250Hz)
            time.sleep(0.004)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error in EEG processing: {e}")
            break
    
    print("Real-time EEG processing stopped")

if __name__ == '__main__':
    # Start EEG processing in background thread
    eeg_thread = threading.Thread(target=real_time_eeg_processing, daemon=True)
    eeg_thread.start()
    
    print("="*60)
    print("🧠 EEG-based IoT Control System with Real BCI Data")
    print("="*60)
    print("🔗 Web Interface: http://localhost:5000")
    print("📊 Using BCI Competition IV Dataset 2a (A01T.gdf)")
    print("🎮 Motor Imagery Controls:")
    print("   • Left Hand  → Light Bulb ON")
    print("   • Right Hand → Light Bulb OFF") 
    print("   • Feet       → Tube Light ON")
    print("   • Tongue     → Fan OFF")
    print("="*60)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        bci_processor.is_running = False
