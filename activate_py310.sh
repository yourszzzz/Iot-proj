#!/bin/bash
# Activate Python 3.10 Virtual Environment Script
# Run this with: source activate_py310.sh

echo "🐍 Activating Python 3.10 environment for BCI Project..."

# Check if venv310 exists
if [ ! -d "venv310" ]; then
    echo "❌ Python 3.10 virtual environment not found!"
    echo "🔧 Creating new Python 3.10 virtual environment..."
    python3.10 -m venv venv310
    
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created successfully!"
    else
        echo "❌ Failed to create virtual environment. Installing Python 3.10..."
        sudo apt update && sudo apt install -y software-properties-common
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        sudo apt update && sudo apt install -y python3.10 python3.10-venv python3.10-dev python3.10-distutils
        python3.10 -m venv venv310
    fi
fi

# Activate the virtual environment
source venv310/bin/activate

# Check if packages are installed
if ! python -c "import mne" 2>/dev/null; then
    echo "📦 Installing required packages..."
    pip install --upgrade pip
    pip install numpy mne scipy matplotlib flask flask-socketio
fi

echo "✅ Python 3.10 environment is active!"
echo "🧠 MNE Version: $(python -c 'import mne; print(mne.__version__)')"
echo "🐍 Python Version: $(python --version)"
echo ""
echo "🚀 Ready to run your BCI project!"
echo "   Run: python main.py"
echo "   Or use: ./run_bci.sh"
