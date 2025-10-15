# Hero Word Swap - Usage Guide

## Quick Start

### 1. Basic HTML Integration

```html
<h1>
  Extract <strong id="swapping-word">Functionality</strong> from Any Codebase
</h1>

<script src="hero-word-swap.js"></script>
```

The script will auto-initialize and begin animating the word with id `swapping-word`.

### 2. Custom Configuration

```html
<strong id="custom-word">Word</strong>

<script src="hero-word-swap.js"></script>
<script>
  // Custom configuration
  const swapper = new WordSwapper('custom-word', {
    words: ['First', 'Second', 'Third'],
    interval: 3000,      // 3 seconds between swaps
    fadeDuration: 500    // 500ms fade transition
  });
</script>
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `words` | Array | See below | Array of words to cycle through |
| `interval` | Number | 4000 | Time between word swaps (milliseconds) |
| `fadeDuration` | Number | 300 | Fade transition duration (milliseconds) |

### Default Words
```javascript
[
  'Functionality',
  'Features',
  'Capabilities',
  'Patterns',
  'Workflows',
  'Business Logic'
]
```

## Advanced Usage

### Manual Control

```javascript
const swapper = new WordSwapper('swapping-word');

// Stop animation
swapper.stop();

// Start animation
swapper.start();

// Destroy instance
swapper.destroy();
```

### Multiple Instances

```html
<p>Extract <strong id="word1">Functionality</strong> from any codebase</p>
<p>Analyze <strong id="word2">Patterns</strong> automatically</p>

<script>
  new WordSwapper('word1', {
    words: ['Functionality', 'Features', 'Logic'],
    interval: 4000
  });

  new WordSwapper('word2', {
    words: ['Patterns', 'Architecture', 'Structure'],
    interval: 3000
  });
</script>
```

### React Integration

```jsx
import { useEffect, useRef } from 'react';

function HeroSection() {
  const wordRef = useRef(null);
  const swapperRef = useRef(null);

  useEffect(() => {
    if (wordRef.current && !swapperRef.current) {
      swapperRef.current = new WordSwapper(wordRef.current.id, {
        words: ['Functionality', 'Features', 'Capabilities'],
        interval: 4000
      });
    }

    return () => {
      if (swapperRef.current) {
        swapperRef.current.destroy();
      }
    };
  }, []);

  return (
    <h1>
      Extract <strong id="swapping-word" ref={wordRef}>Functionality</strong> from Any Codebase
    </h1>
  );
}
```

### Vue Integration

```vue
<template>
  <h1>
    Extract <strong id="swapping-word">{{ currentWord }}</strong> from Any Codebase
  </h1>
</template>

<script>
export default {
  data() {
    return {
      currentWord: 'Functionality',
      swapper: null
    };
  },
  mounted() {
    this.swapper = new WordSwapper('swapping-word', {
      words: ['Functionality', 'Features', 'Capabilities'],
      interval: 4000
    });
  },
  beforeUnmount() {
    if (this.swapper) {
      this.swapper.destroy();
    }
  }
};
</script>
```

## Styling Recommendations

### Basic Styling
```css
#swapping-word {
  font-weight: 800;
  color: #ffd700;
  display: inline-block;
  min-width: 200px; /* Prevents layout shift */
  text-align: center;
}
```

### Enhanced Styling
```css
#swapping-word {
  font-weight: 800;
  color: #ffd700;
  text-shadow: 0 2px 10px rgba(255, 215, 0, 0.3);
  background: rgba(255, 255, 255, 0.1);
  padding: 0.2em 0.5em;
  border-radius: 8px;
  display: inline-block;
  min-width: 200px;
  text-align: center;
}
```

### Gradient Text Effect
```css
#swapping-word {
  background: linear-gradient(45deg, #ffd700, #ff6b6b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
  display: inline-block;
  min-width: 200px;
}
```

## Performance Notes

- **Memory Efficient**: Uses a single interval timer, no memory leaks
- **Smooth Animations**: CSS transitions for hardware-accelerated performance
- **No Dependencies**: Pure vanilla JavaScript, no libraries required
- **Small Footprint**: ~2KB minified

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- IE11: Not supported (uses modern JavaScript)

## Troubleshooting

### Word not animating?
- Ensure element has correct `id` attribute
- Check JavaScript console for errors
- Verify script loads after DOM element

### Layout shifting during animation?
- Add `min-width` to the word element
- Use `display: inline-block`
- Set fixed width if word lengths vary significantly

### Animation timing issues?
- Adjust `interval` and `fadeDuration` values
- Ensure `fadeDuration * 2 < interval` for smooth transitions

## License

MIT - Free for commercial and personal use
