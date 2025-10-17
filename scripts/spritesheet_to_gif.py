#!/usr/bin/env python3
"""
Convert spritesheet to animated GIF.

This script extracts individual frames from a spritesheet and creates
an animated GIF with the specified frame rate and loop settings.
"""

from PIL import Image
import os
import argparse
import numpy as np


def segment_sprites_from_spritesheet(spritesheet, alpha_threshold=26, bg_color=None, color_tolerance=80, min_sprite_area=5000):
    """
    Automatically detect individual sprites in a spritesheet using flood fill segmentation.

    Args:
        spritesheet: PIL Image of the spritesheet
        alpha_threshold: Minimum alpha value to consider as content (0-255)
        bg_color: Background color as (r, g, b) tuple or None to auto-detect
        color_tolerance: Color distance threshold (0-255)
        min_sprite_area: Minimum sprite area in pixels to keep (filters out noise/bubbles)

    Returns:
        List of sprite bounding boxes as (x, y, width, height) tuples
    """
    # Convert to RGBA if needed
    if spritesheet.mode != 'RGBA':
        if spritesheet.mode == 'RGB':
            # For RGB images, add full alpha channel
            spritesheet = spritesheet.convert('RGBA')
        else:
            spritesheet = spritesheet.convert('RGBA')

    width, height = spritesheet.size
    img_array = np.array(spritesheet)

    # Check if image has transparency
    alpha_channel = img_array[:, :, 3]
    has_transparency = np.any(alpha_channel < 255)

    # Create segmentation map (1 = sprite, 0 = background)
    if has_transparency:
        # Alpha-based segmentation
        segmentation_map = (alpha_channel > alpha_threshold).astype(np.uint8)
        print(f"Using alpha-based detection (threshold={alpha_threshold})")
    else:
        # Color-based segmentation
        if bg_color is None:
            # Auto-detect background from top-left pixel
            bg_color = tuple(img_array[0, 0, :3])

        print(f"Background color detected: RGB{bg_color}")
        print(f"Color tolerance: {color_tolerance}")

        # Calculate color distance (convert to float to avoid uint8 overflow)
        rgb_array = img_array[:, :, :3].astype(np.float32)
        bg_array = np.array(bg_color, dtype=np.float32)
        distance = np.sqrt(np.sum((rgb_array - bg_array)**2, axis=2))
        segmentation_map = (distance > color_tolerance).astype(np.uint8)

        # Diagnostic output
        foreground_pixels = np.sum(segmentation_map)
        total_pixels = width * height
        foreground_percentage = (foreground_pixels / total_pixels) * 100
        print(f"Foreground pixels: {foreground_pixels}/{total_pixels} ({foreground_percentage:.1f}%)")

    # Find connected components using flood fill
    visited = np.zeros((height, width), dtype=np.uint8)
    sprites = []

    def flood_fill(start_x, start_y):
        """Flood fill to find connected sprite region."""
        stack = [(start_x, start_y)]
        min_x = max_x = start_x
        min_y = max_y = start_y

        while stack:
            x, y = stack.pop()

            if (x < 0 or x >= width or y < 0 or y >= height or
                visited[y, x] or not segmentation_map[y, x]):
                continue

            visited[y, x] = 1
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

            # Check 4-way neighbors
            stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])

        return (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    # Find all sprites
    for y in range(height):
        for x in range(width):
            if segmentation_map[y, x] and not visited[y, x]:
                bbox = flood_fill(x, y)
                sprites.append(bbox)

    # DIAGNOSTIC: Show pre-filtering stats
    total_detected = len(sprites)
    print(f"\n🔍 Sprite Detection Diagnostics:")
    print(f"   Total sprites detected (before filtering): {total_detected}")

    if sprites:
        # Calculate areas for all detected sprites
        areas = [w * h for _, _, w, h in sprites]
        print(f"   Size range: min={min(areas)}px, max={max(areas)}px, median={int(np.median(areas))}px")

    # FILTER: Remove sprites smaller than minimum area threshold
    filtered_sprites = [
        (x, y, w, h) for x, y, w, h in sprites
        if (w * h) >= min_sprite_area
    ]

    # DIAGNOSTIC: Show post-filtering stats
    filtered_count = len(filtered_sprites)
    removed_count = total_detected - filtered_count
    print(f"   Sprites after size filtering (>={min_sprite_area}px): {filtered_count}")
    print(f"   Small sprites removed (noise/bubbles): {removed_count}")

    if filtered_sprites:
        filtered_areas = [w * h for _, _, w, h in filtered_sprites]
        print(f"   Kept sprite size range: min={min(filtered_areas)}px, max={max(filtered_areas)}px, median={int(np.median(filtered_areas))}px")

    return filtered_sprites


def detect_grid_dimensions(sprites, min_sprite_size=10):
    """
    Detect grid dimensions from sprite positions.

    Args:
        sprites: List of sprite bounding boxes as (x, y, width, height) tuples
        min_sprite_size: Minimum sprite size to consider (filters noise)

    Returns:
        Tuple of (cols, rows, sorted_sprites) or None if grid not detected
    """
    if not sprites:
        return None

    # Filter out tiny sprites (noise)
    sprites = [s for s in sprites if s[2] >= min_sprite_size and s[3] >= min_sprite_size]

    if len(sprites) < 2:
        return None

    print(f"\n📐 Grid Detection:")
    print(f"  Total sprites detected: {len(sprites)}")

    # Find all valid factorizations of sprite count
    sprite_count = len(sprites)
    factorizations = []
    for cols in range(1, sprite_count + 1):
        if sprite_count % cols == 0:
            rows = sprite_count // cols
            factorizations.append((cols, rows))

    print(f"  Possible grid configurations for {sprite_count} sprites: {factorizations}")

    # Choose the factorization that best matches sprite layout
    # Prefer grids that are closer to square (minimizes abs difference between cols and rows)
    best_factorization = min(factorizations, key=lambda f: abs(f[0] - f[1]))

    cols, rows = best_factorization
    print(f"  Selected grid: {cols} cols x {rows} rows (aspect ratio: {cols/rows:.2f})")

    # Sort sprites by position (top-to-bottom, left-to-right)
    def get_grid_position(sprite):
        x, y, _, _ = sprite
        # Sort first by y (row), then by x (column)
        return (y, x)

    sorted_sprites = sorted(sprites, key=get_grid_position)

    # Diagnostic output: show positions of selected sprites
    print(f"  ✓ Selected sprite positions (x, y):")
    for idx, sprite in enumerate(sorted_sprites[:min(10, len(sorted_sprites))]):
        x, y, w, h = sprite
        area = w * h
        row = idx // cols
        col = idx % cols
        print(f"    [{idx}] row={row} col={col} pos=({x}, {y}) size={w}x{h} area={area}")
    if len(sorted_sprites) > 10:
        print(f"    ... and {len(sorted_sprites) - 10} more sprites")

    return (cols, rows, sorted_sprites)


def get_content_bbox_alpha(frame, alpha_threshold=26):
    """
    Get bounding box of content in a frame based on alpha channel.

    Args:
        frame: PIL Image with alpha channel
        alpha_threshold: Minimum alpha value to consider as content (0-255)

    Returns:
        Tuple of (left, top, right, bottom) or None if no content found
    """
    if frame.mode != 'RGBA':
        frame = frame.convert('RGBA')

    alpha = frame.split()[-1]
    alpha_array = np.array(alpha)

    # Create binary mask of pixels above threshold
    mask = alpha_array > alpha_threshold

    # Find bounding box
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)

    if not rows.any() or not cols.any():
        return None

    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin, xmax = np.where(cols)[0][[0, -1]]

    return (xmin, ymin, xmax + 1, ymax + 1)


def get_content_bbox_color(frame, bg_color=None, tolerance=30):
    """
    Get bounding box of content based on color distance from background.

    Args:
        frame: PIL Image
        bg_color: Background color as (r, g, b) tuple or None to auto-detect
        tolerance: Color distance threshold (0-255)

    Returns:
        Tuple of (left, top, right, bottom) or None if no content found
    """
    if frame.mode != 'RGB' and frame.mode != 'RGBA':
        frame = frame.convert('RGB')

    # Auto-detect background from top-left pixel if not provided
    if bg_color is None:
        bg_color = frame.getpixel((0, 0))[:3]

    img_array = np.array(frame.convert('RGB'))

    # Calculate Euclidean distance in RGB space (convert to float to avoid uint8 overflow)
    rgb_float = img_array.astype(np.float32)
    bg_float = np.array(bg_color, dtype=np.float32)
    distance = np.sqrt(np.sum((rgb_float - bg_float)**2, axis=2))

    # Create binary mask
    mask = distance > tolerance

    # Find bounding box
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)

    if not rows.any() or not cols.any():
        return None

    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin, xmax = np.where(cols)[0][[0, -1]]

    return (xmin, ymin, xmax + 1, ymax + 1)


def center_frame(frame, bbox, frame_size=None):
    """
    Center content within a frame based on bounding box.

    Args:
        frame: PIL Image to center
        bbox: Bounding box (left, top, right, bottom)
        frame_size: Target frame size or None to use original size

    Returns:
        Centered PIL Image
    """
    if bbox is None:
        return frame

    if frame_size is None:
        frame_size = frame.size

    left, top, right, bottom = bbox
    content_width = right - left
    content_height = bottom - top

    # Calculate centering offset
    offset_x = (frame_size[0] - content_width) // 2
    offset_y = (frame_size[1] - content_height) // 2

    # Create new centered frame with transparency
    if frame.mode == 'RGBA':
        centered = Image.new('RGBA', frame_size, (0, 0, 0, 0))
    else:
        # For non-transparent images, use black background
        centered = Image.new('RGB', frame_size, (0, 0, 0))

    # Extract and paste content
    content = frame.crop(bbox)
    centered.paste(content, (offset_x, offset_y), content if frame.mode == 'RGBA' else None)

    return centered


def auto_detect_and_center(frame, center_mode='auto', alpha_threshold=26,
                           bg_color=None, color_tolerance=30):
    """
    Auto-detect best centering method and apply it.

    Args:
        frame: PIL Image to center
        center_mode: 'auto', 'alpha', 'color', or 'none'
        alpha_threshold: Alpha threshold for alpha mode (0-255)
        bg_color: Background color for color mode
        color_tolerance: Color distance tolerance

    Returns:
        Centered PIL Image
    """
    if center_mode == 'none':
        return frame

    bbox = None

    if center_mode == 'auto':
        # Auto-detect: check for transparency
        if frame.mode == 'RGBA':
            alpha = np.array(frame.split()[-1])
            has_transparency = np.any(alpha < 255)

            if has_transparency:
                bbox = get_content_bbox_alpha(frame, alpha_threshold)
            else:
                bbox = get_content_bbox_color(frame, bg_color, color_tolerance)
        else:
            bbox = get_content_bbox_color(frame, bg_color, color_tolerance)

    elif center_mode == 'alpha':
        bbox = get_content_bbox_alpha(frame, alpha_threshold)

    elif center_mode == 'color':
        bbox = get_content_bbox_color(frame, bg_color, color_tolerance)

    if bbox is None:
        return frame

    return center_frame(frame, bbox, frame.size)


def spritesheet_to_gif(
    spritesheet_path,
    output_path,
    grid_cols=None,
    grid_rows=None,
    fps=8,
    loop=0,
    center_mode='none',
    alpha_threshold=10,
    bg_color=None,
    color_tolerance=80,
    unified_centering=False,
    auto_detect=False
):
    """
    Convert a spritesheet to an animated GIF.

    Args:
        spritesheet_path: Path to the input spritesheet image
        output_path: Path where the GIF will be saved
        grid_cols: Number of columns in the spritesheet grid (None for auto-detect)
        grid_rows: Number of rows in the spritesheet grid (None for auto-detect)
        fps: Frames per second for the animation
        loop: Number of loops (0 = infinite, 1 = once, etc.)
        center_mode: Centering mode ('none', 'auto', 'alpha', 'color')
        alpha_threshold: Alpha threshold percentage (0-100) for alpha mode
        bg_color: Background color as (r, g, b) tuple for color mode
        color_tolerance: Color distance tolerance (0-255) for color mode
        unified_centering: If True, use same offset for all frames (smoother animation)
        auto_detect: If True, automatically detect grid dimensions
    """
    # Load the spritesheet
    spritesheet = Image.open(spritesheet_path)

    # Auto-detect grid dimensions if not provided
    if grid_cols is None or grid_rows is None or auto_detect:
        print("Auto-detecting grid dimensions...")

        # Convert alpha threshold from percentage to 0-255 scale for segmentation
        alpha_threshold_value = int((alpha_threshold / 100) * 255)

        # Segment sprites from spritesheet
        sprites = segment_sprites_from_spritesheet(
            spritesheet,
            alpha_threshold=alpha_threshold_value,
            bg_color=bg_color,
            color_tolerance=color_tolerance
        )

        # Adaptive tolerance: retry with higher tolerance if no sprites found
        if len(sprites) == 0 and color_tolerance == 80:
            print("⚠ No sprites detected with tolerance=80, retrying with tolerance=120...")
            sprites = segment_sprites_from_spritesheet(
                spritesheet,
                alpha_threshold=alpha_threshold_value,
                bg_color=bg_color,
                color_tolerance=120
            )

        # Detect grid dimensions
        grid_result = detect_grid_dimensions(sprites)

        if grid_result is None:
            raise ValueError(
                "Could not auto-detect grid dimensions. "
                "Please provide --cols and --rows manually, or adjust detection parameters."
            )

        grid_cols, grid_rows, _ = grid_result
        print(f"✓ Detected grid: {grid_cols}x{grid_rows}")

    # Calculate individual frame dimensions
    sprite_width = spritesheet.width // grid_cols
    sprite_height = spritesheet.height // grid_rows

    print(f"Spritesheet size: {spritesheet.width}x{spritesheet.height}")
    print(f"Grid layout: {grid_cols}x{grid_rows}")
    print(f"Frame size: {sprite_width}x{sprite_height}")
    print(f"Total frames: {grid_cols * grid_rows}")

    # Convert alpha threshold from percentage to 0-255 scale
    alpha_threshold_value = int((alpha_threshold / 100) * 255)

    # Extract individual frames
    frames = []
    bboxes = []  # Store bounding boxes for unified centering

    for row in range(grid_rows):
        for col in range(grid_cols):
            # Calculate the position of this frame
            left = col * sprite_width
            top = row * sprite_height
            right = left + sprite_width
            bottom = top + sprite_height

            # Extract the frame
            frame = spritesheet.crop((left, top, right, bottom))

            # Apply centering if requested
            if center_mode != 'none':
                if unified_centering:
                    # For unified mode, just collect bboxes first
                    if center_mode == 'auto':
                        if frame.mode == 'RGBA':
                            alpha = np.array(frame.split()[-1])
                            has_transparency = np.any(alpha < 255)
                            if has_transparency:
                                bbox = get_content_bbox_alpha(frame, alpha_threshold_value)
                            else:
                                bbox = get_content_bbox_color(frame, bg_color, color_tolerance)
                        else:
                            bbox = get_content_bbox_color(frame, bg_color, color_tolerance)
                    elif center_mode == 'alpha':
                        bbox = get_content_bbox_alpha(frame, alpha_threshold_value)
                    elif center_mode == 'color':
                        bbox = get_content_bbox_color(frame, bg_color, color_tolerance)

                    bboxes.append(bbox)
                    frames.append(frame)
                else:
                    # Per-frame centering
                    frame = auto_detect_and_center(
                        frame, center_mode, alpha_threshold_value,
                        bg_color, color_tolerance
                    )
                    frames.append(frame)
            else:
                frames.append(frame)

    # Apply unified centering if requested
    if center_mode != 'none' and unified_centering:
        # Calculate unified bounding box across all frames
        valid_bboxes = [bbox for bbox in bboxes if bbox is not None]

        if valid_bboxes:
            # Find the union of all bounding boxes
            min_left = min(bbox[0] for bbox in valid_bboxes)
            min_top = min(bbox[1] for bbox in valid_bboxes)
            max_right = max(bbox[2] for bbox in valid_bboxes)
            max_bottom = max(bbox[3] for bbox in valid_bboxes)

            unified_bbox = (min_left, min_top, max_right, max_bottom)

            # Apply the same centering to all frames
            centered_frames = []
            for frame in frames:
                centered_frames.append(center_frame(frame, unified_bbox, (sprite_width, sprite_height)))
            frames = centered_frames

            print(f"Applied unified centering with bbox: {unified_bbox}")

    # Calculate frame duration in milliseconds
    frame_duration = int(1000 / fps)

    print(f"\nCreating GIF:")
    print(f"  FPS: {fps}")
    print(f"  Frame duration: {frame_duration}ms")
    print(f"  Loop: {'infinite' if loop == 0 else f'{loop} time(s)'}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save as animated GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration,
        loop=loop,
        optimize=False,
        disposal=2  # Clear frame before rendering next (important for transparency)
    )

    print(f"\n✓ GIF saved to: {output_path}")

    # Display file size
    file_size = os.path.getsize(output_path)
    print(f"  File size: {file_size / 1024:.1f} KB")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Convert a spritesheet to an animated GIF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect grid dimensions (no need to specify cols/rows)
  python spritesheet_to_gif.py --input sprite.png --auto-detect

  # Convert a 3x4 grid spritesheet at 8 FPS (manual grid specification)
  python spritesheet_to_gif.py --input sprite.png --cols 3 --rows 4

  # Auto-detect with auto-centering for smooth animation
  python spritesheet_to_gif.py --input sprite.png --auto-detect --center auto --unified

  # Convert with alpha-based centering and custom threshold
  python spritesheet_to_gif.py --input sprite.png --cols 3 --rows 4 --center alpha --alpha-threshold 15

  # Convert opaque image with color-based centering
  python spritesheet_to_gif.py --input sprite.jpg --cols 2 --rows 3 --center color --bg-color #FFFFFF

  # Auto-detect with infinite loop
  python spritesheet_to_gif.py --input sprite.png --auto-detect --loop 0

Centering Modes:
  none  : No centering (default, backward compatible)
  auto  : Auto-detect best method (alpha for transparent, color for opaque)
  alpha : Use alpha channel for transparent sprites (adjustable threshold)
  color : Use background color detection (adjustable tolerance)

Tips:
  - Use --unified for smoother animations (same offset for all frames)
  - Use --center auto for best results with most sprite sheets
  - Adjust --alpha-threshold (0-100) for semi-transparent sprites
  - Adjust --color-tolerance (0-255) for noisy backgrounds
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path to the input spritesheet image'
    )

    parser.add_argument(
        '--output', '-o',
        required=False,
        help='Path where the output GIF will be saved (default: same directory/name as input with .gif extension)'
    )

    parser.add_argument(
        '--cols', '-c',
        type=int,
        required=False,
        help='Number of columns in the spritesheet grid (optional if using --auto-detect)'
    )

    parser.add_argument(
        '--rows', '-r',
        type=int,
        required=False,
        help='Number of rows in the spritesheet grid (optional if using --auto-detect)'
    )

    parser.add_argument(
        '--auto-detect', '-a',
        action='store_true',
        help='Automatically detect grid dimensions using sprite segmentation'
    )

    parser.add_argument(
        '--fps', '-f',
        type=int,
        default=8,
        help='Frames per second for the animation (default: 8)'
    )

    parser.add_argument(
        '--loop', '-l',
        type=int,
        default=1,
        help='Number of loops (0 = infinite, 1 = once, etc.) (default: 1)'
    )

    parser.add_argument(
        '--center',
        type=str,
        choices=['none', 'auto', 'alpha', 'color'],
        default='none',
        help='Centering mode: none (default), auto (detect best method), alpha (transparency-based), color (background color-based)'
    )

    parser.add_argument(
        '--alpha-threshold',
        type=int,
        default=10,
        help='Alpha threshold percentage for alpha centering mode (0-100, default: 10)'
    )

    parser.add_argument(
        '--bg-color',
        type=str,
        default=None,
        help='Background color in hex format (e.g., #FFFFFF) for color centering mode'
    )

    parser.add_argument(
        '--color-tolerance',
        type=int,
        default=80,
        help='Color distance tolerance for color centering mode (0-255, default: 80)'
    )

    parser.add_argument(
        '--unified',
        action='store_true',
        help='Use unified centering (same offset for all frames, smoother animation)'
    )

    args = parser.parse_args()

    # Validate inputs
    if not os.path.exists(args.input):
        print(f"Error: Input file not found at {args.input}")
        return 1

    # Validate grid dimensions if provided
    if not args.auto_detect and (args.cols is None or args.rows is None):
        print("Error: Either provide --cols and --rows, or use --auto-detect")
        return 1

    if args.cols is not None and args.cols <= 0:
        print(f"Error: Columns must be positive (cols={args.cols})")
        return 1

    if args.rows is not None and args.rows <= 0:
        print(f"Error: Rows must be positive (rows={args.rows})")
        return 1

    if args.fps <= 0:
        print(f"Error: FPS must be positive (fps={args.fps})")
        return 1

    if args.loop < 0:
        print(f"Error: Loop count must be non-negative (loop={args.loop})")
        return 1

    if args.alpha_threshold < 0 or args.alpha_threshold > 100:
        print(f"Error: Alpha threshold must be 0-100 (alpha_threshold={args.alpha_threshold})")
        return 1

    if args.color_tolerance < 0 or args.color_tolerance > 255:
        print(f"Error: Color tolerance must be 0-255 (color_tolerance={args.color_tolerance})")
        return 1

    # Parse background color if provided
    bg_color = None
    if args.bg_color:
        try:
            # Remove '#' if present
            hex_color = args.bg_color.lstrip('#')
            if len(hex_color) != 6:
                raise ValueError("Invalid hex color format")
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            bg_color = (r, g, b)
        except ValueError:
            print(f"Error: Invalid background color format. Use hex format like #FFFFFF")
            return 1

    # Determine output path if not provided
    if args.output is None:
        input_dir = os.path.dirname(args.input)
        input_basename = os.path.basename(args.input)
        input_name_without_ext = os.path.splitext(input_basename)[0]
        output_path = os.path.join(input_dir, f"{input_name_without_ext}.gif")
    else:
        output_path = args.output

    print("=" * 60)
    print("Spritesheet to GIF Converter")
    print("=" * 60)

    # Convert spritesheet to GIF
    spritesheet_to_gif(
        spritesheet_path=args.input,
        output_path=output_path,
        grid_cols=args.cols,
        grid_rows=args.rows,
        fps=args.fps,
        loop=args.loop,
        center_mode=args.center,
        alpha_threshold=args.alpha_threshold,
        bg_color=bg_color,
        color_tolerance=args.color_tolerance,
        unified_centering=args.unified,
        auto_detect=args.auto_detect
    )

    return 0


if __name__ == "__main__":
    exit(main())
