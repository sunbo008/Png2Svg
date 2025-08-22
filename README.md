# Png2Svg - PNG转SVG矢量化工具

基于Potrace的多色栅格到矢量追踪器的Python实现。输入PNG图像，输出SVG矢量图。

## 功能特性

- 🎨 **多色支持** - 自动检测并保留图像中的多种颜色
- 🔍 **智能分析** - 自动分析图像并提供多种矢量化选项
- 📐 **高质量输出** - 生成优化的SVG矢量图形
- 🎯 **灵活配置** - 可自定义颜色数量和处理步骤
- 📁 **批量处理** - 支持单文件或整个目录的批量转换
- 🚀 **智能输出** - 单文件同目录生成，批量处理输出到子目录
- 💡 **友好提示** - 无参数时显示详细的使用说明

## 安装

### 系统依赖

首先需要安装Potrace（用于栅格到矢量的转换）：

**macOS:**
```bash
brew install potrace
```

**Ubuntu/Debian:**
```bash
sudo apt-get install potrace
```

**Windows:**
从 [Potrace官网](http://potrace.sourceforge.net/) 下载并安装

### Python包安装

安装Python依赖：

```bash
pip install -r requirements.txt
```

或使用安装脚本：

```bash
./install.sh
```

## 使用方法

### 命令行使用

```bash
# 显示使用帮助
python main.py

# 转换单个PNG文件（自动模式）
python main.py /path/to/image.png --auto

# 转换单个PNG文件（交互式选择）
python main.py /path/to/image.png

# 批量转换目录中所有PNG文件
python main.py /path/to/directory --auto

# 查看文件的矢量化选项
python main.py /path/to/image.png --inspect-only
```

### 批量转换脚本

```bash
# 使用便捷脚本批量转换
./batch_convert.sh /path/to/directory

# 转换当前目录
./batch_convert.sh
```

### Python模块使用

```python
from vectorizer import inspect_image, parse_image

def convert_image():
    # 分析图像，获取可用的矢量化选项
    options = inspect_image("image_name")
    print(f"可用选项: {options}")
    
    # 选择一个选项进行转换
    if options:
        option = options[0]  # 使用第一个选项
        parse_image("image_name", option['step'], option['colors'])
        print("转换完成！")

# 运行函数
convert_image()
```

## API参考

### `inspect_image(image_name: str)`

分析图像并返回可能的矢量化选项。

**参数:**
- `image_name`: 图像文件名（不含扩展名）

**返回:**
- 选项列表，每个选项包含：
  - `step`: 颜色层级数
  - `colors`: 使用的颜色列表

### `parse_image(image_name: str, step: int, colors: List[str])`

将图像转换为SVG矢量图。

**参数:**
- `image_name`: 图像文件名（不含扩展名）
- `step`: 颜色层级数（1-4）
- `colors`: 要使用的颜色列表（十六进制格式）

**返回:**
- SVG内容字符串

## 项目结构

```
Png2Svg/
├── vectorizer.py      # 核心矢量化功能
├── main.py           # 命令行接口（支持文件/目录）
├── example.py        # 使用示例
├── test.py          # 测试脚本
├── batch_convert.sh  # 批量转换脚本
├── requirements.txt  # Python依赖
├── install.sh       # 快速安装脚本
├── Makefile         # 构建工具
└── README.md        # 本文档
```

## 工作原理

1. **图像分析**: 使用ColorThief提取图像的主要颜色
2. **颜色分类**: 根据色相、饱和度和亮度判断图像类型（黑白、单色或多色）
3. **矢量化处理**: 使用Potrace将栅格图像转换为矢量路径
4. **颜色映射**: 将SVG中的颜色映射到原始图像的颜色
5. **优化输出**: 优化SVG代码并添加viewBox以支持缩放

## 输出规则

- **单文件模式**: SVG生成在PNG文件的同目录下
- **目录批量模式**: SVG保存到 `svg_output` 子目录中

## 示例

```bash
# 转换单个文件
python main.py photo.png --auto

# 批量转换目录
python main.py ./images --auto

# 使用Makefile
make run IMG=photo
```

## 依赖说明

- **Pillow**: 图像处理和操作
- **numpy**: 数组和数值计算
- **scikit-learn**: 颜色聚类（KMeans）
- **scipy**: 颜色距离计算
- **colorthief**: 提取图像主要颜色
- **lxml**: XML/SVG处理（可选）
- **potrace**: 外部依赖，用于实际的矢量化

## 许可证

MIT License

## 贡献

欢迎提交问题和拉取请求！

## 注意事项

- 确保输入图像为PNG格式
- 大图像可能需要较长处理时间
- 颜色越复杂，处理时间越长
- 建议图像大小小于2000x2000像素以获得最佳性能