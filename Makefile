# Makefile for Python Vectorizer

.PHONY: help install test clean run example

# Default target
help:
	@echo "Python Vectorizer - Makefile Commands"
	@echo "====================================="
	@echo "make install    - Install Python dependencies"
	@echo "make test       - Run test suite"
	@echo "make example    - Run example code"
	@echo "make clean      - Clean temporary files"
	@echo "make run IMG=<name> - Convert image (e.g., make run IMG=test)"
	@echo ""

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip3 install -r requirements.txt
	@echo "Installation complete!"
	@echo ""
	@echo "Note: Make sure potrace is installed:"
	@echo "  macOS: brew install potrace"
	@echo "  Linux: sudo apt-get install potrace"

# Run tests
test:
	@echo "Running test suite..."
	python3 test.py

# Run example
example:
	@echo "Running example..."
	python3 example.py

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf .pytest_cache
	rm -f test_sample.png
	rm -f *.svg
	rm -f *.bmp
	@echo "Clean complete!"

# Run vectorizer on specific image
run:
ifndef IMG
	@echo "Error: Please specify image name"
	@echo "Usage: make run IMG=<image_name>"
	@echo "Example: make run IMG=test"
else
	@echo "Processing $(IMG).png..."
	python3 main.py $(IMG) --auto
endif
