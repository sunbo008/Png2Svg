#include <iostream>
#include <string>
#include <vector>
#include <filesystem>
#include <algorithm>
#include <iomanip>
#include "vectorizer.h"

namespace fs = std::filesystem;

// Process a single PNG file and convert it to SVG
bool processSingleFile(const fs::path& pngPath, bool autoSelect = true, 
                       int optionIndex = 0, bool quiet = false) {
    
    if (!fs::exists(pngPath)) {
        std::cerr << "错误: 文件不存在 - " << pngPath << std::endl;
        return false;
    }
    
    if (pngPath.extension() != ".png" && pngPath.extension() != ".PNG") {
        std::cerr << "错误: 不是PNG文件 - " << pngPath << std::endl;
        return false;
    }
    
    // Get the output SVG path (same directory as input)
    fs::path svgPath = pngPath;
    svgPath.replace_extension(".svg");
    
    // Get image name without extension
    std::string imageName = pngPath.stem().string();
    
    if (!quiet) {
        std::cout << "处理: " << pngPath << std::endl;
    }
    
    try {
        // Create temporary working directory link
        fs::path tempPng = "./" + imageName + ".png";
        fs::path tempSvg = "./" + imageName + ".svg";
        
        // Copy file to working directory if needed
        if (!fs::exists(tempPng) || !fs::equivalent(tempPng, pngPath)) {
            fs::copy_file(pngPath, tempPng, fs::copy_options::overwrite_existing);
        }
        
        // Get vectorization options
        std::vector<VectorizationOption> options = inspectImage(imageName);
        
        if (options.empty()) {
            std::cerr << "警告: 无法获取矢量化选项 - " << pngPath << std::endl;
            return false;
        }
        
        if (!quiet) {
            std::cout << "  找到 " << options.size() << " 个矢量化选项" << std::endl;
        }
        
        // Select option
        VectorizationOption selectedOption;
        if (autoSelect) {
            int idx = std::min(optionIndex, static_cast<int>(options.size() - 1));
            selectedOption = options[idx];
        } else {
            // Interactive selection
            std::cout << "  可用选项:" << std::endl;
            for (size_t i = 0; i < options.size(); ++i) {
                std::cout << "    " << i << ": Step=" << options[i].step 
                         << ", Colors=";
                for (const auto& color : options[i].colors) {
                    std::cout << color << " ";
                }
                std::cout << std::endl;
            }
            
            int choice;
            while (true) {
                std::cout << "  选择选项 (0-" << options.size() - 1 << "): ";
                std::cin >> choice;
                
                if (std::cin.good() && choice >= 0 && choice < options.size()) {
                    selectedOption = options[choice];
                    break;
                } else {
                    std::cout << "  请输入 0 到 " << options.size() - 1 
                             << " 之间的数字" << std::endl;
                    std::cin.clear();
                    std::cin.ignore(10000, '\n');
                }
            }
        }
        
        // Process the image
        parseImage(imageName, selectedOption.step, selectedOption.colors);
        
        // Move the generated SVG to the target location
        if (fs::exists(tempSvg)) {
            fs::rename(tempSvg, svgPath);
            if (!quiet) {
                std::cout << "  ✓ 生成: " << svgPath << std::endl;
            }
        }
        
        // Clean up temporary file if it was created
        if (fs::exists(tempPng) && !fs::equivalent(tempPng, pngPath)) {
            fs::remove(tempPng);
        }
        
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "错误处理 " << pngPath << ": " << e.what() << std::endl;
        return false;
    }
}

// Process all PNG files in a directory
bool processDirectory(const fs::path& dirPath, bool autoSelect = true, int optionIndex = 0) {
    
    if (!fs::exists(dirPath)) {
        std::cerr << "错误: 目录不存在 - " << dirPath << std::endl;
        return false;
    }
    
    if (!fs::is_directory(dirPath)) {
        std::cerr << "错误: 不是目录 - " << dirPath << std::endl;
        return false;
    }
    
    // Find all PNG files
    std::vector<fs::path> pngFiles;
    for (const auto& entry : fs::directory_iterator(dirPath)) {
        if (entry.is_regular_file()) {
            std::string ext = entry.path().extension().string();
            std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
            if (ext == ".png") {
                pngFiles.push_back(entry.path());
            }
        }
    }
    
    if (pngFiles.empty()) {
        std::cerr << "警告: 目录中没有PNG文件 - " << dirPath << std::endl;
        return false;
    }
    
    // Create output subdirectory
    fs::path outputDir = dirPath / "svg_output";
    fs::create_directories(outputDir);
    
    std::cout << "找到 " << pngFiles.size() << " 个PNG文件" << std::endl;
    std::cout << "输出目录: " << outputDir << std::endl;
    std::cout << std::string(50, '-') << std::endl;
    
    int successCount = 0;
    int failCount = 0;
    
    for (size_t i = 0; i < pngFiles.size(); ++i) {
        std::cout << "[" << (i + 1) << "/" << pngFiles.size() << "] " 
                 << pngFiles[i].filename() << std::endl;
        
        // Process the file
        bool success = processSingleFile(pngFiles[i], autoSelect, optionIndex, true);
        
        if (success) {
            // Move SVG to output directory
            fs::path svgFile = pngFiles[i];
            svgFile.replace_extension(".svg");
            
            if (fs::exists(svgFile)) {
                fs::path targetSvg = outputDir / svgFile.filename();
                fs::rename(svgFile, targetSvg);
                std::cout << "  ✓ 已保存到: svg_output/" << svgFile.filename() << std::endl;
                successCount++;
            }
        } else {
            std::cout << "  ✗ 转换失败" << std::endl;
            failCount++;
        }
    }
    
    std::cout << std::string(50, '-') << std::endl;
    std::cout << "完成: 成功 " << successCount << " 个, 失败 " << failCount << " 个" << std::endl;
    
    return true;
}

// Show usage information
void showUsage() {
    std::cout << R"(
╔════════════════════════════════════════════════════════════════╗
║               C++ Vectorizer - PNG转SVG工具                      ║
╚════════════════════════════════════════════════════════════════╝

用法: png2svg <文件或目录> [选项]

参数:
  <文件或目录>     PNG文件路径或包含PNG文件的目录

选项:
  --auto          自动选择第一个矢量化选项（默认交互式选择）
  --option N      与--auto配合使用，选择第N个选项（默认: 0）
  --inspect-only  仅显示可用选项，不进行转换
  --help, -h      显示此帮助信息

示例:
  # 转换单个文件（交互式）
  ./png2svg /path/to/image.png
  
  # 转换单个文件（自动）
  ./png2svg /path/to/image.png --auto
  
  # 批量转换目录中所有PNG文件
  ./png2svg /path/to/directory --auto
  
  # 查看文件的矢量化选项
  ./png2svg /path/to/image.png --inspect-only

说明:
  • 单个文件: SVG将生成在PNG文件的同目录下
  • 目录批量: SVG将保存到 svg_output 子目录中
  • 需要安装 potrace 工具
    )" << std::endl;
}

int main(int argc, char* argv[]) {
    // If no arguments, show usage
    if (argc == 1) {
        showUsage();
        return 0;
    }
    
    // Parse command line arguments
    std::string inputPath;
    bool autoSelect = false;
    int optionIndex = 0;
    bool inspectOnly = false;
    bool showHelp = false;
    
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        
        if (arg == "--help" || arg == "-h") {
            showHelp = true;
        } else if (arg == "--auto") {
            autoSelect = true;
        } else if (arg == "--option" && i + 1 < argc) {
            optionIndex = std::stoi(argv[++i]);
        } else if (arg == "--inspect-only") {
            inspectOnly = true;
        } else if (inputPath.empty() && arg[0] != '-') {
            inputPath = arg;
        }
    }
    
    // Handle help
    if (showHelp || inputPath.empty()) {
        showUsage();
        return 0;
    }
    
    // Convert input to path
    fs::path path(inputPath);
    path = fs::absolute(path);
    
    // Check if input exists
    if (!fs::exists(path)) {
        std::cerr << "错误: 路径不存在 - " << path << std::endl;
        return 1;
    }
    
    // Handle inspect-only mode
    if (inspectOnly) {
        if (fs::is_regular_file(path)) {
            if (path.extension() != ".png" && path.extension() != ".PNG") {
                std::cerr << "错误: 不是PNG文件 - " << path << std::endl;
                return 1;
            }
            
            // Get image name for inspect
            std::string imageName = path.stem().string();
            
            // Copy to working directory temporarily
            fs::path tempPng = "./" + imageName + ".png";
            if (!fs::exists(tempPng) || !fs::equivalent(tempPng, path)) {
                fs::copy_file(path, tempPng, fs::copy_options::overwrite_existing);
            }
            
            try {
                std::vector<VectorizationOption> options = inspectImage(imageName);
                
                // Print options as JSON-like format
                std::cout << "[\n";
                for (size_t i = 0; i < options.size(); ++i) {
                    std::cout << "  {\n";
                    std::cout << "    \"step\": " << options[i].step << ",\n";
                    std::cout << "    \"colors\": [";
                    for (size_t j = 0; j < options[i].colors.size(); ++j) {
                        std::cout << "\"" << options[i].colors[j] << "\"";
                        if (j < options[i].colors.size() - 1) std::cout << ", ";
                    }
                    std::cout << "]\n";
                    std::cout << "  }";
                    if (i < options.size() - 1) std::cout << ",";
                    std::cout << "\n";
                }
                std::cout << "]" << std::endl;
                
                // Clean up
                if (fs::exists(tempPng) && !fs::equivalent(tempPng, path)) {
                    fs::remove(tempPng);
                }
            } catch (const std::exception& e) {
                std::cerr << "错误: " << e.what() << std::endl;
                // Clean up
                if (fs::exists(tempPng) && !fs::equivalent(tempPng, path)) {
                    fs::remove(tempPng);
                }
                return 1;
            }
        } else {
            std::cerr << "错误: --inspect-only 只能用于单个文件" << std::endl;
            return 1;
        }
    } else {
        // Process file or directory
        if (fs::is_regular_file(path)) {
            bool success = processSingleFile(path, autoSelect, optionIndex);
            return success ? 0 : 1;
        } else if (fs::is_directory(path)) {
            bool success = processDirectory(path, autoSelect, optionIndex);
            return success ? 0 : 1;
        } else {
            std::cerr << "错误: 无法识别的输入类型 - " << path << std::endl;
            return 1;
        }
    }
    
    return 0;
}
