/**
 * Hero Section Animated Word Swapper
 * Cycles through words with smooth fade transitions
 * No dependencies - vanilla JavaScript
 */

class WordSwapper {
  constructor(elementId, options = {}) {
    this.element = document.getElementById(elementId);
    if (!this.element) {
      console.error(`Element with id "${elementId}" not found`);
      return;
    }

    // Configuration
    this.words = options.words || [
      'Functionality',
      'Features',
      'Capabilities',
      'Patterns',
      'Workflows',
      'Business Logic'
    ];
    this.interval = options.interval || 4000; // 4 seconds
    this.fadeDuration = options.fadeDuration || 300; // 300ms fade

    // State
    this.currentIndex = 0;
    this.isAnimating = false;
    this.intervalId = null;

    // Initialize
    this.init();
  }

  init() {
    // Set initial word
    this.element.textContent = this.words[0];
    this.element.style.transition = `opacity ${this.fadeDuration}ms ease-in-out`;
    this.element.style.display = 'inline-block';
    this.element.style.minWidth = '200px'; // Prevent layout shift

    // Start animation cycle
    this.start();
  }

  fadeOut() {
    return new Promise(resolve => {
      this.element.style.opacity = '0';
      setTimeout(resolve, this.fadeDuration);
    });
  }

  fadeIn() {
    return new Promise(resolve => {
      this.element.style.opacity = '1';
      setTimeout(resolve, this.fadeDuration);
    });
  }

  async swapWord() {
    if (this.isAnimating) return;

    this.isAnimating = true;

    // Fade out current word
    await this.fadeOut();

    // Update to next word
    this.currentIndex = (this.currentIndex + 1) % this.words.length;
    this.element.textContent = this.words[this.currentIndex];

    // Fade in new word
    await this.fadeIn();

    this.isAnimating = false;
  }

  start() {
    // Clear any existing interval
    this.stop();

    // Start new interval
    this.intervalId = setInterval(() => {
      this.swapWord();
    }, this.interval);
  }

  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  destroy() {
    this.stop();
    this.element.style.opacity = '1';
  }
}

/**
 * Initialize the word swapper when DOM is ready
 * Usage: Add id="swapping-word" to the word element in your HTML
 */
function initHeroWordSwap() {
  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      new WordSwapper('swapping-word', {
        words: [
          'Functionality',
          'Features',
          'Capabilities',
          'Patterns',
          'Workflows',
          'Business Logic'
        ],
        interval: 4000,
        fadeDuration: 300
      });
    });
  } else {
    // DOM is already ready
    new WordSwapper('swapping-word', {
      words: [
        'Functionality',
        'Features',
        'Capabilities',
        'Patterns',
        'Workflows',
        'Business Logic'
      ],
      interval: 4000,
      fadeDuration: 300
    });
  }
}

// Auto-initialize
initHeroWordSwap();

// Export for module usage (optional)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = WordSwapper;
}
