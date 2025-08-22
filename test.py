#!/usr/bin/env python3
"""
Test script to verify the Python vectorizer functionality.
"""

import sys

from pathlib import Path

# Test basic imports
def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        import numpy as np
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import numpy: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ PIL (Pillow) imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PIL: {e}")
        return False
    
    try:
        from sklearn.cluster import KMeans
        print("✓ scikit-learn imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import scikit-learn: {e}")
        return False
    
    try:
        from colorthief import ColorThief
        print("✓ colorthief imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import colorthief: {e}")
        return False
    
    try:
        from scipy.spatial import distance
        print("✓ scipy imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import scipy: {e}")
        return False
    
    try:
        from vectorizer import Vectorizer, inspect_image, parse_image
        print("✓ vectorizer module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import vectorizer: {e}")
        return False
    
    return True


def test_potrace():
    """Test if potrace is installed."""
    print("\nTesting potrace installation...")
    import subprocess
    try:
        result = subprocess.run(['potrace', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ potrace is installed")
            print(f"  Version info: {result.stdout.strip()}")
            return True
        else:
            print("✗ potrace command failed")
            return False
    except FileNotFoundError:
        print("✗ potrace is not installed")
        print("  Please install potrace:")
        print("  - macOS: brew install potrace")
        print("  - Ubuntu/Debian: sudo apt-get install potrace")
        print("  - Windows: Download from http://potrace.sourceforge.net/")
        return False


def test_vectorizer_functions():
    """Test the main vectorizer functions."""
    print("\nTesting vectorizer functions...")
    
    try:
        from vectorizer import Vectorizer
        v = Vectorizer()
        
        # Test hex_to_rgb
        rgb = v.hex_to_rgb("#FF0000")
        assert rgb == (255, 0, 0), f"hex_to_rgb failed: expected (255, 0, 0), got {rgb}"
        print("✓ hex_to_rgb works correctly")
        
        # Test rgb_to_hex
        hex_color = v.rgb_to_hex((255, 0, 0))
        assert hex_color == "#ff0000", f"rgb_to_hex failed: expected #ff0000, got {hex_color}"
        print("✓ rgb_to_hex works correctly")
        
        # Test combine_opacity
        combined = v.combine_opacity(0.5, 0.5)
        assert abs(combined - 0.75) < 0.01, f"combine_opacity failed: expected 0.75, got {combined}"
        print("✓ combine_opacity works correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing vectorizer functions: {e}")
        return False


def test_with_sample_image():
    """Test with a sample image if available."""
    print("\nTesting with sample image...")
    
    # Create a simple test image
    try:
        from PIL import Image
        import numpy as np
        
        # Create a simple 100x100 test image
        img_array = np.zeros((100, 100, 3), dtype=np.uint8)
        # Add some colored rectangles
        img_array[10:40, 10:40] = [255, 0, 0]  # Red
        img_array[60:90, 10:40] = [0, 255, 0]  # Green
        img_array[10:40, 60:90] = [0, 0, 255]  # Blue
        img_array[60:90, 60:90] = [255, 255, 0]  # Yellow
        
        img = Image.fromarray(img_array)
        test_image_path = Path("test_sample.png")
        img.save(test_image_path)
        print(f"✓ Created test image: {test_image_path}")
        
        # Test inspect_image
        from vectorizer import inspect_image
        options = inspect_image("test_sample")
        print(f"✓ inspect_image returned {len(options)} options")
        for i, opt in enumerate(options):
            print(f"  Option {i}: step={opt['step']}, colors={opt['colors']}")
        
        # Clean up test image
        test_image_path.unlink()
        print("✓ Cleaned up test image")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in sample image test: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Python Vectorizer Test Suite")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test potrace
    if not test_potrace():
        all_passed = False
    
    # Test vectorizer functions
    if not test_vectorizer_functions():
        all_passed = False
    
    # Test with sample image
    if not test_with_sample_image():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nMake sure to install all dependencies:")
        print("  pip install -r requirements.txt")
    print("=" * 50)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
