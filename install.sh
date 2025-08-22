#!/bin/bash
# Installation script for Python Vectorizer

echo "=================================="
echo "Python Vectorizer Installation"
echo "=================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

echo "Python version:"
python3 --version

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed."
    echo "Please install pip3."
    exit 1
fi

# Check if potrace is installed
if ! command -v potrace &> /dev/null; then
    echo "Warning: potrace is not installed."
    echo "Please install potrace:"
    echo "  - macOS: brew install potrace"
    echo "  - Ubuntu/Debian: sudo apt-get install potrace"
    echo "  - Windows: Download from http://potrace.sourceforge.net/"
    echo ""
    read -p "Continue without potrace? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "Installation completed successfully!"
    echo "=================================="
    echo ""
    echo "You can now use the vectorizer:"
    echo "  python3 main.py <image_name>"
    echo "  python3 example.py"
    echo ""
    echo "Run tests with:"
    echo "  python3 test.py"
else
    echo ""
    echo "=================================="
    echo "Installation failed!"
    echo "=================================="
    echo "Please check the error messages above."
    exit 1
fi
