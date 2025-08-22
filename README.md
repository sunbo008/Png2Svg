# SVG生成脚本使用说明

## 功能介绍
这套脚本将PNG图像转换为高质量的SVG矢量图，具体步骤包括：
1. 将PNG转换为二值图像
2. 使用potrace进行矢量化
3. 修复SVG填充，移除背景，只保留文字部分
4. 添加白色背景

## 主要功能更新 ✨

### 增强版Python脚本 (`generate_svg_complete.py`)
现已支持以下功能：
- **单文件处理**: 处理单个PNG文件
- **批量处理**: 处理整个目录中的PNG文件
- **递归处理**: 可递归处理子目录
- **自定义输出**: 指定输出目录
- **阈值调整**: 动态调整二值化阈值
- **临时文件管理**: 可选择保留或清理临时文件
- **安静模式**: 减少输出信息

## 使用方法

### 基本用法
```bash
python3 generate_svg_complete.py [选项] <输入路径>
```

### 参数说明
- `<输入路径>`: PNG文件路径或包含PNG文件的目录路径

### 选项说明
| 选项 | 长选项 | 说明 |
|------|--------|------|
| `-h` | `--help` | 显示帮助信息 |
| `-r` | `--recursive` | 递归处理子目录（仅目录模式） |
| `-o` | `--output` | 指定输出目录 |
| `-k` | `--keep` | 保留临时文件（不清理） |
| `-q` | `--quiet` | 安静模式（减少输出） |
| `-t` | `--threshold` | 设置二值化阈值（默认: 50） |

### 使用示例

#### 1. 处理单个文件
```bash
# 基本用法 - 在同目录生成SVG
python3 generate_svg_complete.py image.png

# 指定输出目录
python3 generate_svg_complete.py -o ./output/ image.png

# 调整阈值（30%，保留更多细节）
python3 generate_svg_complete.py -t 30 image.png

# 保留临时文件供调试
python3 generate_svg_complete.py -k image.png
```

#### 2. 批量处理目录
```bash
# 处理目录中的所有PNG
python3 generate_svg_complete.py ./images/

# 递归处理所有子目录
python3 generate_svg_complete.py -r ./images/

# 批量处理并输出到指定目录
python3 generate_svg_complete.py -o ./svg_output/ ./png_input/

# 安静模式批量处理
python3 generate_svg_complete.py -q ./images/
```

#### 3. 组合使用
```bash
# 递归处理，自定义阈值，保留临时文件
python3 generate_svg_complete.py -r -t 40 -k ./images/

# 批量处理到输出目录，安静模式
python3 generate_svg_complete.py -q -o ./output/ ./input/
```

## 其他可用脚本

### 1. Shell脚本版本（Mac/Linux）
**文件名**: `generate_svg.sh`

```bash
./generate_svg.sh
# 或
bash generate_svg.sh
```
注：此版本仅处理固定的 `bj.png` 文件

### 2. Windows批处理版本
**文件名**: `generate_svg.bat`

```cmd
generate_svg.bat
```
注：此版本仅处理固定的 `bj.png` 文件

## 依赖要求

### 必需软件
1. **ImageMagick** - 用于图像转换
   - Mac: `brew install imagemagick`
   - Linux: `sudo apt-get install imagemagick`
   - Windows: 下载安装包

2. **Potrace** - 用于矢量化
   - Mac: `brew install potrace`
   - Linux: `sudo apt-get install potrace`
   - Windows: 下载可执行文件

3. **Python 3** - 运行Python脚本
   - 需要 Python 3.6 或更高版本

## 输入输出说明

### 输入
- 支持PNG格式图像
- 文件扩展名：`.png` 或 `.PNG`

### 输出
- SVG矢量图文件
- 文件名保持与输入相同，扩展名改为 `.svg`
- 例如：`image.png` → `image.svg`

### 临时文件
处理过程中会生成临时文件：
- `*_binary.pbm` - 二值化图像
- `*_inverted.svg` - 初始矢量化结果

默认自动清理，使用 `-k` 选项可保留

## 参数调整建议

### 阈值（Threshold）调整
阈值控制二值化的敏感度，影响最终效果：
- **默认值 50%**: 适合大多数情况
- **降低值（30-40%）**: 保留更多细节，适合浅色图像
- **提高值（60-70%）**: 图像更清晰，适合高对比度图像

### 最佳实践
1. **高质量源图像**: 使用分辨率高、对比度好的PNG
2. **黑白图像优先**: 黑白或灰度图像转换效果最佳
3. **测试不同阈值**: 针对不同图像测试最佳阈值
4. **批量处理前测试**: 先处理单个文件验证参数

## 故障排除

### 常见问题

1. **命令未找到错误**
   ```
   解决：确保ImageMagick和Potrace已正确安装并在PATH中
   ```

2. **Python模块错误**
   ```
   解决：确保使用Python 3.6+版本
   ```

3. **权限错误**
   ```
   解决：确保对输入文件有读权限，对输出目录有写权限
   ```

4. **输出质量问题**
   ```
   解决：调整阈值参数，使用高质量源图像
   ```

## 性能优化

### 批量处理建议
- 使用 `-q` 安静模式减少输出开销
- 合理设置阈值避免重复处理
- 考虑分批处理大量文件

### 内存使用
- 处理大图像时可能占用较多内存
- 建议处理前关闭不必要的程序

## 扩展功能

如需自定义处理流程，可以修改以下部分：

1. **修改填充颜色**: 编辑 `potrace` 命令中的 `--fillcolor` 参数
2. **调整SVG优化**: 修改 `fix_svg_fill` 函数
3. **添加图像预处理**: 在转换前添加ImageMagick命令

## 版本历史

### v2.0 (当前版本)
- 添加命令行参数支持
- 支持批量处理和递归处理
- 可自定义输出目录和阈值
- 改进错误处理和日志输出

### v1.0
- 基础PNG转SVG功能
- 固定文件名处理
- 自动填充修复

## 联系和支持

如遇到问题或需要帮助，请：
1. 检查依赖软件是否正确安装
2. 查看错误信息并参考故障排除
3. 使用 `-k` 保留临时文件以便调试
