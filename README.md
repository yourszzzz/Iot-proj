# 🧠 BCI IoT Control System - EEG-based Device Control
check the output on - https://iot-proj-1.onrender.com
This project processes real EEG data to control IoT devices based on brain activity patterns using motor imagery.

## 🚀 Quick Start

**Just run this command:**
```bash
./start.sh
```

**Or alternatively:**
```bash
./run_bci.sh
```

## 🔧 Technical Setup

✅ **Python 3.10.18** - Automatically installed and configured  
✅ **MNE 1.10.1** - For EEG data processing  
✅ **Virtual Environment** - `venv310/` with all dependencies  
✅ **One-click launcher** - No manual setup needed

## 🎮 How to Use

### 🌟 **Main Application:**
```bash
python main.py
```
- Real-time EEG processing with BCI Competition IV dataset
- Web interface at **http://localhost:5000**
- Brain-controlled IoT device simulation
- Motor imagery detection (left hand, right hand, feet, tongue)

## ✅ What This System Does

✅ **Real BCI data processing** - BCI Competition IV Dataset 2a  
✅ **Motor imagery detection** - Left/right hand, feet, tongue movements  
✅ **Web interface** - Real-time visualization and control  
✅ **IoT device simulation** - Light bulbs, fans, switches  
✅ **One-click setup** - No manual environment configuration  

## 📁 Project Structure
- `start.sh` - **One-click launcher** (recommended)
- `run_bci.sh` - Quick run script  
- `activate_py310.sh` - Python 3.10 environment setup
- `main.py` - **Main BCI application**
- `venv310/` - Python 3.10 virtual environment
- `data/BCICIV_2a_gdf/` - Real BCI Competition IV dataset
- `templates/index.html` - Web interface template

## 🧠 How It Works
The system processes real EEG data by:
1. Loading BCI Competition IV Dataset 2a (real human brain signals)
2. Detecting motor imagery events (imagined movements)
3. Classifying brain signals: left hand, right hand, feet, tongue
4. Controlling virtual IoT devices based on detected brain patterns
5. Providing real-time feedback through web interface

## 🎯 Brain Control Commands
- **Left Hand Imagery** → Toggle Light Bulb
- **Right Hand Imagery** → Toggle Tube Light  
- **Feet Imagery** → Toggle Fan
- **Tongue Imagery** → Turn OFF All Devices

## 🌐 Web Interface
Access the real-time brain-computer interface at:
**http://localhost:5000**

## 📊 Technical Stack
- **Python 3.10.18** - Required for MNE compatibility
- **MNE 1.10.1** - EEG data processing and analysis
- **Flask + SocketIO** - Real-time web interface
- **NumPy, SciPy** - Scientific computing
- **Real EEG Data** - BCI Competition IV Dataset 2a

## 🔧 Environment Management
- **Check setup:** `./check_setup.sh`
- **Activate environment:** `source activate_py310.sh`
- **Space usage:** ~337MB for complete environment
2. Detecting event markers in the signal
3. Mapping different event codes to device actions:
   - Event 1: Device ON
   - Event 2: Device OFF  
   - Event 3: Device ACTION
   - Event 4: Device STOP

**Run `python test_main.py` or `python main.py` to see it in action!**
