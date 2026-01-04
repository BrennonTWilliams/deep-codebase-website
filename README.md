# Deep-Codebase Website

A landing page for Deep-Codebase - a tool for extracting functionality from any codebase. Features an auto-playing animated diver character, rotating hero text, and terminal demonstration carousel.

## Features

- **Auto-Playing Animation**: Diver character animates continuously using sprite sheet
- **Lazy-Loaded Assets**: Spritesheet loads after page load for optimal performance
- **WebP/PNG Fallback**: Modern image formats with automatic fallback support
- **Responsive Design**: Mobile-optimized layout with adaptive background elements
- **Terminal Carousel**: Auto-rotating demonstration examples
- **Performance Optimized**: Paused animations when page is hidden

## Project Structure

```
deep-codebase-website/
├── index.html                          # Main landing page
├── images/
│   └── diver/
│       ├── glyph-wall-left.webp       # Left background wall (403px wide)
│       ├── glyph-wall-left.png        # PNG fallback
│       └── spritesheets/
│           ├── diver-spritesheet.webp # Animated diver (7320×6784px, 24 frames)
│           ├── diver-spritesheet.png  # PNG fallback
│           └── diver-spritesheet.json # Frame coordinate data
└── README.md
```

## Setup

### Prerequisites

A local HTTP server is required to properly serve the site and avoid CORS issues with image loading.

### Installation & Running

**Option 1: Python (Built-in)**
```bash
# Python 3
python3 -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```

**Option 2: Node.js (http-server)**
```bash
# Install globally
npm install -g http-server

# Run server
http-server -p 8000
```

**Option 3: VS Code Live Server**
1. Install "Live Server" extension
2. Right-click `index.html`
3. Select "Open with Live Server"

### Access

Open your browser to: `http://localhost:8000`

## Diver Animation System

### How It Works

1. **Lazy Loading**: Spritesheet loads after page fully loads to prioritize initial render
2. **Frame Cycling**: Animation cycles through 24 frames continuously at a set interval
3. **Sprite Positioning**: Background position updates via `requestAnimationFrame` for smooth performance

### Spritesheet Specifications

- **Total Size**: 7320×6784px (scaled to 604.5×560px in CSS)
- **Frame Count**: 24 frames (6 columns × 4 rows)
- **Frame Size**: 1220×1696px (scaled to 100.75×140px display size)
- **Format**: WebP primary, PNG fallback
- **JSON Data**: Frame coordinates in `diver-spritesheet.json`

### Customizing Animation

Edit the sprite configuration in `index.html`:

```javascript
// Line 82-94: Sprite container sizing
#diver-sprite {
    left: 200px;              // Horizontal position
    top: 50%;                 // Vertical position
    width: 100.75px;          // Display width
    height: 140px;            // Display height
    background-size: 604.5px 560px;  // Spritesheet scale
}
```

## Performance Features

- **Visibility API**: Pauses animations when tab is hidden
- **RequestAnimationFrame**: Smooth sprite updates synced to display refresh
- **Lazy Asset Loading**: Defers non-critical image loading
- **Optimized Gradients**: Reduced layer count from 5→2 for better rendering

## Responsive Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| >1024px | Full diver animation + wall background |
| ≤1024px | Diver and wall hidden (tablet/mobile) |
| ≤768px | Single column layout, vertical diagram flow |

## Browser Support

- **Modern Browsers**: Full WebP support with sprite animation
- **Legacy Browsers**: Automatic PNG fallback via `image-set()` and `@supports`
- **Mobile**: Optimized layout without background animations

## Development

### Modifying Content

- **Hero Words**: Edit `words` array (line 752)
- **Terminal Examples**: Update `.terminal` divs (lines 567-619)
- **Feature Cards**: Modify `.feature-card` sections (lines 667-693)
- **Color Palette**: Adjust CSS variables in `:root` (lines 14-44)

### Adding New Terminals

```html
<div class="terminal" data-terminal="3">
    <div class="terminal-header">┌─ deep-codebase extraction ─┐</div>
    <div class="terminal-line">
        <span class="terminal-prompt">$</span> your-command-here
    </div>
    <!-- Add output lines -->
</div>
```

Update terminal count in JavaScript:
```javascript
// Line 779: Adjust rotation interval if needed
terminalInterval = setInterval(switchTerminal, 8000);
```

## Troubleshooting

### Diver Animation Not Working

1. **Check Console**: Look for spritesheet loading errors
2. **Verify Files**: Ensure `diver-spritesheet.json` and images exist
3. **Server Required**: Must use HTTP server, not `file://` protocol
4. **Debug Mode**: Set `DEBUG = true` (line 800) for console logging

### Images Not Loading

1. **Path Verification**: Check image paths match file structure
2. **WebP Support**: Ensure browser supports WebP or PNG fallback loads
3. **CORS Issues**: Use local server instead of opening HTML directly

### Performance Issues

1. **Reduce Animation Complexity**: Increase interval timings
2. **Disable Background**: Remove `body::before` wall image
3. **Simplify Gradients**: Further reduce gradient layers in feature cards

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Deep-Codebase - Extract • Analyze • Integrate
