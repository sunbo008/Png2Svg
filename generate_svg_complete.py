#!/usr/bin/env python3
"""
完整的SVG生成脚本
结合图像转换、矢量化和填充修复
支持单文件、批量处理和目录扫描
"""

import subprocess
import os
import sys
import xml.etree.ElementTree as ET
import re
import argparse
from pathlib import Path

# 全局阈值变量
THRESHOLD = 50

def run_command(cmd, description, quiet=False):
    """运行命令并返回结果"""
    if not quiet:
        print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            if not quiet:
                print(f"✓ {description}成功")
            return True
        else:
            if not quiet:
                print(f"✗ {description}失败")
                if result.stderr:
                    print(f"错误信息: {result.stderr}")
            return False
    except Exception as e:
        if not quiet:
            print(f"✗ 执行命令失败: {e}")
        return False

def fix_svg_fill(input_file, output_file):
    """
    修复SVG，确保只有文字部分被填充
    """
    print(f"\n修复SVG填充...")
    try:
        # 解析SVG
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        # 注册命名空间
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        
        # 查找所有path元素
        paths_to_remove = []
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if tag == 'path':
                # 检查path的d属性
                d = elem.get('d', '')
                
                # 如果path是整个画布的矩形（通常以M0开始，包含l0 -整个高度），移除它
                if re.match(r'^[Mm]\s*0\s+\d+\s+[lL]\s*0\s+-\d+', d):
                    # 这是背景矩形，标记为删除
                    paths_to_remove.append(elem)
                    continue
                
                # 确保其他path有正确的填充
                elem.set('fill', '#000000')
                elem.set('fill-opacity', '1')
                elem.set('stroke', 'none')
                elem.set('fill-rule', 'evenodd')
        
        # 移除背景path
        for path in paths_to_remove:
            parent = None
            for p in root.iter():
                if path in list(p):
                    parent = p
                    break
            if parent is not None:
                parent.remove(path)
        
        # 确保g元素有正确的填充属性
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag == 'g':
                elem.set('fill', '#000000')
                elem.set('stroke', 'none')
        
        # 添加白色背景矩形作为第一个元素
        viewbox = root.get('viewBox')
        if viewbox:
            parts = viewbox.split()
            if len(parts) == 4:
                # 创建白色背景
                rect = ET.Element('rect', {
                    'x': '0',
                    'y': '0',
                    'width': parts[2],
                    'height': parts[3],
                    'fill': 'white'
                })
                root.insert(0, rect)
        
        # 保存修改后的SVG
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        print(f"✓ 已修复SVG: {output_file}")
        return True
    except Exception as e:
        print(f"✗ 修复SVG失败: {e}")
        return False

def view_svg_head(filename, lines=25):
    """查看SVG文件的前几行"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.readlines()
            print(f"\n=== {filename} (前{lines}行) ===")
            for i, line in enumerate(content[:lines], 1):
                print(line.rstrip())
            if len(content) > lines:
                print(f"... (文件共{len(content)}行)")
    except Exception as e:
        print(f"无法读取文件 {filename}: {e}")

def process_single_png(input_path, output_dir=None, verbose=True, clean_temp=True):
    """
    处理单个PNG文件
    """
    input_path = Path(input_path)
    
    # 确定输出目录和文件名
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = input_path.parent
    
    # 生成文件名
    base_name = input_path.stem
    binary_file = output_dir / f"{base_name}_binary.pbm"
    inverted_svg = output_dir / f"{base_name}_inverted.svg"
    final_svg = output_dir / f"{base_name}.svg"
    
    if verbose:
        print(f"\n处理文件: {input_path}")
        print(f"输出到: {final_svg}")
    
    # 步骤1: 转换PNG为二值PBM
    cmd1 = f"convert '{input_path}' -colorspace Gray -threshold {THRESHOLD}% '{binary_file}'"
    if not run_command(cmd1, "步骤1: 将PNG转换为二值PBM", quiet=not verbose):
        return False
    
    # 步骤2: 使用potrace生成反色SVG
    cmd2 = f"potrace -s -i --fillcolor '#000000' -o '{inverted_svg}' '{binary_file}'"
    if not run_command(cmd2, "步骤2: 使用potrace生成SVG", quiet=not verbose):
        return False
    
    # 步骤3: 修复SVG填充
    if not fix_svg_fill(str(inverted_svg), str(final_svg)):
        return False
    
    # 清理临时文件
    if clean_temp:
        try:
            if binary_file.exists():
                binary_file.unlink()
            if inverted_svg.exists():
                inverted_svg.unlink()
            if verbose:
                print(f"✓ 已清理临时文件")
        except Exception as e:
            print(f"警告: 清理临时文件失败: {e}")
    
    if verbose:
        print(f"✓ 成功生成: {final_svg}")
    
    return True

def process_directory(dir_path, recursive=False, clean_temp=True):
    """
    处理目录中的所有PNG文件
    """
    dir_path = Path(dir_path)
    
    if not dir_path.is_dir():
        print(f"✗ 错误: {dir_path} 不是有效的目录")
        return False
    
    # 查找PNG文件
    if recursive:
        png_files = list(dir_path.rglob("*.png")) + list(dir_path.rglob("*.PNG"))
    else:
        png_files = list(dir_path.glob("*.png")) + list(dir_path.glob("*.PNG"))
    
    if not png_files:
        print(f"✗ 未在目录 {dir_path} 中找到PNG文件")
        return False
    
    print(f"\n找到 {len(png_files)} 个PNG文件")
    print("===================================")
    
    success_count = 0
    fail_count = 0
    
    for i, png_file in enumerate(png_files, 1):
        print(f"\n[{i}/{len(png_files)}] 处理: {png_file.name}")
        print("-" * 35)
        
        if process_single_png(png_file, verbose=False, clean_temp=clean_temp):
            success_count += 1
            print(f"✓ 成功: {png_file.stem}.svg")
        else:
            fail_count += 1
            print(f"✗ 失败: {png_file.name}")
    
    print("\n===================================")
    print(f"处理完成: 成功 {success_count} 个, 失败 {fail_count} 个")
    
    return fail_count == 0

def show_usage():
    """
    显示使用说明
    """
    usage_text = """
╔════════════════════════════════════════════════════════════════╗
║               PNG转SVG矢量化工具 - 使用说明                       ║
╚════════════════════════════════════════════════════════════════╝

用法:
    python3 generate_svg_complete.py [选项] <输入路径>

参数:
    <输入路径>        PNG文件路径或包含PNG文件的目录路径

选项:
    -h, --help       显示帮助信息
    -r, --recursive  递归处理子目录（仅用于目录模式）
    -o, --output     指定输出目录
    -k, --keep       保留临时文件（不清理）
    -q, --quiet      安静模式（减少输出）
    -t, --threshold  设置二值化阈值（默认: 50%）

示例:
    # 处理单个文件
    python3 generate_svg_complete.py image.png
    
    # 处理目录中的所有PNG
    python3 generate_svg_complete.py ./images/
    
    # 递归处理目录及子目录
    python3 generate_svg_complete.py -r ./images/
    
    # 指定输出目录
    python3 generate_svg_complete.py -o ./output/ image.png
    
    # 保留临时文件
    python3 generate_svg_complete.py -k image.png
    
    # 调整阈值（更低的值保留更多细节）
    python3 generate_svg_complete.py -t 30 image.png

输出文件:
    - 同名SVG文件将生成在源文件相同目录（或指定的输出目录）
    - 例如: image.png → image.svg

依赖要求:
    - ImageMagick (convert命令)
    - Potrace (potrace命令)
    - Python 3.x
"""
    print(usage_text)

def main():
    """主函数"""
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description='PNG转SVG矢量化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )
    
    parser.add_argument('input_path', nargs='?', help='PNG文件或目录路径')
    parser.add_argument('-h', '--help', action='store_true', help='显示帮助信息')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    parser.add_argument('-o', '--output', help='指定输出目录')
    parser.add_argument('-k', '--keep', action='store_true', help='保留临时文件')
    parser.add_argument('-q', '--quiet', action='store_true', help='安静模式')
    parser.add_argument('-t', '--threshold', type=int, default=50, help='二值化阈值(百分比)')
    
    args = parser.parse_args()
    
    # 如果没有参数或请求帮助，显示用法
    if args.help or not args.input_path:
        show_usage()
        sys.exit(0)
    
    # 设置全局阈值（这里简化处理，实际使用时需要修改run_command函数）
    global THRESHOLD
    THRESHOLD = args.threshold
    
    input_path = Path(args.input_path)
    
    # 检查输入路径是否存在
    if not input_path.exists():
        print(f"✗ 错误: 路径 '{input_path}' 不存在")
        sys.exit(1)
    
    print("===================================")
    print("    PNG转SVG矢量化工具")
    print("===================================")
    
    # 判断是文件还是目录
    if input_path.is_file():
        # 检查是否为PNG文件
        if input_path.suffix.lower() not in ['.png']:
            print(f"✗ 错误: '{input_path}' 不是PNG文件")
            sys.exit(1)
        
        # 处理单个文件
        success = process_single_png(
            input_path, 
            output_dir=args.output,
            verbose=not args.quiet,
            clean_temp=not args.keep
        )
        
        if success:
            print("\n✓ 处理完成")
            sys.exit(0)
        else:
            print("\n✗ 处理失败")
            sys.exit(1)
    
    elif input_path.is_dir():
        # 处理目录
        success = process_directory(
            input_path,
            recursive=args.recursive,
            clean_temp=not args.keep
        )
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    
    else:
        print(f"✗ 错误: '{input_path}' 既不是文件也不是目录")
        sys.exit(1)

if __name__ == "__main__":
    main()
