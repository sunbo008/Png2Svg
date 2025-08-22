#!/usr/bin/env python3
"""
Example usage of the vectorizer module.
Similar to the original index_local.js
"""

from vectorizer import inspect_image, parse_image


def main():
    """
    Example usage demonstrating how to use the vectorizer.
    """
    # Example 1: Process a test image
    image_name = "test"
    
    print(f"Processing {image_name}.png...")
    
    # Inspect the image to get vectorization options
    options = inspect_image(image_name)
    print(f"Available options: {options}")
    
    # Use the first option
    if options:
        option_index = 0
        selected_option = options[option_index]
        print(f"Using option {option_index}: {selected_option}")
        
        # Parse the image with the selected option
        parse_image(
            image_name, 
            selected_option['step'], 
            selected_option['colors']
        )
        print(f"Successfully converted {image_name}.png to {image_name}.svg")
    else:
        print(f"No vectorization options available for {image_name}.png")
    
    # You can uncomment these to process other images:
    # process_image("image-asset")
    # process_image("coffee")


def process_image(image_name: str):
    """
    Helper function to process an image with default settings.
    
    Args:
        image_name: Name of the image file (without extension)
    """
    print(f"\nProcessing {image_name}.png...")
    
    options = inspect_image(image_name)
    if options:
        # Use the first option by default
        option = options[0]
        parse_image(image_name, option['step'], option['colors'])
        print(f"Successfully converted {image_name}.png to {image_name}.svg")
    else:
        print(f"No options available for {image_name}.png")


if __name__ == '__main__':
    # Run the main function
    main()
