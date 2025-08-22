#ifndef VECTORIZER_H
#define VECTORIZER_H

#include <string>
#include <vector>
#include <tuple>
#include <unordered_map>

// Structure to represent vectorization options
struct VectorizationOption {
    int step;
    std::vector<std::string> colors;
};

// Structure to represent pixel data
struct PixelData {
    std::vector<std::vector<std::vector<uint8_t>>> pixels;  // height x width x channels
    int width;
    int height;
    int channels;
    std::string mode;
};

class Vectorizer {
public:
    Vectorizer();
    ~Vectorizer();

    // Convert hex color to RGB tuple
    static std::tuple<int, int, int> hexToRgb(const std::string& hexColor);
    
    // Convert RGB tuple to hex color string
    static std::string rgbToHex(int r, int g, int b);
    static std::string rgbToHex(const std::tuple<int, int, int>& rgb);
    
    // Convert RGBA to hex, blending with white background
    static std::string rgbaToHex(int r, int g, int b, float a);
    
    // Combine two opacity values
    static float combineOpacity(float a, float b);
    
    // Convert opacity-based SVG to solid colors
    std::string getSolid(const std::string& svgContent, bool stroke = false);
    
    // Get pixel data from an image
    PixelData getPixels(const std::string& imagePath);
    
    // Find the nearest color from a list of colors
    std::string findNearestColor(const std::string& color, const std::vector<std::string>& colorList);
    
    // Replace colors in SVG based on the original image colors
    std::string replaceColors(const std::string& svgContent, const std::string& originalImagePath);
    
    // Convert SVG width/height to viewBox for better scaling
    std::string viewboxify(const std::string& svgContent);
    
    // Optimize SVG content
    std::string optimizeSvg(const std::string& svgContent);
    
    // Parse an image and convert it to SVG
    std::string parseImage(const std::string& imageName, int step = 3, 
                          const std::vector<std::string>& colors = {});
    
    // Inspect an image and return possible vectorization options
    std::vector<VectorizationOption> inspectImage(const std::string& imageName);

private:
    // Helper function to extract dominant colors using K-means clustering
    std::vector<std::string> extractDominantColors(const PixelData& data, int numColors);
    
    // Helper function to run potrace command
    bool runPotrace(const std::string& inputPath, const std::string& outputPath);
    
    // Helper function to posterize an image
    void posterizeImage(const std::string& inputPath, const std::string& outputPath, int levels);
};

// Standalone functions for compatibility
std::vector<VectorizationOption> inspectImage(const std::string& imageName);
std::string parseImage(const std::string& imageName, int step = 3, 
                      const std::vector<std::string>& colors = {});

#endif // VECTORIZER_H
