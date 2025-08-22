#!/bin/bash
#
# 批量转换PNG到SVG的便捷脚本
# 用法: ./batch_convert.sh [目录路径]
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 显示帮助
show_help() {
    echo "==========================================="
    echo "     PNG批量转换SVG工具"
    echo "==========================================="
    echo ""
    echo "用法:"
    echo "  $0 [目录路径]"
    echo ""
    echo "参数:"
    echo "  目录路径    包含PNG文件的目录（默认为当前目录）"
    echo ""
    echo "示例:"
    echo "  $0                    # 转换当前目录"
    echo "  $0 ./images           # 转换images目录"
    echo "  $0 /path/to/folder    # 转换指定路径"
    echo ""
    echo "说明:"
    echo "  • SVG文件将保存到 svg_output 子目录"
    echo "  • 自动处理所有PNG文件"
    echo "  • 支持中文文件名"
    echo ""
}

# 检查Python和依赖
check_requirements() {
    print_info "检查环境..."
    
    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        print_error "Python3未安装"
        exit 1
    fi
    
    # 检查potrace
    if ! command -v potrace &> /dev/null; then
        print_warning "potrace未安装"
        echo "  请安装potrace："
        echo "  macOS: brew install potrace"
        echo "  Linux: sudo apt-get install potrace"
        read -p "是否继续？(y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_success "环境检查通过"
}

# 主函数
main() {
    # 处理参数
    if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        show_help
        exit 0
    fi
    
    # 设置目标目录
    TARGET_DIR="${1:-.}"
    
    # 转换为绝对路径
    TARGET_DIR=$(cd "$TARGET_DIR" 2>/dev/null && pwd || echo "$TARGET_DIR")
    
    # 检查目录是否存在
    if [ ! -d "$TARGET_DIR" ]; then
        print_error "目录不存在: $TARGET_DIR"
        exit 1
    fi
    
    print_info "目标目录: $TARGET_DIR"
    
    # 检查是否有PNG文件
    PNG_COUNT=$(find "$TARGET_DIR" -maxdepth 1 -name "*.png" -o -name "*.PNG" | wc -l | tr -d ' ')
    
    if [ "$PNG_COUNT" -eq 0 ]; then
        print_warning "目录中没有PNG文件"
        exit 0
    fi
    
    print_info "找到 $PNG_COUNT 个PNG文件"
    
    # 检查环境
    check_requirements
    
    echo ""
    echo "==========================================="
    echo "开始批量转换..."
    echo "==========================================="
    echo ""
    
    # 执行转换
    python3 main.py "$TARGET_DIR" --auto
    
    # 检查输出目录
    OUTPUT_DIR="$TARGET_DIR/svg_output"
    if [ -d "$OUTPUT_DIR" ]; then
        SVG_COUNT=$(find "$OUTPUT_DIR" -name "*.svg" | wc -l | tr -d ' ')
        print_success "转换完成！生成了 $SVG_COUNT 个SVG文件"
        print_info "输出目录: $OUTPUT_DIR"
        
        # 显示文件列表
        echo ""
        echo "生成的文件:"
        ls -lh "$OUTPUT_DIR"/*.svg 2>/dev/null | awk '{print "  • " $9 " (" $5 ")"}'
    else
        print_error "转换可能失败，未找到输出目录"
    fi
    
    echo ""
    echo "==========================================="
    echo "批量转换完成！"
    echo "==========================================="
}

# 运行主函数
main "$@"
