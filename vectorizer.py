"""
Python implementation of the vectorizer - a Potrace-based multi-colored raster to vector tracer.
Converts PNG/JPG images to SVG format.
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from colorthief import ColorThief
import colorsys
from scipy.spatial import distance


class Vectorizer:
    """Main class for converting raster images to SVG vectors."""
    
    def __init__(self):
        """Initialize the vectorizer."""
        pass
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color to RGB tuple.
        
        Args:
            hex_color: Hex color string (e.g., '#FF0000' or 'FF0000')
            
        Returns:
            Tuple of (r, g, b) values
        """
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        
        # Handle 3-character hex codes
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """
        Convert RGB tuple to hex color string.
        
        Args:
            rgb: Tuple of (r, g, b) values
            
        Returns:
            Hex color string with '#' prefix
        """
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    @staticmethod
    def rgba_to_hex(rgba: Tuple[int, int, int, float]) -> str:
        """
        Convert RGBA to hex, blending with white background.
        
        Args:
            rgba: Tuple of (r, g, b, a) values where a is 0-1
            
        Returns:
            Hex color string with '#' prefix
        """
        r, g, b, a = rgba
        # Blend with white background
        r = int(a * r + (1 - a) * 255)
        g = int(a * g + (1 - a) * 255)
        b = int(a * b + (1 - a) * 255)
        return Vectorizer.rgb_to_hex((r, g, b))
    
    @staticmethod
    def combine_opacity(a: float, b: float) -> float:
        """
        Combine two opacity values.
        
        Args:
            a: First opacity value (0-1)
            b: Second opacity value (0-1)
            
        Returns:
            Combined opacity value
        """
        return 1 - (1 - a) * (1 - b)
    
    def get_solid(self, svg_content: str, stroke: bool = False) -> str:
        """
        Convert opacity-based SVG to solid colors.
        
        Args:
            svg_content: SVG content as string
            stroke: Whether to add stroke attributes
            
        Returns:
            Modified SVG content with solid colors
        """
        # Remove fill="black" attributes
        svg_content = svg_content.replace('fill="black"', '')
        
        # Find all fill-opacity attributes
        opacity_pattern = re.compile(r'fill-opacity="([\d\.]+)"')
        matches = opacity_pattern.findall(svg_content)
        
        if not matches:
            return svg_content
        
        # Get unique opacity values and sort them
        unique_opacities = sorted(set(float(m) for m in matches), reverse=True)
        
        # Calculate true opacity for each value
        color_replacements = []
        for i, opacity in enumerate(unique_opacities):
            # Combine all lighter opacities
            lighter_opacities = unique_opacities[i:]
            true_opacity = lighter_opacities[0]
            for op in lighter_opacities[1:]:
                true_opacity = self.combine_opacity(true_opacity, op)
            
            # Convert to hex color
            hex_color = self.rgba_to_hex((0, 0, 0, true_opacity))
            
            color_replacements.append({
                'opacity_str': f'fill-opacity="{opacity}"',
                'hex': hex_color,
                'opacity': opacity
            })
        
        # Replace opacity attributes with solid colors
        for replacement in color_replacements:
            if stroke:
                new_attr = f'fill="{replacement["hex"]}" stroke-width="1" stroke="{replacement["hex"]}"'
                svg_content = svg_content.replace(replacement['opacity_str'], new_attr)
            else:
                svg_content = svg_content.replace(replacement['opacity_str'], f'fill="{replacement["hex"]}"')
        
        # Remove stroke="none" attributes
        svg_content = svg_content.replace(' stroke="none"', '')
        
        return svg_content
    
    def get_pixels(self, image_path: str) -> Dict[str, Any]:
        """
        Get pixel data from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing pixels array and metadata
        """
        img = Image.open(image_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB' and img.mode != 'RGBA':
            img = img.convert('RGB')
        
        pixels = np.array(img)
        
        return {
            'pixels': pixels,
            'width': img.width,
            'height': img.height,
            'channels': len(img.mode),
            'mode': img.mode
        }
    
    def find_nearest_color(self, color: str, color_list: List[str]) -> str:
        """
        Find the nearest color from a list of colors.
        
        Args:
            color: Target color in hex format
            color_list: List of colors to compare against
            
        Returns:
            Nearest color from the list
        """
        target_rgb = np.array(self.hex_to_rgb(color))
        min_distance = float('inf')
        nearest = color_list[0]
        
        for c in color_list:
            c_rgb = np.array(self.hex_to_rgb(c))
            dist = distance.euclidean(target_rgb, c_rgb)
            if dist < min_distance:
                min_distance = dist
                nearest = c
        
        return nearest
    
    def replace_colors(self, svg_content: str, original_image_path: str) -> str:
        """
        Replace colors in SVG based on the original image colors.
        
        Args:
            svg_content: SVG content as string
            original_image_path: Path to the original image
            
        Returns:
            Modified SVG content with replaced colors
        """
        # Check if image is grayscale
        img = Image.open(original_image_path)
        if img.mode == 'L' or img.mode == 'LA':
            return svg_content
        
        # Find all hex colors in SVG
        hex_pattern = re.compile(r'#([a-f0-9]{3}){1,2}\b', re.IGNORECASE)
        svg_colors = list(set(hex_pattern.findall(svg_content)))
        svg_colors = ['#' + c for c in svg_colors]
        
        if not svg_colors:
            return svg_content
        
        # Get pixels from original image
        original_data = self.get_pixels(original_image_path)
        original_pixels = original_data['pixels'].reshape(-1, original_data['channels'])
        
        # Create temporary SVG file and render it
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as tmp_svg:
            tmp_svg.write(svg_content)
            tmp_svg_path = tmp_svg.name
        
        # For simplicity, we'll use a different approach:
        # Sample colors from the original image and map SVG colors to them
        
        # Get dominant colors from original image using KMeans
        n_colors = min(len(svg_colors), 5)
        if len(original_pixels) > 1000:
            # Sample pixels for faster processing
            sample_indices = np.random.choice(len(original_pixels), 1000, replace=False)
            sample_pixels = original_pixels[sample_indices]
        else:
            sample_pixels = original_pixels
        
        # Remove transparent pixels if RGBA
        if original_data['channels'] == 4:
            # Filter out transparent pixels
            opaque_mask = sample_pixels[:, 3] > 128
            sample_pixels = sample_pixels[opaque_mask][:, :3]
        elif original_data['channels'] == 3:
            sample_pixels = sample_pixels
        
        if len(sample_pixels) > 0:
            kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
            kmeans.fit(sample_pixels)
            
            # Get cluster centers as RGB values
            dominant_colors = kmeans.cluster_centers_.astype(int)
            dominant_hex = [self.rgb_to_hex(tuple(c)) for c in dominant_colors]
            
            # Map SVG colors to dominant colors
            color_mapping = {}
            for svg_color in svg_colors:
                nearest = self.find_nearest_color(svg_color, dominant_hex)
                color_mapping[svg_color] = nearest
            
            # Replace colors in SVG
            for old_color, new_color in color_mapping.items():
                svg_content = svg_content.replace(old_color, new_color)
        
        # Clean up
        os.unlink(tmp_svg_path)
        
        return svg_content
    
    def viewboxify(self, svg_content: str) -> str:
        """
        Convert SVG width/height to viewBox for better scaling.
        
        Args:
            svg_content: SVG content as string
            
        Returns:
            Modified SVG content with viewBox
        """
        # Extract width and height
        width_match = re.search(r'width="(\d+)"', svg_content)
        height_match = re.search(r'height="(\d+)"', svg_content)
        
        if width_match and height_match:
            width = width_match.group(1)
            height = height_match.group(1)
            
            old_header = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
            new_header = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
            
            svg_content = svg_content.replace(old_header, new_header)
        
        return svg_content
    
    def optimize_svg(self, svg_content: str) -> str:
        """
        Optimize SVG content (simplified version).
        
        Args:
            svg_content: SVG content as string
            
        Returns:
            Optimized SVG content
        """
        # Basic optimization: remove unnecessary whitespace
        svg_content = re.sub(r'\s+', ' ', svg_content)
        svg_content = re.sub(r'> <', '><', svg_content)
        
        return svg_content
    
    def parse_image(self, image_name: str, step: int = 3, colors: List[str] = None) -> str:
        """
        Parse an image and convert it to SVG.
        
        Args:
            image_name: Name of the image file (without extension)
            step: Number of color levels for posterization
            colors: List of colors to use
            
        Returns:
            SVG content as string
        """
        image_path = f"./{image_name}.png"
        
        # Check if potrace is installed
        try:
            subprocess.run(['potrace', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("Potrace is not installed. Please install it first.")
        
        # Create temporary BMP file (potrace works better with BMP)
        img = Image.open(image_path)
        
        # If posterizing, convert to grayscale and apply posterization
        if step > 1:
            img = img.convert('L')
            # Posterize the image
            img = Image.eval(img, lambda x: int(x / 256 * step) * int(256 / step))
        
        with tempfile.NamedTemporaryFile(suffix='.bmp', delete=False) as tmp_bmp:
            img.save(tmp_bmp.name)
            tmp_bmp_path = tmp_bmp.name
        
        # Run potrace
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp_svg:
            tmp_svg_path = tmp_svg.name
        
        potrace_cmd = [
            'potrace',
            tmp_bmp_path,
            '-s',  # SVG output
            '-o', tmp_svg_path,
            '--opttolerance', '0.5'
        ]
        
        subprocess.run(potrace_cmd, check=True)
        
        # Read the SVG content
        with open(tmp_svg_path, 'r') as f:
            svg_content = f.read()
        
        # Clean up temporary files
        os.unlink(tmp_bmp_path)
        os.unlink(tmp_svg_path)
        
        # Process the SVG
        svg_content = self.get_solid(svg_content, step != 1)
        
        if step == 1 and colors:
            # For single color, replace black with the specified color
            svg_content = svg_content.replace('#000000', colors[0])
        elif step > 1:
            # Replace colors based on original image
            svg_content = self.replace_colors(svg_content, image_path)
        
        # Optimize and viewboxify
        svg_content = self.optimize_svg(svg_content)
        svg_content = self.viewboxify(svg_content)
        
        # Save the result
        output_path = f"./{image_name}.svg"
        with open(output_path, 'w') as f:
            f.write(svg_content)
        
        print(f"SVG saved to {output_path}")
        return svg_content
    
    def inspect_image(self, image_name: str) -> List[Dict[str, Any]]:
        """
        Inspect an image and return possible vectorization options.
        
        Args:
            image_name: Name of the image file (without extension)
            
        Returns:
            List of options with step and colors parameters
        """
        image_path = f"./{image_name}.png"
        
        # Get dominant colors using ColorThief
        color_thief = ColorThief(image_path)
        palette = color_thief.get_palette(color_count=5, quality=1)
        
        # Convert palette to different formats
        hex_list = [self.rgb_to_hex(color) for color in palette]
        hsl_list = [colorsys.rgb_to_hls(r/255, g/255, b/255) for r, g, b in palette]
        
        # Check if image has white background
        is_white_background = hsl_list[0][1] > 0.80  # L (lightness) > 0.80
        if is_white_background:
            hex_list = hex_list[1:]
            hsl_list = hsl_list[1:]
        
        # Check if image is black and white
        is_black_and_white = len(hsl_list) > 0 and hsl_list[-1][1] < 0.05  # L < 0.05
        
        # Check for NaN values (grayscale)
        if len(hsl_list) > 0:
            h, l, s = hsl_list[-1]
            if s == 0:  # Saturation is 0 for grayscale
                is_black_and_white = True
        
        options = []
        
        if is_black_and_white:
            options.append({'step': 1, 'colors': ['#000000']})
        else:
            # Calculate hue and luminance differences
            hue_array = [h for h, l, s in hsl_list]
            lum_array = [l for h, l, s in hsl_list]
            
            hue_difference = 0
            lum_difference = 0
            for i in range(1, len(hue_array)):
                hue_difference += abs(hue_array[i-1] - hue_array[i]) * 360  # Convert to degrees
                lum_difference += abs(lum_array[i-1] - lum_array[i])
            
            # Check if image is monochrome
            is_monocolor = hue_difference < 5 and lum_difference < 0.2
            
            if is_monocolor and hex_list:
                options.append({'step': 1, 'colors': [hex_list[-1]]})
            else:
                # Offer multiple options with different color counts
                for i in range(1, min(5, len(hex_list) + 1)):
                    options.append({'step': i, 'colors': hex_list[:i]})
        
        return options


# Export functions for compatibility with the original API
def inspect_image(image_name: str) -> List[Dict[str, Any]]:
    """
    Inspect an image and return possible vectorization options.
    
    Args:
        image_name: Name of the image file (without extension)
        
    Returns:
        List of options with step and colors parameters
    """
    vectorizer = Vectorizer()
    return vectorizer.inspect_image(image_name)


def parse_image(image_name: str, step: int = 3, colors: List[str] = None) -> str:
    """
    Parse an image and convert it to SVG.
    
    Args:
        image_name: Name of the image file (without extension)
        step: Number of color levels for posterization
        colors: List of colors to use
        
    Returns:
        SVG content as string
    """
    vectorizer = Vectorizer()
    return vectorizer.parse_image(image_name, step, colors)
