#!/bin/bash
# Setup script for Debris Detection application
# Requires: Python 3.10+, conda (recommended), GPU with 8GB+ VRAM (recommended)

echo "=================================="
echo "Debris Detection Setup"
echo "=================================="

# Check for conda
if command -v conda &> /dev/null; then
    echo "Creating conda environment..."
    conda create -n debris_detect python=3.11 -y
    conda activate debris_detect

    # Install PyTorch with CUDA support
    conda install pytorch torchvision pytorch-cuda=12.1 -c pytorch -c nvidia -y
else
    echo "Conda not found. Using pip directly..."
    python3 -m venv debris_env
    source debris_env/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Test installation
echo "Testing installation..."
python3 -c "from samgeo.text_sam import LangSAM; print('LangSAM imported successfully')" 2>/dev/null && \
    echo "✓ SamGeo with text prompts ready" || \
    echo "⚠ Install may need GPU - try Google Colab for full functionality"

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "To run the debris detector:"
echo "  python3 debris_detector.py"
echo ""
echo "Or use the Jupyter notebook:"
echo "  jupyter lab debris_detection_notebook.ipynb"
