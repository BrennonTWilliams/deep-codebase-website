# Auto-Detection Feature for spritesheet_to_gif.py

## Overview
The script now supports automatic grid detection, eliminating the need to manually specify `--cols` and `--rows` arguments. This feature uses sprite segmentation techniques adapted from SpriteExtractor.html.

## Implementation Details

### Core Components

1. **Sprite Segmentation** (`segment_sprites_from_spritesheet`)
   - Uses flood fill algorithm to detect individual sprites
   - Supports both transparent (alpha-based) and opaque (color-based) images
   - Auto-detects background color from top-left pixel for opaque images

2. **Grid Detection** (`detect_grid_dimensions`)
   - Analyzes sprite positions to identify regular grid patterns
   - Clusters positions with tolerance for slight misalignment (10px default)
   - Validates that detected pattern forms a complete rectangular grid
   - Sorts sprites in reading order (top-to-bottom, left-to-right)

3. **Position Clustering**
   - Groups sprite positions that are within tolerance threshold
   - Uses mean values to find grid alignment points
   - Handles sprites that aren't perfectly aligned

### Algorithm Flow

```
1. Load spritesheet image
2. Create segmentation map (alpha or color-based)
3. Apply flood fill to find connected regions (sprites)
4. Extract bounding boxes for each sprite
5. Cluster X and Y positions to detect grid structure
6. Calculate cols = unique X positions, rows = unique Y positions
7. Validate: sprite_count == cols × rows
8. Sort sprites by grid position
9. Return detected grid dimensions
```

## Usage

### Auto-Detection Mode
```bash
# Simple auto-detection
python spritesheet_to_gif.py --input sprite.png --auto-detect

# With centering and animation options
python spritesheet_to_gif.py --input sprite.png --auto-detect --center auto --unified --loop 0
```

### Manual Mode (Original)
```bash
# Explicit grid dimensions (faster, more reliable for known layouts)
python spritesheet_to_gif.py --input sprite.png --cols 3 --rows 4
```

### Validation Rules
- Either provide `--cols` AND `--rows`, OR use `--auto-detect`
- Cannot use auto-detect with partial manual specification
- Auto-detect will fail if grid is irregular or incomplete

## Technical Specifications

### Parameters
- **alpha_threshold**: 10% default for segmentation (0-100)
- **color_tolerance**: 30 default for color-based detection (0-255)
- **min_sprite_size**: 10px minimum to filter noise
- **position_tolerance**: 10px for clustering alignment

### Supported Image Types
- **Transparent PNGs**: Uses alpha channel segmentation
- **Opaque images**: Uses color distance from background
- **Mixed formats**: Auto-detects best segmentation method

### Limitations
- Requires regular grid layout (equal spacing)
- Sprites must be separated by background
- Partial grids or irregular layouts will fail
- Position clustering tolerance may need adjustment for very small sprites

## Advantages Over Manual Specification

1. **No counting required**: No need to manually count rows/columns
2. **Reduces errors**: Eliminates manual counting mistakes
3. **Flexible**: Works with varying sprite sizes within grid
4. **Robust**: Handles slight misalignment (within tolerance)

## Fallback Strategy

If auto-detection fails:
1. Error message indicates detection failure
2. Suggests using manual `--cols` and `--rows` specification
3. Recommends adjusting detection parameters if needed

## Code Adaptations from SpriteExtractor

### Adapted Components
- Alpha-based segmentation map creation
- Color-based segmentation for opaque images
- Flood fill algorithm for connected component detection
- Bounding box extraction

### New Components (Not in SpriteExtractor)
- Grid dimension detection logic
- Position clustering algorithm
- Grid validation (ensure complete rectangular grid)
- Sprite sorting by grid position

## Testing Recommendations

Test with:
- Transparent sprite sheets with regular grids
- Opaque sprite sheets with consistent backgrounds
- Sprite sheets with slight position variations
- Various grid sizes (2x2, 3x4, 4x4, etc.)
- Edge cases: single row/column, large grids (10x10+)

## Performance Considerations

- Auto-detection is slower than manual specification (~2-3x)
- Segmentation requires full image analysis
- Recommended for convenience, not performance-critical workflows
- Use manual mode when grid dimensions are known
