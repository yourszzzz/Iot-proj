#!/usr/bin/env python3
"""
DEBUG VERSION: EEG-based IoT Control System with Real BCI Data
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

print("🔧 DEBUG: Starting application...")

# Set MNE data cache outside the repo to prevent files in workspace
mne_data_path = "/tmp/mne_data"
os.makedirs(mne_data_path, exist_ok=True)
os.environ.setdefault("MNE_DATA", mne_data_path)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

print("🔧 DEBUG: Creating Flask app...")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'eeg_iot_control_secret'
socketio = SocketIO(app, cors_allowed_origins="*")
print("🔧 DEBUG: Flask app created successfully")

class BCIDataProcessor:
    def __init__(self):
        print("🔧 DEBUG: Initializing BCI Data Processor...")
        self.raw_data = None
        self.events = None
        self.event_id = None
        self.sampling_rate = 250  # BCI Competition IV Dataset 2a sampling rate
        self.channels = []
        self.current_sample = 0
        self.is_running = False
        print("🔧 DEBUG: BCI Data Processor initialized")
        
    def load_bci_data(self):
        """Load the real BCI Competition IV Dataset 2a"""
        try:
            print("🔧 DEBUG: Starting BCI data loading...")
            data_file = 'data/BCICIV_2a_gdf/A01T.gdf'
            print(f"🔧 DEBUG: Loading BCI data from: {data_file}")
            
            self.raw_data = mne.io.read_raw_gdf(data_file, preload=True, verbose=False)
            print("🔧 DEBUG: Raw data loaded successfully")
            
            self.events, self.event_id = mne.events_from_annotations(self.raw_data, verbose=False)
            print("🔧 DEBUG: Events extracted successfully")
            
            # Get channel names and data
            self.channels = self.raw_data.ch_names
            self.sampling_rate = self.raw_data.info['sfreq']
            
            print(f"🔧 DEBUG: Loaded {len(self.events)} events from real BCI data")
            print(f"🔧 DEBUG: Channels: {len(self.channels)} ({self.channels[:8]}...)")
            print(f"🔧 DEBUG: Sampling rate: {self.sampling_rate} Hz")
            print(f"🔧 DEBUG: Event types: {self.event_id}")
            
            return True
            
        except Exception as e:
            print(f"🔧 DEBUG ERROR: Error loading BCI data: {e}")
            import traceback
            traceback.print_exc()
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
        print("🔧 DEBUG: Initializing IoT Device Controller...")
        self.devices = {
            'Light Bulb': {'status': False, 'location': 'Living Room'},
            'Tube Light': {'status': False, 'location': 'Kitchen'},
            'Fan': {'status': False, 'location': 'Bedroom'}
        }
        print("🔧 DEBUG: IoT Device Controller initialized")
        
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
print("🔧 DEBUG: Creating global instances...")
bci_processor = BCIDataProcessor()
device_controller = IoTDeviceController()
print("🔧 DEBUG: Global instances created")

@app.route('/')
def index():
    print("🔧 DEBUG: Serving index page")
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('🔧 DEBUG: Client connected')
    socketio.emit('device_status', device_controller.get_status())

@socketio.on('disconnect')
def handle_disconnect():
    print('🔧 DEBUG: Client disconnected')

@socketio.on('toggle_device')
def handle_toggle_device(data):
    print(f"🔧 DEBUG: Toggle device request: {data}")
    device_name = data['device']
    if device_controller.toggle_device(device_name):
        socketio.emit('device_status', device_controller.get_status())
        socketio.emit('activity_log', {
            'timestamp': time.strftime('%H:%M:%S'),
            'message': f"Manual toggle: {device_name} {'ON' if device_controller.devices[device_name]['status'] else 'OFF'}"
        })

def real_time_eeg_processing():
    """Real-time EEG processing thread using actual BCI data"""
    print("🔧 DEBUG: Starting real-time EEG processing thread...")
    
    if not bci_processor.load_bci_data():
        print("🔧 DEBUG ERROR: Failed to load BCI data, exiting thread...")
        return
        
    bci_processor.is_running = True
    print("🔧 DEBUG: BCI data loaded, starting main processing loop...")
    
    sample_count = 0
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
                
                sample_count += 1
                if sample_count % 250 == 0:  # Every second
                    print(f"🔧 DEBUG: Processed {sample_count} samples")
                
                # Check for motor imagery events
                event = bci_processor.check_for_events()
                if event:
                    print(f"🔧 DEBUG: Detected motor imagery: {event}")
                    
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
            print("🔧 DEBUG: KeyboardInterrupt in processing thread")
            break
        except Exception as e:
            print(f"🔧 DEBUG ERROR: Error in EEG processing: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print("🔧 DEBUG: Real-time EEG processing stopped")

if __name__ == '__main__':
    print("🔧 DEBUG: Starting main application...")
    
    # Start EEG processing in background thread
    print("🔧 DEBUG: Creating EEG processing thread...")
    eeg_thread = threading.Thread(target=real_time_eeg_processing, daemon=True)
    print("🔧 DEBUG: Starting EEG processing thread...")
    eeg_thread.start()
    print("🔧 DEBUG: EEG processing thread started")
    
    print("="*60)
    print("🧠 EEG-based IoT Control System with Real BCI Data (DEBUG)")
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
        print("🔧 DEBUG: Starting Flask-SocketIO server...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("🔧 DEBUG: KeyboardInterrupt received, shutting down...")
    except Exception as e:
        print(f"🔧 DEBUG ERROR: Error starting server: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔧 DEBUG: Setting is_running to False...")
        bci_processor.is_running = False
        print("🔧 DEBUG: Application shutdown complete")
