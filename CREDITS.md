# 致谢 / Credits

## 原始项目 / Original Project

本项目基于 **[btk/vectorizer](https://github.com/btk/vectorizer)** 实现，特此致谢！

This project is based on **[btk/vectorizer](https://github.com/btk/vectorizer)**. Special thanks to the original author!

### 关于原项目 / About Original Project

[btk/vectorizer](https://github.com/btk/vectorizer) 是一个基于Potrace的多色栅格到矢量追踪器，使用JavaScript实现，能够将PNG/JPG图像转换为SVG格式。

原项目的核心特性：
- 基于Potrace算法
- 支持多色图像处理
- 提供`inspectImage`和`parseImage`两个核心API
- JavaScript/Node.js实现

项目主页：[vectormaker.co](https://vectormaker.co/)

### 本项目的贡献 / Our Contributions

在原项目的基础上，我们进行了以下扩展和改进：

#### Python版本
- 完整的Python实现，保持与原项目相同的API设计
- 添加了命令行批处理功能
- 支持中文界面和文档
- 增强了颜色分析算法
- 添加了更多的矢量化选项

#### C++版本
- 高性能的原生C++实现
- 跨平台支持（macOS、Linux、Windows）
- 更优的内存管理和执行效率
- 保持了与原项目相同的核心功能
- 扩展了批处理能力

### 技术栈对比 / Technology Stack Comparison

| 特性 | btk/vectorizer (原版) | Png2Svg Python版 | Png2Svg C++版 |
|------|---------------------|-----------------|---------------|
| 语言 | JavaScript/Node.js | Python 3 | C++17 |
| 依赖 | npm packages | pip packages | stb_image |
| 性能 | 标准 | 标准 | 高性能 |
| 界面 | Web/CLI | CLI | CLI |
| 批处理 | - | ✓ | ✓ |
| 中文支持 | - | ✓ | ✓ |

### 感谢 / Thanks

感谢 [@btk](https://github.com/btk) 创建了优秀的vectorizer项目，为我们提供了宝贵的设计思路和算法参考。

Thanks to [@btk](https://github.com/btk) for creating the excellent vectorizer project, which provided us with valuable design ideas and algorithm references.

### 许可证 / License

原项目和本项目均采用 MIT License 开源许可。

Both the original project and this project are licensed under the MIT License.

---

**原项目链接 / Original Project Link:**
- GitHub: https://github.com/btk/vectorizer
- Website: https://vectormaker.co/

**本项目链接 / This Project Link:**
- GitHub: https://github.com/[your-username]/Png2Svg
