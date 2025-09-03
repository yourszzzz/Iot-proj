#!/bin/bash
# Quick run script for BCI Project with Python 3.10
# Makes sure environment is activated and runs the project

echo "🧠 Starting BCI IoT Control System..."

# Activate Python 3.10 environment
if [ ! -d "venv310" ]; then
    echo "🔧 Setting up Python 3.10 environment first..."
    source activate_py310.sh
else
    source venv310/bin/activate
fi

# Check if packages are available
if ! python -c "import mne, flask" 2>/dev/null; then
    echo "📦 Installing missing packages..."
    pip install numpy mne scipy matplotlib flask flask-socketio
fi

echo "🚀 Running BCI Project with Python $(python --version)..."
echo "🌐 Web interface will be available at: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Run the main BCI application
python main.py
