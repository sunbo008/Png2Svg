# Makefile for Png2Svg C++ version

# Compiler settings
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
INCLUDES = -I./include -I./third_party
LDFLAGS = 

# Platform-specific settings
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    LDFLAGS += -lstdc++fs -pthread
endif
ifeq ($(UNAME_S),Darwin)
    LDFLAGS += -pthread
endif

# Directories
SRC_DIR = src
INC_DIR = include
BUILD_DIR = build
BIN_DIR = $(BUILD_DIR)/bin
OBJ_DIR = $(BUILD_DIR)/obj
THIRD_PARTY_DIR = third_party

# Files
SOURCES = $(wildcard $(SRC_DIR)/*.cpp)
OBJECTS = $(patsubst $(SRC_DIR)/%.cpp,$(OBJ_DIR)/%.o,$(SOURCES))
EXECUTABLE = $(BIN_DIR)/png2svg

# Default target
all: download_deps $(EXECUTABLE)

# Download dependencies
download_deps: $(THIRD_PARTY_DIR)/stb_image.h $(THIRD_PARTY_DIR)/stb_image_write.h

$(THIRD_PARTY_DIR)/stb_image.h:
	@echo "Downloading stb_image.h..."
	@mkdir -p $(THIRD_PARTY_DIR)
	@curl -s -o $(THIRD_PARTY_DIR)/stb_image.h https://raw.githubusercontent.com/nothings/stb/master/stb_image.h

$(THIRD_PARTY_DIR)/stb_image_write.h:
	@echo "Downloading stb_image_write.h..."
	@mkdir -p $(THIRD_PARTY_DIR)
	@curl -s -o $(THIRD_PARTY_DIR)/stb_image_write.h https://raw.githubusercontent.com/nothings/stb/master/stb_image_write.h

# Create directories
$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

$(OBJ_DIR):
	@mkdir -p $(OBJ_DIR)

# Build executable
$(EXECUTABLE): $(OBJECTS) | $(BIN_DIR)
	@echo "Linking $@..."
	@$(CXX) $(OBJECTS) -o $@ $(LDFLAGS)
	@echo "Build complete: $@"

# Compile source files
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp | $(OBJ_DIR)
	@echo "Compiling $<..."
	@$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# Run with test image
run: $(EXECUTABLE)
	@if [ -z "$(IMG)" ]; then \
		echo "Usage: make run IMG=image_name (without extension)"; \
	else \
		$(EXECUTABLE) $(IMG).png --auto; \
	fi

# Test the program
test: $(EXECUTABLE)
	@echo "Running test..."
	@$(EXECUTABLE) --help

# Clean build files
clean:
	@echo "Cleaning build files..."
	@rm -rf $(BUILD_DIR)

# Clean everything including downloaded dependencies
distclean: clean
	@echo "Cleaning downloaded dependencies..."
	@rm -rf $(THIRD_PARTY_DIR)

# Install to system
install: $(EXECUTABLE)
	@echo "Installing to /usr/local/bin..."
	@sudo cp $(EXECUTABLE) /usr/local/bin/
	@echo "Installation complete"

# Uninstall from system
uninstall:
	@echo "Uninstalling from /usr/local/bin..."
	@sudo rm -f /usr/local/bin/png2svg
	@echo "Uninstallation complete"

# Build with debug symbols
debug: CXXFLAGS = -std=c++17 -Wall -Wextra -g -O0 -DDEBUG
debug: all

# Build with CMake (alternative)
cmake-build:
	@echo "Building with CMake..."
	@mkdir -p cmake-build
	@cd cmake-build && cmake .. && make -j4
	@echo "CMake build complete: cmake-build/bin/png2svg"

# Show help
help:
	@echo "Png2Svg C++ Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all          - Build the project (default)"
	@echo "  clean        - Remove build files"
	@echo "  distclean    - Remove build files and downloaded dependencies"
	@echo "  install      - Install to /usr/local/bin"
	@echo "  uninstall    - Uninstall from /usr/local/bin"
	@echo "  debug        - Build with debug symbols"
	@echo "  test         - Run basic test"
	@echo "  run IMG=name - Run with specific image"
	@echo "  cmake-build  - Build using CMake"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make                 # Build the project"
	@echo "  make run IMG=photo   # Convert photo.png"
	@echo "  make clean          # Clean build files"
	@echo "  make install        # Install to system"

.PHONY: all clean distclean install uninstall debug test run cmake-build help download_deps
