#!/bin/bash
# One-command setup and run for BCI Project
# This is the ONLY command you need to run each time!

echo "🧠 BCI IoT Control System - One-Click Launcher"
echo "==============================================="

# Auto-setup if needed
if [ ! -d "venv310" ] || ! source venv310/bin/activate 2>/dev/null || ! python -c "import mne" 2>/dev/null; then
    echo "🔧 Setting up Python 3.10 environment (one-time setup)..."
    source activate_py310.sh
else
    echo "✅ Python 3.10 environment ready!"
    source venv310/bin/activate
fi

echo "🚀 Launching BCI Project..."
echo "🌐 Web Interface: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Run the BCI application
python main.py
