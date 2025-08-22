cmake_minimum_required(VERSION 3.14)
project(Png2Svg VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Add include directories
include_directories(${PROJECT_SOURCE_DIR}/include)
include_directories(${PROJECT_SOURCE_DIR}/third_party)

# Download stb_image headers if not present
include(FetchContent)
FetchContent_Declare(
    stb
    GIT_REPOSITORY https://github.com/nothings/stb.git
    GIT_TAG master
)
FetchContent_MakeAvailable(stb)

# Create third_party directory and copy stb headers
file(MAKE_DIRECTORY ${PROJECT_SOURCE_DIR}/third_party)
file(COPY ${stb_SOURCE_DIR}/stb_image.h DESTINATION ${PROJECT_SOURCE_DIR}/third_party)
file(COPY ${stb_SOURCE_DIR}/stb_image_write.h DESTINATION ${PROJECT_SOURCE_DIR}/third_party)

# Find required packages
find_package(Threads REQUIRED)

# Source files
set(SOURCES
    src/main.cpp
    src/vectorizer.cpp
)

# Create executable
add_executable(png2svg ${SOURCES})

# Link libraries
target_link_libraries(png2svg PRIVATE Threads::Threads)

# Platform-specific settings
if(APPLE)
    # macOS specific settings
    target_compile_options(png2svg PRIVATE -Wall -Wextra -O2)
elseif(UNIX)
    # Linux specific settings
    target_compile_options(png2svg PRIVATE -Wall -Wextra -O2)
    target_link_libraries(png2svg PRIVATE stdc++fs)
elseif(WIN32)
    # Windows specific settings
    target_compile_options(png2svg PRIVATE /W4 /O2)
endif()

# Install rules
install(TARGETS png2svg
    RUNTIME DESTINATION bin
)

# Create uninstall target
if(NOT TARGET uninstall)
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake.in"
        "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
        IMMEDIATE @ONLY)

    add_custom_target(uninstall
        COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake)
endif()

# Print build configuration
message(STATUS "")
message(STATUS "Build configuration:")
message(STATUS "  C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  Install Prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "")
message(STATUS "Dependencies:")
message(STATUS "  Threads: Found")
message(STATUS "  stb_image: Will be downloaded")
message(STATUS "")
message(STATUS "IMPORTANT: This program requires 'potrace' to be installed separately!")
message(STATUS "  macOS: brew install potrace")
message(STATUS "  Ubuntu/Debian: sudo apt-get install potrace")
message(STATUS "  Windows: Download from http://potrace.sourceforge.net/")
message(STATUS "")
