#!/bin/bash

# Build script for Png2Svg C++ version

echo "========================================"
echo "  Png2Svg C++ Build Script"
echo "========================================"
echo ""

# Check for required tools
echo "Checking dependencies..."

# Check for C++ compiler
if ! command -v g++ &> /dev/null && ! command -v clang++ &> /dev/null; then
    echo "❌ Error: No C++ compiler found. Please install g++ or clang++."
    exit 1
fi
echo "✓ C++ compiler found"

# Check for potrace
if ! command -v potrace &> /dev/null; then
    echo "⚠️  Warning: potrace not found. Please install it:"
    echo "  macOS: brew install potrace"
    echo "  Ubuntu/Debian: sudo apt-get install potrace"
    echo "  Windows: Download from http://potrace.sourceforge.net/"
    echo ""
fi

# Check for CMake (optional)
if command -v cmake &> /dev/null; then
    echo "✓ CMake found (optional)"
    USE_CMAKE=true
else
    echo "ℹ️  CMake not found, will use Makefile"
    USE_CMAKE=false
fi

echo ""
echo "Select build method:"
echo "1) Use Makefile (simple, fast)"
echo "2) Use CMake (recommended for cross-platform)"
echo -n "Choice [1]: "
read choice

if [ "$choice" = "2" ] && [ "$USE_CMAKE" = true ]; then
    echo ""
    echo "Building with CMake..."
    echo "----------------------"
    
    # Create build directory
    mkdir -p build
    cd build
    
    # Configure
    echo "Configuring..."
    cmake -DCMAKE_BUILD_TYPE=Release ..
    
    if [ $? -ne 0 ]; then
        echo "❌ CMake configuration failed"
        exit 1
    fi
    
    # Build
    echo ""
    echo "Building..."
    make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)
    
    if [ $? -ne 0 ]; then
        echo "❌ Build failed"
        exit 1
    fi
    
    echo ""
    echo "✅ Build successful!"
    echo "Executable: build/bin/png2svg"
    
else
    echo ""
    echo "Building with Makefile..."
    echo "-------------------------"
    
    # Download dependencies
    echo "Downloading dependencies..."
    make download_deps
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to download dependencies"
        exit 1
    fi
    
    # Build
    echo ""
    echo "Building..."
    make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)
    
    if [ $? -ne 0 ]; then
        echo "❌ Build failed"
        exit 1
    fi
    
    echo ""
    echo "✅ Build successful!"
    echo "Executable: build/bin/png2svg"
fi

echo ""
echo "========================================"
echo "Build complete!"
echo ""
echo "To install system-wide, run:"
echo "  sudo make install"
echo ""
echo "To test the program, run:"
echo "  ./build/bin/png2svg --help"
echo "========================================"
