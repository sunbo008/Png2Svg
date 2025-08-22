#!/usr/bin/env python3
"""
Main entry point for the Python vectorizer.
Supports single file or batch directory processing.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Optional

from vectorizer import inspect_image, parse_image, Vectorizer


def process_single_file(png_path: Path, auto_select: bool = True, option_index: int = 0, quiet: bool = False):
    """
    Process a single PNG file and convert it to SVG.
    
    Args:
        png_path: Path to the PNG file
        auto_select: Whether to automatically select the first option
        option_index: Index of the option to use (if auto_select is True)
        quiet: Suppress output messages
    """
    if not png_path.exists():
        print(f"错误: 文件不存在 - {png_path}")
        return False
    
    if png_path.suffix.lower() != '.png':
        print(f"错误: 不是PNG文件 - {png_path}")
        return False
    
    # Get the output SVG path (same directory as input)
    svg_path = png_path.with_suffix('.svg')
    
    # Get image name without extension and path
    image_name = png_path.stem
    
    if not quiet:
        print(f"处理: {png_path}")
    
    try:
        # Create temporary working directory link
        temp_png = Path(f"./{image_name}.png")
        temp_svg = Path(f"./{image_name}.svg")
        
        # Copy file to working directory if needed
        if not temp_png.exists() or not temp_png.samefile(png_path):
            import shutil
            shutil.copy2(png_path, temp_png)
        
        # Get vectorization options
        options = inspect_image(image_name)
        
        if not options:
            print(f"警告: 无法获取矢量化选项 - {png_path}")
            return False
        
        if not quiet:
            print(f"  找到 {len(options)} 个矢量化选项")
        
        # Select option
        if auto_select:
            selected_option = options[min(option_index, len(options) - 1)]
        else:
            # Interactive selection
            print(f"  可用选项:")
            for i, option in enumerate(options):
                print(f"    {i}: Step={option['step']}, Colors={option['colors']}")
            
            while True:
                try:
                    choice = input(f"  选择选项 (0-{len(options)-1}): ")
                    idx = int(choice)
                    if 0 <= idx < len(options):
                        selected_option = options[idx]
                        break
                    else:
                        print(f"  请输入 0 到 {len(options)-1} 之间的数字")
                except ValueError:
                    print("  请输入有效数字")
        
        # Process the image
        parse_image(image_name, selected_option['step'], selected_option['colors'])
        
        # Move the generated SVG to the target location
        if temp_svg.exists():
            import shutil
            shutil.move(str(temp_svg), str(svg_path))
            if not quiet:
                print(f"  ✓ 生成: {svg_path}")
        
        # Clean up temporary file if it was created
        if temp_png.exists() and not temp_png.samefile(png_path):
            temp_png.unlink()
        
        return True
        
    except Exception as e:
        print(f"错误处理 {png_path}: {e}")
        return False


def process_directory(dir_path: Path, auto_select: bool = True, option_index: int = 0):
    """
    Process all PNG files in a directory.
    
    Args:
        dir_path: Path to the directory
        auto_select: Whether to automatically select the first option
        option_index: Index of the option to use (if auto_select is True)
    """
    if not dir_path.exists():
        print(f"错误: 目录不存在 - {dir_path}")
        return False
    
    if not dir_path.is_dir():
        print(f"错误: 不是目录 - {dir_path}")
        return False
    
    # Find all PNG files
    png_files = list(dir_path.glob("*.png")) + list(dir_path.glob("*.PNG"))
    
    if not png_files:
        print(f"警告: 目录中没有PNG文件 - {dir_path}")
        return False
    
    # Create output subdirectory
    output_dir = dir_path / "svg_output"
    output_dir.mkdir(exist_ok=True)
    
    print(f"找到 {len(png_files)} 个PNG文件")
    print(f"输出目录: {output_dir}")
    print("-" * 50)
    
    success_count = 0
    fail_count = 0
    
    for i, png_file in enumerate(png_files, 1):
        print(f"[{i}/{len(png_files)}] {png_file.name}")
        
        # Process the file
        success = process_single_file(png_file, auto_select, option_index, quiet=True)
        
        if success:
            # Move SVG to output directory
            svg_file = png_file.with_suffix('.svg')
            if svg_file.exists():
                target_svg = output_dir / svg_file.name
                import shutil
                shutil.move(str(svg_file), str(target_svg))
                print(f"  ✓ 已保存到: svg_output/{svg_file.name}")
                success_count += 1
        else:
            print(f"  ✗ 转换失败")
            fail_count += 1
    
    print("-" * 50)
    print(f"完成: 成功 {success_count} 个, 失败 {fail_count} 个")
    return True


def show_usage():
    """Show usage information when no arguments are provided."""
    print("""
╔════════════════════════════════════════════════════════════════╗
║               Python Vectorizer - PNG转SVG工具                   ║
╚════════════════════════════════════════════════════════════════╝

用法: python main.py <文件或目录> [选项]

参数:
  <文件或目录>     PNG文件路径或包含PNG文件的目录

选项:
  --auto          自动选择第一个矢量化选项（默认交互式选择）
  --option N      与--auto配合使用，选择第N个选项（默认: 0）
  --inspect-only  仅显示可用选项，不进行转换

示例:
  # 转换单个文件（交互式）
  python main.py /path/to/image.png
  
  # 转换单个文件（自动）
  python main.py /path/to/image.png --auto
  
  # 批量转换目录中所有PNG文件
  python main.py /path/to/directory --auto
  
  # 查看文件的矢量化选项
  python main.py /path/to/image.png --inspect-only

说明:
  • 单个文件: SVG将生成在PNG文件的同目录下
  • 目录批量: SVG将保存到 svg_output 子目录中
  • 支持中文文件名和路径
    """)


def main():
    """Main function for command-line interface."""
    # If no arguments, show usage
    if len(sys.argv) == 1:
        show_usage()
        sys.exit(0)
    
    parser = argparse.ArgumentParser(
        description='转换PNG图像为SVG矢量图',
        add_help=False  # We'll handle help ourselves
    )
    parser.add_argument(
        'input',
        nargs='?',
        help='PNG文件或包含PNG文件的目录'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='自动选择第一个矢量化选项'
    )
    parser.add_argument(
        '--option',
        type=int,
        default=0,
        help='与--auto配合使用时选择的选项索引（默认: 0）'
    )
    parser.add_argument(
        '--inspect-only',
        action='store_true',
        help='仅检查图像并显示选项，不进行处理'
    )
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help='显示帮助信息'
    )
    
    args = parser.parse_args()
    
    # Handle help
    if args.help or not args.input:
        show_usage()
        sys.exit(0)
    
    # Convert input to Path
    input_path = Path(args.input).resolve()
    
    # Check if input exists
    if not input_path.exists():
        print(f"错误: 路径不存在 - {input_path}")
        sys.exit(1)
    
    # Handle inspect-only mode
    if args.inspect_only:
        if input_path.is_file():
            if input_path.suffix.lower() != '.png':
                print(f"错误: 不是PNG文件 - {input_path}")
                sys.exit(1)
            
            # Get image name for inspect
            image_name = input_path.stem
            
            # Copy to working directory temporarily
            temp_png = Path(f"./{image_name}.png")
            if not temp_png.exists() or not temp_png.samefile(input_path):
                import shutil
                shutil.copy2(input_path, temp_png)
            
            try:
                options = inspect_image(image_name)
                print(json.dumps(options, indent=2, ensure_ascii=False))
            finally:
                # Clean up
                if temp_png.exists() and not temp_png.samefile(input_path):
                    temp_png.unlink()
        else:
            print("错误: --inspect-only 只能用于单个文件")
            sys.exit(1)
    else:
        # Process file or directory
        if input_path.is_file():
            success = process_single_file(input_path, args.auto, args.option)
            sys.exit(0 if success else 1)
        elif input_path.is_dir():
            success = process_directory(input_path, args.auto, args.option)
            sys.exit(0 if success else 1)
        else:
            print(f"错误: 无法识别的输入类型 - {input_path}")
            sys.exit(1)


if __name__ == '__main__':
    main()