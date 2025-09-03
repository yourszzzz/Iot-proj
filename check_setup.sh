#!/bin/bash
# Check Python 3.10 setup status

echo "🔍 Python 3.10 BCI Environment Status Check"
echo "============================================"

# Check if Python 3.10 is installed
if command -v python3.10 &> /dev/null; then
    echo "✅ Python 3.10 installed: $(python3.10 --version)"
else
    echo "❌ Python 3.10 not found"
fi

# Check if virtual environment exists
if [ -d "venv310" ]; then
    echo "✅ Virtual environment exists: venv310/"
    
    # Activate and check packages
    source venv310/bin/activate
    echo "✅ Python in venv: $(python --version)"
    
    # Check key packages
    if python -c "import mne" 2>/dev/null; then
        echo "✅ MNE installed: $(python -c 'import mne; print(mne.__version__)')"
    else
        echo "❌ MNE not installed"
    fi
    
    if python -c "import flask" 2>/dev/null; then
        echo "✅ Flask installed: $(python -c 'import flask; print(flask.__version__)')"
    else
        echo "❌ Flask not installed"
    fi
    
    if python -c "import numpy" 2>/dev/null; then
        echo "✅ NumPy installed: $(python -c 'import numpy; print(numpy.__version__)')"
    else
        echo "❌ NumPy not installed"
    fi
    
else
    echo "❌ Virtual environment not found: venv310/"
fi

echo ""
echo "🚀 To run BCI project: ./run_bci.sh"
echo "🔧 To activate environment: source activate_py310.sh"
