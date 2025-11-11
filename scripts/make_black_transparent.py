#!/usr/bin/env python3
"""Replace black background pixels with transparency in PNG images."""

from PIL import Image
import sys

def make_black_transparent(input_path, output_path=None, threshold=0):
    """
    Replace pure black or near-black pixels with transparent pixels.

    Args:
        input_path: Path to input PNG file
        output_path: Path to output PNG file (defaults to overwriting input)
        threshold: Brightness threshold below or equal to which pixels become transparent (0-255)
                  Default 0 = only pure black (0,0,0)
                  Recommended values: 0 (pure black only), 1-5 (very conservative), 10-30 (aggressive)
    """
    # Open image and convert to RGBA if needed
    img = Image.open(input_path)
    img = img.convert("RGBA")

    # Get pixel data
    data = img.getdata()

    # Create new data with black pixels replaced by transparent
    new_data = []
    pixels_changed = 0

    for item in data:
        r, g, b = item[0], item[1], item[2]

        # Check if pixel is at or below threshold (pure black if threshold=0)
        if r <= threshold and g <= threshold and b <= threshold:
            # Replace with transparent
            new_data.append((0, 0, 0, 0))
            pixels_changed += 1
        else:
            new_data.append(item)

    # Update image data
    img.putdata(new_data)

    # Save the image
    output = output_path if output_path else input_path
    img.save(output, "PNG")

    total_pixels = len(data)
    percent_changed = (pixels_changed / total_pixels) * 100

    print(f"Processed: {input_path}")
    print(f"Changed {pixels_changed:,} pixels ({percent_changed:.2f}%) to transparent")
    print(f"Saved to: {output}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python make_black_transparent.py <input_image> [output_image] [threshold]")
        print("  threshold: brightness threshold (0-255), default=0 (pure black only)")
        print("  Recommended: 0=pure black, 1-5=conservative, 10-30=aggressive")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    make_black_transparent(input_file, output_file, threshold)
