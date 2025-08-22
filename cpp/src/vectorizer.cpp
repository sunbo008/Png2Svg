#include "vectorizer.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <regex>
#include <cmath>
#include <algorithm>
#include <filesystem>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <stdexcept>
#include <array>
#include <random>
#include <set>
#include <map>

// For image processing, we'll use stb_image
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

namespace fs = std::filesystem;

// Custom deleter for stbi_load allocated memory
struct StbiDeleter {
    void operator()(unsigned char* p) const {
        if (p) stbi_image_free(p);
    }
};

// Alias for smart pointer with stbi images
using StbiImagePtr = std::unique_ptr<unsigned char[], StbiDeleter>;

Vectorizer::Vectorizer() {
    // Constructor
}

Vectorizer::~Vectorizer() {
    // Destructor
}

std::tuple<int, int, int> Vectorizer::hexToRgb(const std::string& hexColor) {
    std::string hex = hexColor;
    
    // Remove '#' if present
    if (hex[0] == '#') {
        hex = hex.substr(1);
    }
    
    // Handle 3-character hex codes
    if (hex.length() == 3) {
        std::string expanded;
        for (char c : hex) {
            expanded += c;
            expanded += c;
        }
        hex = expanded;
    }
    
    int r = std::stoi(hex.substr(0, 2), nullptr, 16);
    int g = std::stoi(hex.substr(2, 2), nullptr, 16);
    int b = std::stoi(hex.substr(4, 2), nullptr, 16);
    
    return std::make_tuple(r, g, b);
}

std::string Vectorizer::rgbToHex(int r, int g, int b) {
    char buffer[8];
    snprintf(buffer, sizeof(buffer), "#%02x%02x%02x", r, g, b);
    return std::string(buffer);
}

std::string Vectorizer::rgbToHex(const std::tuple<int, int, int>& rgb) {
    return rgbToHex(std::get<0>(rgb), std::get<1>(rgb), std::get<2>(rgb));
}

std::string Vectorizer::rgbaToHex(int r, int g, int b, float a) {
    // Blend with white background
    r = static_cast<int>(a * r + (1 - a) * 255);
    g = static_cast<int>(a * g + (1 - a) * 255);
    b = static_cast<int>(a * b + (1 - a) * 255);
    return rgbToHex(r, g, b);
}

float Vectorizer::combineOpacity(float a, float b) {
    return 1 - (1 - a) * (1 - b);
}

std::string Vectorizer::getSolid(const std::string& svgContent, bool stroke) {
    std::string result = svgContent;
    
    // Remove fill="black" attributes
    result = std::regex_replace(result, std::regex("fill=\"black\""), "");
    
    // Find all fill-opacity attributes
    std::regex opacityPattern("fill-opacity=\"([\\d\\.]+)\"");
    std::smatch matches;
    std::set<float> uniqueOpacities;
    
    std::string temp = result;
    while (std::regex_search(temp, matches, opacityPattern)) {
        uniqueOpacities.insert(std::stof(matches[1]));
        temp = matches.suffix();
    }
    
    if (uniqueOpacities.empty()) {
        return result;
    }
    
    // Sort opacities in descending order
    std::vector<float> sortedOpacities(uniqueOpacities.begin(), uniqueOpacities.end());
    std::sort(sortedOpacities.rbegin(), sortedOpacities.rend());
    
    // Calculate true opacity and create replacements
    for (size_t i = 0; i < sortedOpacities.size(); ++i) {
        float trueOpacity = sortedOpacities[i];
        
        // Combine with lighter opacities
        for (size_t j = i + 1; j < sortedOpacities.size(); ++j) {
            trueOpacity = combineOpacity(trueOpacity, sortedOpacities[j]);
        }
        
        // Convert to hex color
        std::string hexColor = rgbaToHex(0, 0, 0, trueOpacity);
        
        // Create replacement string
        std::string oldAttr = "fill-opacity=\"" + std::to_string(sortedOpacities[i]) + "\"";
        std::string newAttr;
        
        if (stroke) {
            newAttr = "fill=\"" + hexColor + "\" stroke-width=\"1\" stroke=\"" + hexColor + "\"";
        } else {
            newAttr = "fill=\"" + hexColor + "\"";
        }
        
        // Replace in result
        size_t pos = 0;
        while ((pos = result.find(oldAttr, pos)) != std::string::npos) {
            result.replace(pos, oldAttr.length(), newAttr);
            pos += newAttr.length();
        }
    }
    
    // Remove stroke="none" attributes
    result = std::regex_replace(result, std::regex(" stroke=\"none\""), "");
    
    return result;
}

PixelData Vectorizer::getPixels(const std::string& imagePath) {
    PixelData data;
    int width, height, channels;
    
    // Load image using stb_image with smart pointer
    StbiImagePtr pixels(stbi_load(imagePath.c_str(), &width, &height, &channels, 0));
    if (!pixels) {
        throw std::runtime_error("Failed to load image: " + imagePath);
    }
    
    data.width = width;
    data.height = height;
    data.channels = channels;
    
    // Determine mode based on channels
    switch (channels) {
        case 1: data.mode = "L"; break;
        case 2: data.mode = "LA"; break;
        case 3: data.mode = "RGB"; break;
        case 4: data.mode = "RGBA"; break;
        default: data.mode = "UNKNOWN"; break;
    }
    
    // Convert to 3D vector
    data.pixels.resize(height);
    for (int y = 0; y < height; ++y) {
        data.pixels[y].resize(width);
        for (int x = 0; x < width; ++x) {
            data.pixels[y][x].resize(channels);
            for (int c = 0; c < channels; ++c) {
                data.pixels[y][x][c] = pixels[(y * width + x) * channels + c];
            }
        }
    }
    
    // No need to manually free - smart pointer handles it
    return data;
}

std::string Vectorizer::findNearestColor(const std::string& color, const std::vector<std::string>& colorList) {
    auto targetRgb = hexToRgb(color);
    double minDistance = std::numeric_limits<double>::max();
    std::string nearest = colorList[0];
    
    for (const auto& c : colorList) {
        auto cRgb = hexToRgb(c);
        
        // Calculate Euclidean distance
        double dist = std::sqrt(
            std::pow(std::get<0>(targetRgb) - std::get<0>(cRgb), 2) +
            std::pow(std::get<1>(targetRgb) - std::get<1>(cRgb), 2) +
            std::pow(std::get<2>(targetRgb) - std::get<2>(cRgb), 2)
        );
        
        if (dist < minDistance) {
            minDistance = dist;
            nearest = c;
        }
    }
    
    return nearest;
}

std::vector<std::string> Vectorizer::extractDominantColors(const PixelData& data, int numColors) {
    std::vector<std::string> dominantColors;
    
    // Simple color quantization using histogram
    // This is a simplified version - in production, you'd want to use proper K-means clustering
    std::map<std::string, int> colorCount;
    
    // Sample pixels for faster processing
    int sampleStep = std::max(1, std::min(data.width, data.height) / 100);
    
    for (int y = 0; y < data.height; y += sampleStep) {
        for (int x = 0; x < data.width; x += sampleStep) {
            if (data.channels >= 3) {
                // Skip transparent pixels if RGBA
                if (data.channels == 4 && data.pixels[y][x][3] < 128) {
                    continue;
                }
                
                // Quantize colors to reduce color space
                int r = (data.pixels[y][x][0] / 32) * 32;
                int g = (data.pixels[y][x][1] / 32) * 32;
                int b = (data.pixels[y][x][2] / 32) * 32;
                
                std::string color = rgbToHex(r, g, b);
                colorCount[color]++;
            }
        }
    }
    
    // Sort colors by frequency and take top N
    std::vector<std::pair<std::string, int>> sortedColors(colorCount.begin(), colorCount.end());
    std::sort(sortedColors.begin(), sortedColors.end(),
              [](const auto& a, const auto& b) { return a.second > b.second; });
    
    for (int i = 0; i < numColors && i < static_cast<int>(sortedColors.size()); ++i) {
        dominantColors.push_back(sortedColors[i].first);
    }
    
    return dominantColors;
}

std::string Vectorizer::replaceColors(const std::string& svgContent, const std::string& originalImagePath) {
    // Get pixel data from original image
    PixelData originalData = getPixels(originalImagePath);
    
    // Check if image is grayscale
    if (originalData.mode == "L" || originalData.mode == "LA") {
        return svgContent;
    }
    
    // Find all hex colors in SVG
    std::regex hexPattern("#([a-f0-9]{3}){1,2}\\b", std::regex::icase);
    std::set<std::string> svgColorsSet;
    std::smatch match;
    std::string temp = svgContent;
    
    while (std::regex_search(temp, match, hexPattern)) {
        svgColorsSet.insert(match[0]);
        temp = match.suffix();
    }
    
    if (svgColorsSet.empty()) {
        return svgContent;
    }
    
    std::vector<std::string> svgColors(svgColorsSet.begin(), svgColorsSet.end());
    
    // Extract dominant colors from original image
    int numColors = std::min(static_cast<int>(svgColors.size()), 5);
    std::vector<std::string> dominantColors = extractDominantColors(originalData, numColors);
    
    if (dominantColors.empty()) {
        return svgContent;
    }
    
    // Map SVG colors to dominant colors
    std::string result = svgContent;
    for (const auto& svgColor : svgColors) {
        std::string nearest = findNearestColor(svgColor, dominantColors);
        
        // Replace all occurrences
        size_t pos = 0;
        while ((pos = result.find(svgColor, pos)) != std::string::npos) {
            result.replace(pos, svgColor.length(), nearest);
            pos += nearest.length();
        }
    }
    
    return result;
}

std::string Vectorizer::viewboxify(const std::string& svgContent) {
    std::regex widthPattern("width=\"(\\d+)\"");
    std::regex heightPattern("height=\"(\\d+)\"");
    std::smatch widthMatch, heightMatch;
    
    std::string result = svgContent;
    
    if (std::regex_search(svgContent, widthMatch, widthPattern) &&
        std::regex_search(svgContent, heightMatch, heightPattern)) {
        
        std::string width = widthMatch[1];
        std::string height = heightMatch[1];
        
        std::string oldHeader = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"" + 
                                width + "\" height=\"" + height + "\">";
        std::string newHeader = "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 " + 
                                width + " " + height + "\">";
        
        size_t pos = result.find(oldHeader);
        if (pos != std::string::npos) {
            result.replace(pos, oldHeader.length(), newHeader);
        }
    }
    
    return result;
}

std::string Vectorizer::optimizeSvg(const std::string& svgContent) {
    std::string result = svgContent;
    
    // Remove excessive whitespace
    result = std::regex_replace(result, std::regex("\\s+"), " ");
    result = std::regex_replace(result, std::regex("> <"), "><");
    
    return result;
}

bool Vectorizer::runPotrace(const std::string& inputPath, const std::string& outputPath) {
    std::string command = "potrace \"" + inputPath + "\" -s -o \"" + outputPath + "\" --opttolerance 0.5";
    int result = std::system(command.c_str());
    return result == 0;
}

void Vectorizer::posterizeImage(const std::string& inputPath, const std::string& outputPath, int levels) {
    int width, height, channels;
    
    // Load image using smart pointer
    StbiImagePtr pixels(stbi_load(inputPath.c_str(), &width, &height, &channels, 0));
    
    if (!pixels) {
        throw std::runtime_error("Failed to load image for posterization");
    }
    
    // Use vector for grayscale conversion
    std::vector<unsigned char> grayPixels;
    unsigned char* workingPixels = pixels.get();
    
    // Convert to grayscale if needed
    if (channels > 1) {
        grayPixels.resize(width * height);
        for (int i = 0; i < width * height; ++i) {
            // Simple grayscale conversion
            int r = pixels[i * channels];
            int g = pixels[i * channels + 1];
            int b = pixels[i * channels + 2];
            grayPixels[i] = static_cast<unsigned char>(0.299 * r + 0.587 * g + 0.114 * b);
        }
        workingPixels = grayPixels.data();
        channels = 1;
    }
    
    // Apply posterization
    if (levels > 1) {
        int step = 256 / levels;
        for (int i = 0; i < width * height; ++i) {
            workingPixels[i] = static_cast<unsigned char>((workingPixels[i] / step) * step);
        }
    }
    
    // Save as BMP (potrace works better with BMP)
    stbi_write_bmp(outputPath.c_str(), width, height, 1, workingPixels);
}

std::string Vectorizer::parseImage(const std::string& imageName, int step, 
                                   const std::vector<std::string>& colors) {
    std::string imagePath = "./" + imageName + ".png";
    
    // Check if potrace is installed
    if (std::system("which potrace > /dev/null 2>&1") != 0) {
        throw std::runtime_error("Potrace is not installed. Please install it first.");
    }
    
    // Create temporary BMP file
    std::string tempBmpPath = "/tmp/" + imageName + "_temp.bmp";
    
    // Posterize if needed
    if (step > 1) {
        posterizeImage(imagePath, tempBmpPath, step);
    } else {
        // Just convert to BMP
        int width, height, channels;
        
        // Use smart pointer for image loading
        StbiImagePtr pixels(stbi_load(imagePath.c_str(), &width, &height, &channels, 0));
        if (!pixels) {
            throw std::runtime_error("Failed to load image");
        }
        
        // Convert to grayscale if needed using vector
        if (channels > 1) {
            std::vector<unsigned char> grayPixels(width * height);
            for (int i = 0; i < width * height; ++i) {
                int r = pixels[i * channels];
                int g = (channels > 1) ? pixels[i * channels + 1] : r;
                int b = (channels > 2) ? pixels[i * channels + 2] : r;
                grayPixels[i] = static_cast<unsigned char>(0.299 * r + 0.587 * g + 0.114 * b);
            }
            stbi_write_bmp(tempBmpPath.c_str(), width, height, 1, grayPixels.data());
        } else {
            stbi_write_bmp(tempBmpPath.c_str(), width, height, 1, pixels.get());
        }
    }
    
    // Run potrace
    std::string tempSvgPath = "/tmp/" + imageName + "_temp.svg";
    if (!runPotrace(tempBmpPath, tempSvgPath)) {
        std::remove(tempBmpPath.c_str());
        throw std::runtime_error("Potrace failed");
    }
    
    // Read SVG content
    std::ifstream svgFile(tempSvgPath);
    std::string svgContent((std::istreambuf_iterator<char>(svgFile)),
                           std::istreambuf_iterator<char>());
    svgFile.close();
    
    // Clean up temporary files
    std::remove(tempBmpPath.c_str());
    std::remove(tempSvgPath.c_str());
    
    // Process the SVG
    svgContent = getSolid(svgContent, step != 1);
    
    if (step == 1 && !colors.empty()) {
        // Replace black with specified color
        svgContent = std::regex_replace(svgContent, std::regex("#000000"), colors[0]);
    } else if (step > 1) {
        // Replace colors based on original image
        svgContent = replaceColors(svgContent, imagePath);
    }
    
    // Optimize and viewboxify
    svgContent = optimizeSvg(svgContent);
    svgContent = viewboxify(svgContent);
    
    // Save the result
    std::string outputPath = "./" + imageName + ".svg";
    std::ofstream outFile(outputPath);
    outFile << svgContent;
    outFile.close();
    
    std::cout << "SVG saved to " << outputPath << std::endl;
    return svgContent;
}

std::vector<VectorizationOption> Vectorizer::inspectImage(const std::string& imageName) {
    std::string imagePath = "./" + imageName + ".png";
    std::vector<VectorizationOption> options;
    
    // Get pixel data
    PixelData data = getPixels(imagePath);
    
    // Extract dominant colors (simplified version)
    std::vector<std::string> palette = extractDominantColors(data, 5);
    
    if (palette.empty()) {
        // Default to black
        VectorizationOption opt;
        opt.step = 1;
        opt.colors = {"#000000"};
        options.push_back(opt);
        return options;
    }
    
    // Check if first color is white (background)
    auto firstRgb = hexToRgb(palette[0]);
    bool isWhiteBackground = (std::get<0>(firstRgb) > 200 && 
                             std::get<1>(firstRgb) > 200 && 
                             std::get<2>(firstRgb) > 200);
    
    if (isWhiteBackground && palette.size() > 1) {
        palette.erase(palette.begin());
    }
    
    // Check if image is black and white
    bool isBlackAndWhite = false;
    if (!palette.empty()) {
        auto lastRgb = hexToRgb(palette.back());
        if (std::get<0>(lastRgb) < 50 && 
            std::get<1>(lastRgb) < 50 && 
            std::get<2>(lastRgb) < 50) {
            isBlackAndWhite = true;
        }
    }
    
    if (isBlackAndWhite) {
        VectorizationOption opt;
        opt.step = 1;
        opt.colors = {"#000000"};
        options.push_back(opt);
    } else {
        // Offer multiple options with different color counts
        for (int i = 1; i <= std::min(4, static_cast<int>(palette.size())); ++i) {
            VectorizationOption opt;
            opt.step = i;
            opt.colors = std::vector<std::string>(palette.begin(), palette.begin() + i);
            options.push_back(opt);
        }
    }
    
    return options;
}

// Standalone functions
std::vector<VectorizationOption> inspectImage(const std::string& imageName) {
    Vectorizer vectorizer;
    return vectorizer.inspectImage(imageName);
}

std::string parseImage(const std::string& imageName, int step, 
                      const std::vector<std::string>& colors) {
    Vectorizer vectorizer;
    return vectorizer.parseImage(imageName, step, colors);
}