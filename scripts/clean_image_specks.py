#!/usr/bin/env python3
"""
Remove white specks from PNG images while preserving transparency.
Production-ready implementation with proper alpha channel handling.
"""

from PIL import Image
from pathlib import Path
import numpy as np
from scipy import ndimage
from typing import Union


def clean_white_specks_with_transparency(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    min_speck_size: int = 50,
    white_threshold: int = 250,
) -> Image.Image:
    """
    Remove white specks from image while preserving transparent background.

    Algorithm:
    1. Load image in RGBA mode
    2. Separate alpha channel from RGB data
    3. Detect white pixels only in non-transparent areas
    4. Use connected component analysis to find small white regions
    5. Remove specks smaller than threshold
    6. Reconstruct image with original alpha channel

    Args:
        input_path: Path to input PNG image
        output_path: Path to save cleaned image
        min_speck_size: Minimum pixel area to preserve (smaller = removed)
        white_threshold: RGB values above this are considered "white" (0-255)

    Returns:
        Cleaned PIL Image object

    Raises:
        FileNotFoundError: If input image doesn't exist
        ValueError: If parameters are out of valid range
    """
    # Validation
    if not Path(input_path).exists():
        raise FileNotFoundError(f"Input image not found: {input_path}")
    if not 1 <= min_speck_size <= 10000:
        raise ValueError(f"min_speck_size must be 1-10000, got {min_speck_size}")
    if not 0 <= white_threshold <= 255:
        raise ValueError(f"white_threshold must be 0-255, got {white_threshold}")

    # Load image in RGBA mode
    img = Image.open(input_path).convert("RGBA")
    img_array = np.array(img)

    # Separate channels: RGB (0:3) and Alpha (3)
    rgb_array = img_array[:, :, 0:3]  # Shape: (H, W, 3)
    alpha_array = img_array[:, :, 3]   # Shape: (H, W)

    # Create mask for opaque/semi-opaque pixels (where we look for specks)
    # Only process areas that are NOT transparent
    opaque_mask = alpha_array > 0

    # Detect white pixels in RGB channels
    # A pixel is "white" if ALL RGB channels are above threshold
    is_white = (
        (rgb_array[:, :, 0] > white_threshold) &
        (rgb_array[:, :, 1] > white_threshold) &
        (rgb_array[:, :, 2] > white_threshold)
    )

    # Only consider white pixels in non-transparent areas
    white_in_opaque = is_white & opaque_mask

    # Convert to binary for connected component analysis
    binary_white = white_in_opaque.astype(np.uint8) * 255

    # Label connected white components
    labeled, num_features = ndimage.label(binary_white)

    # Calculate size of each component
    component_sizes = np.bincount(labeled.ravel())

    # Identify small components (specks to remove)
    # component 0 is background, so we don't remove it
    small_components = component_sizes < min_speck_size
    small_components[0] = False  # Preserve background

    # Create mask for pixels to remove
    remove_mask = small_components[labeled]

    # Remove specks by setting them to black (0, 0, 0)
    # This preserves the design while removing white noise
    rgb_cleaned = rgb_array.copy()
    rgb_cleaned[remove_mask] = [0, 0, 0]

    # Reconstruct RGBA image with original alpha channel
    rgba_cleaned = np.zeros_like(img_array)
    rgba_cleaned[:, :, 0:3] = rgb_cleaned  # RGB channels
    rgba_cleaned[:, :, 3] = alpha_array    # Original alpha (unchanged)

    # Convert back to PIL Image
    cleaned_img = Image.fromarray(rgba_cleaned.astype(np.uint8), mode="RGBA")

    # Save with PNG compression
    cleaned_img.save(output_path, "PNG", optimize=True)

    # Report statistics
    num_specks_removed = np.sum(small_components) - 1  # -1 for background
    total_pixels_cleaned = np.sum(remove_mask)

    print(f"✓ Image cleaned successfully")
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}")
    print(f"  Specks removed: {num_specks_removed}")
    print(f"  Pixels cleaned: {total_pixels_cleaned}")
    print(f"  Threshold: white > {white_threshold}, size < {min_speck_size}px")

    return cleaned_img


def batch_clean_images(
    image_paths: list,
    output_dir: Union[Path, None] = None,
    **clean_kwargs
) -> list:
    """
    Clean multiple images in batch.

    Args:
        image_paths: List of image paths to clean
        output_dir: Output directory (defaults to same as input with '-cleaned' suffix)
        **clean_kwargs: Additional arguments for clean_white_specks_with_transparency

    Returns:
        List of output file paths
    """
    output_paths = []

    for input_path in image_paths:
        input_path = Path(input_path)

        if output_dir:
            output_path = output_dir / f"{input_path.stem}-cleaned{input_path.suffix}"
        else:
            output_path = input_path.parent / f"{input_path.stem}-cleaned{input_path.suffix}"

        try:
            clean_white_specks_with_transparency(input_path, output_path, **clean_kwargs)
            output_paths.append(output_path)
        except Exception as e:
            print(f"✗ Failed to clean {input_path}: {e}")

    return output_paths


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Remove white specks from PNG images while preserving transparency"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input PNG image path"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output path (default: <input>-cleaned.png)"
    )
    parser.add_argument(
        "-s", "--size",
        type=int,
        default=50,
        help="Minimum speck size to preserve in pixels (default: 50)"
    )
    parser.add_argument(
        "-t", "--threshold",
        type=int,
        default=250,
        help="White detection threshold 0-255 (default: 250)"
    )

    args = parser.parse_args()

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = args.input.parent / f"{args.input.stem}-cleaned{args.input.suffix}"

    # Clean the image
    cleaned = clean_white_specks_with_transparency(
        args.input,
        output_path,
        min_speck_size=args.size,
        white_threshold=args.threshold,
    )
