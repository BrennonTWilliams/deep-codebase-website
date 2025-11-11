#!/usr/bin/env python3
"""Replace pure white pixels with transparency in PNG images."""

from PIL import Image
import sys

def make_white_transparent(input_path, output_path=None):
    """
    Replace all pure white (255, 255, 255) pixels with transparent pixels.

    Args:
        input_path: Path to input PNG file
        output_path: Path to output PNG file (defaults to overwriting input)
    """
    # Open image and convert to RGBA if needed
    img = Image.open(input_path)
    img = img.convert("RGBA")

    # Get pixel data
    data = img.getdata()

    # Create new data with white pixels replaced by transparent
    new_data = []
    for item in data:
        # Check if pixel is pure white (255, 255, 255)
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            # Replace with transparent (0, 0, 0, 0)
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    # Update image data
    img.putdata(new_data)

    # Save the image
    output = output_path if output_path else input_path
    img.save(output, "PNG")
    print(f"Saved transparent image to: {output}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python make_transparent.py <input_image> [output_image]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    make_white_transparent(input_file, output_file)
