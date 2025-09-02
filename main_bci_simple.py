#!/usr/bin/env python3
"""
Sclass BCIDataProcessor:
    def __init__(self):
        self.raw_data = None
        self.events = None
        self.event_id = None
        self.sampling_rate = 250  # Hz
        self.channels = []
        self.current_sample = 0
        self.is_running = False
        self.data_loaded = False
        self.last_event_sample = -1000  # Cooldown trackingVERSION: EEG-based IoT Control System
Loads data on-demand instead of at startup
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
        self.sampling_rate = 250
        self.channels = []
        self.current_sample = 0
        self.is_running = False
        self.data_loaded = False
        self.last_event_sample = -1000  # Cooldown tracking
        
    def load_bci_data(self):
        """Load the real BCI Competition IV Dataset 2a"""
        if self.data_loaded:
            return True
            
        try:
            print("Loading BCI data from: data/BCICIV_2a_gdf/A01T.gdf")
            
            self.raw_data = mne.io.read_raw_gdf('data/BCICIV_2a_gdf/A01T.gdf', preload=True, verbose=False)
            self.events, self.event_id = mne.events_from_annotations(self.raw_data, verbose=False)
            
            self.channels = self.raw_data.ch_names
            self.sampling_rate = self.raw_data.info['sfreq']
            
            print(f"✅ Loaded {len(self.events)} events from real BCI data")
            print(f"✅ Channels: {len(self.channels)}, Sampling rate: {self.sampling_rate} Hz")
            print(f"🔍 Event ID mapping: {self.event_id}")
            print(f"🔍 First 10 events: {self.events[:10] if len(self.events) > 0 else 'No events'}")
            print(f"🔍 Unique event codes: {list(set(self.events[:, 2])) if len(self.events) > 0 else 'No events'}")
            
            self.data_loaded = True
            print(f"🎯 Jumping to sample 91800 to find motor imagery events faster...")
            self.current_sample = 91800  # Jump close to the first motor imagery event
            return True
            
        except Exception as e:
            print(f"❌ Error loading BCI data: {e}")
            return False
    
    def get_current_eeg_sample(self):
        """Get current EEG sample from real data"""
        if not self.data_loaded or self.raw_data is None:
            return None
            
        n_samples = self.raw_data.n_times
        if self.current_sample >= n_samples:
            self.current_sample = 0  # Loop back to beginning
            
        # Extract data for current sample (first 8 EEG channels)
        data, _ = self.raw_data[:8, self.current_sample:self.current_sample+1]
        self.current_sample += 1
        
        return data.flatten() * 1e6  # Convert to microvolts
    
    def check_for_events(self):
        """Check if current sample has a motor imagery event"""
        if not self.data_loaded or self.events is None:
            return None
            
        # Cooldown period: don't process events too close together (2 seconds = 500 samples at 250Hz)
        cooldown_samples = 500  
        if self.current_sample - self.last_event_sample < cooldown_samples:
            return None
            
        # Find events near current sample with smaller tolerance
        tolerance = 25  # ~0.1 seconds at 250Hz (much more precise)
        current_events = self.events[
            (self.events[:, 0] >= self.current_sample - tolerance) & 
            (self.events[:, 0] <= self.current_sample + tolerance)
        ]
        
        if len(current_events) > 0:
            event_code = current_events[0][2]
            
            # ONLY process motor imagery events (codes 7-10)
            if event_code in [7, 8, 9, 10]:
                print(f"🧠 MOTOR IMAGERY EVENT detected at sample {self.current_sample}: code {event_code}")
                self.last_event_sample = self.current_sample  # Update cooldown
                
                # BRAIN-CONTROLLED DEVICE SWITCHING
                if event_code == 7:  # 769 - Left hand motor imagery
                    return {'action': 'switch_device', 'type': 'left_hand', 'device': 'Light Bulb', 'state': 'toggle'}
                elif event_code == 8:  # 770 - Right hand motor imagery
                    return {'action': 'switch_device', 'type': 'right_hand', 'device': 'Tube Light', 'state': 'toggle'}
                elif event_code == 9:  # 771 - Feet motor imagery
                    return {'action': 'switch_device', 'type': 'feet', 'device': 'Fan', 'state': 'toggle'}
                elif event_code == 10:  # 772 - Tongue motor imagery
                    return {'action': 'all_off', 'type': 'tongue', 'device': 'All Devices', 'state': 'off'}
                
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
            elif action == 'switch_device':
                self.devices[device_name]['status'] = not self.devices[device_name]['status']
            elif action == 'all_off':
                # Turn off all devices for tongue motor imagery
                for device in self.devices:
                    self.devices[device]['status'] = False
                return True
            else:
                self.devices[device_name]['status'] = not self.devices[device_name]['status']
            return True
        return False
        
    def get_status(self):
        return self.devices

# Global instances
bci_processor = BCIDataProcessor()
device_controller = IoTDeviceController()
eeg_thread_started = False

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global eeg_thread_started
    print('🔗 Client connected')
    
    # Start EEG processing when first client connects
    if not eeg_thread_started:
        print('🚀 Starting EEG processing thread...')
        eeg_thread = threading.Thread(target=real_time_eeg_processing, daemon=True)
        eeg_thread.start()
        eeg_thread_started = True
    
    socketio.emit('device_status', device_controller.get_status())

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Client disconnected')

@socketio.on('toggle_device')
def handle_toggle_device(data):
    # DISABLED - Devices are now controlled by brain signals only!
    socketio.emit('activity_log', {
        'timestamp': time.strftime('%H:%M:%S'),
        'message': '⚠️ Manual control disabled - Use brain signals to control devices!'
    })
    socketio.emit('error_message', {
        'message': '🧠 Devices are controlled by brain signals only! Think of motor movements to control them.'
    })

def real_time_eeg_processing():
    """Real-time EEG processing thread"""
    print("📊 Loading BCI data in background...")
    
    if not bci_processor.load_bci_data():
        print("❌ Failed to load BCI data")
        socketio.emit('activity_log', {
            'timestamp': time.strftime('%H:%M:%S'),
            'message': 'Failed to load BCI dataset - check data file'
        })
        return
        
    print("✅ BCI data loaded successfully, starting real-time processing...")
    bci_processor.is_running = True
    
    socketio.emit('activity_log', {
        'timestamp': time.strftime('%H:%M:%S'),
        'message': 'Real BCI data loaded - A01T.gdf streaming started'
    })
    
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
                
                # Check for motor imagery events
                event = bci_processor.check_for_events()
                if event:
                    print(f"🧠 BRAIN SIGNAL DETECTED: {event}")
                    
                    device_name = event['device']
                    action = event['action']
                    
                    if device_controller.toggle_device(device_name, action):
                        socketio.emit('device_status', device_controller.get_status())
                        
                        # Create detailed brain control message
                        if action == 'all_off':
                            message = f"🧠 BRAIN CONTROL ({event['type']}): ALL DEVICES TURNED OFF"
                        else:
                            status = 'ON' if device_controller.devices[device_name]['status'] else 'OFF'
                            message = f"🧠 BRAIN CONTROL ({event['type']}): {device_name} → {status}"
                        
                        socketio.emit('activity_log', {
                            'timestamp': time.strftime('%H:%M:%S'),
                            'message': message
                        })
                        socketio.emit('bci_event', {
                            'type': event['type'],
                            'action': action,
                            'device': device_name,
                            'motor_imagery': event['type'].replace('_', ' ').title()
                        })
            
            # Sleep to simulate real-time processing (4ms = 250Hz)
            time.sleep(0.004)
            
        except Exception as e:
            print(f"❌ Error in EEG processing: {e}")
            break
    
    print("🛑 Real-time EEG processing stopped")

if __name__ == '__main__':
    print("="*60)
    print("🧠 EEG-based IoT Control System (SIMPLIFIED)")
    print("="*60)
    print("🔗 Web Interface: http://localhost:5000")
    print("📊 Using BCI Competition IV Dataset 2a (A01T.gdf)")
    print("🎮 Brain-Controlled Motor Imagery Commands:")
    print("   • Left Hand Thought  → Toggle Light Bulb")
    print("   • Right Hand Thought → Toggle Tube Light") 
    print("   • Feet Thought       → Toggle Fan")
    print("   • Tongue Thought     → Turn OFF All Devices")
    print("   📍 Manual controls are DISABLED - Brain signals control devices!")
    print("="*60)
    
    try:
        print("🚀 Starting Flask-SocketIO server...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        if bci_processor:
            bci_processor.is_running = False
