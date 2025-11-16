# 🎨 Betty Design System

A modern, Tailwind-inspired design system for the Betty OBT Assistant application.

## Overview

This design system provides a consistent, scalable approach to styling using **CSS Custom Properties** (CSS Variables) instead of traditional CSS frameworks. This approach gives us:

✅ **Tailwind-like utility** without build process
✅ **Full design control** with minimal overhead
✅ **Streamlit compatibility** - works natively
✅ **Theme flexibility** - easy to switch between light/dark modes
✅ **Performance** - no external dependencies

---

## 🎨 Color System

### Primary Colors (Purple/Blue Theme)
```css
--color-primary-50: #f5f3ff   /* Lightest */
--color-primary-500: #667eea  /* Main brand color */
--color-primary-600: #764ba2  /* Darker variant */
--color-primary-900: #4c1d95  /* Darkest */
```

**Usage Examples:**
- Primary buttons: `var(--color-primary-500)`
- Hover states: `var(--color-primary-600)`
- Text accents: `var(--color-primary-700)`

### Semantic Colors
```css
--color-success: #48bb78      /* Green - success states */
--color-info: #4299e1         /* Blue - informational */
--color-warning: #ed8936      /* Orange - warnings */
--color-error: #f56565        /* Red - errors */
```

### Neutral Grays
```css
--color-gray-50: #f7fafc      /* Backgrounds */
--color-gray-200: #e2e8f0     /* Borders */
--color-gray-500: #718096     /* Secondary text */
--color-gray-800: #1a202c     /* Primary text */
```

---

## 📏 Spacing Scale

Consistent spacing using a 4px base unit:

```css
--space-1: 0.25rem   /* 4px  - Tight spacing */
--space-2: 0.5rem    /* 8px  - Small gaps */
--space-4: 1rem      /* 16px - Default spacing */
--space-6: 1.5rem    /* 24px - Medium spacing */
--space-8: 2rem      /* 32px - Large spacing */
--space-12: 3rem     /* 48px - Section spacing */
```

**Usage:**
```css
padding: var(--space-4);
margin-bottom: var(--space-6);
gap: var(--space-2);
```

---

## 🔲 Border Radius

```css
--radius-sm: 0.25rem   /* 4px  - Small elements */
--radius-md: 0.5rem    /* 8px  - Buttons, inputs */
--radius-lg: 0.75rem   /* 12px - Cards, messages */
--radius-xl: 1rem      /* 16px - Large containers */
--radius-full: 9999px  /* Circular elements */
```

---

## 🌑 Shadows

Depth and elevation using consistent shadow scales:

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05)       /* Subtle */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1)     /* Default */
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1)   /* Elevated */
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1)   /* High elevation */
```

**Usage:**
- Cards: `var(--shadow-md)`
- Hover states: `var(--shadow-lg)`
- Modals/Popups: `var(--shadow-xl)`

---

## ✍️ Typography

### Font Sizes
```css
--text-xs: 0.75rem     /* 12px - Captions */
--text-sm: 0.875rem    /* 14px - Small text */
--text-base: 1rem      /* 16px - Body text */
--text-lg: 1.125rem    /* 18px - Large body */
--text-xl: 1.25rem     /* 20px - Subheadings */
--text-2xl: 1.5rem     /* 24px - Headings */
--text-4xl: 2.25rem    /* 36px - Large headings */
```

### Font Weights
```css
--font-normal: 400     /* Regular text */
--font-medium: 500     /* Emphasized text */
--font-semibold: 600   /* Subheadings */
--font-bold: 700       /* Headings */
```

---

## ⚡ Transitions

Smooth, consistent animations:

```css
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1)   /* Quick feedback */
--transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1)   /* Default */
--transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1)   /* Smooth effects */
```

**Easing Function:** `cubic-bezier(0.4, 0, 0.2, 1)` - Same as Tailwind's default

---

## 🎯 Utility Classes

### Gradients
```css
.gradient-primary  /* Purple gradient for primary elements */
.gradient-success  /* Green gradient for success states */
.gradient-soft     /* Subtle gray gradient for backgrounds */
```

### Text Effects
```css
.text-gradient     /* Gradient text effect */
```

### Shadows
```css
.shadow-hover      /* Apply on hover for elevation */
```

### Transitions
```css
.transition-all    /* Smooth transition for all properties */
```

---

## 🎨 Component Examples

### Button Styling
```css
.my-button {
    background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600));
    padding: var(--space-3) var(--space-6);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    transition: all var(--transition-base);
    font-weight: var(--font-semibold);
}

.my-button:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}
```

### Card Styling
```css
.my-card {
    background: white;
    padding: var(--space-6);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    border: 1px solid var(--color-gray-200);
}
```

### Message Styling
```css
.success-message {
    background: var(--color-success-light);
    color: var(--color-success);
    padding: var(--space-4);
    border-radius: var(--radius-lg);
    border-left: 4px solid var(--color-success);
}
```

---

## 🌓 Dark Mode Support (Future)

All variables are scoped to `:root` and can be easily overridden for dark mode:

```css
@media (prefers-color-scheme: dark) {
    :root {
        --color-gray-50: #171923;
        --color-gray-900: #f7fafc;
        /* Invert grayscale */
    }
}
```

Or with a class-based approach:
```css
.dark-mode {
    --color-gray-50: #171923;
    /* Override variables */
}
```

---

## 🔧 Implementation Guidelines

### ✅ Do's
- Use design tokens for all spacing, colors, and sizes
- Apply consistent border radius scales
- Use semantic color names (`--color-success`) not hex values
- Leverage utility classes for common patterns
- Maintain consistent transition durations

### ❌ Don'ts
- Don't hardcode colors - use CSS variables
- Don't use arbitrary spacing - stick to the scale
- Don't mix different shadow styles
- Don't skip transitions - they improve UX

---

## 📊 Comparison to Tailwind CSS

| Feature | Tailwind CSS | Betty Design System |
|---------|-------------|---------------------|
| **Utility Classes** | Yes (extensive) | Limited (gradients, shadows) |
| **Design Tokens** | Via config | CSS Custom Properties |
| **Build Process** | Required (JIT) | None - Pure CSS |
| **File Size** | ~3KB (minified) | ~5KB (embedded) |
| **Customization** | Via tailwind.config | Modify :root variables |
| **Streamlit Compatible** | ⚠️ Partial | ✅ Full |
| **Dark Mode** | Built-in | Manual implementation |

---

## 🚀 Future Enhancements

1. **Dark Mode Toggle** - Phase 2
2. **Component Library** - Reusable styled components
3. **Animation Library** - More keyframe animations
4. **Accessibility Utilities** - Focus states, screen reader support
5. **Responsive Utilities** - Breakpoint-based variables

---

## 📚 Resources

- [CSS Custom Properties (MDN)](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
- [Tailwind CSS Design System](https://tailwindcss.com/docs/customizing-colors)
- [Design Tokens Specification](https://tr.designtokens.org/format/)

---

**Version:** 1.0.0
**Last Updated:** 2025-01-XX
**Maintainer:** Betty Development Team
