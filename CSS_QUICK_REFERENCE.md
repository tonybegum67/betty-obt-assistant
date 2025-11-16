# 🎨 CSS Quick Reference - Betty Design System

Quick copy-paste snippets for common styling patterns.

---

## 🎯 Common Patterns

### Modern Button
```css
background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600));
padding: var(--space-3) var(--space-6);
border-radius: var(--radius-md);
box-shadow: var(--shadow-md);
transition: all var(--transition-base);
font-weight: var(--font-semibold);
color: white;
```

### Card Container
```css
background: white;
padding: var(--space-6);
border-radius: var(--radius-lg);
box-shadow: var(--shadow-md);
border: 1px solid var(--color-gray-200);
transition: all var(--transition-base);
```

### Success Message
```css
background: linear-gradient(135deg, #f0fff4 0%, var(--color-success-light) 100%);
color: var(--color-success);
padding: var(--space-4);
border-radius: var(--radius-lg);
border-left: 4px solid var(--color-success);
box-shadow: var(--shadow-sm);
```

### Hover Effect
```css
.element:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}
```

---

## 📦 Layout Utilities

### Spacing
```css
/* Padding */
padding: var(--space-4);              /* 16px all sides */
padding: var(--space-2) var(--space-4); /* 8px vertical, 16px horizontal */

/* Margin */
margin-bottom: var(--space-6);        /* 24px */
gap: var(--space-2);                  /* 8px (for flexbox/grid) */
```

### Borders
```css
border-radius: var(--radius-md);      /* 8px */
border: 1px solid var(--color-gray-200);
```

---

## 🎨 Color Usage

### Backgrounds
```css
background: var(--color-gray-50);     /* Light gray */
background: var(--color-primary-500); /* Primary purple */
```

### Text Colors
```css
color: var(--color-gray-800);         /* Primary text */
color: var(--color-gray-500);         /* Secondary text */
color: var(--color-primary-600);      /* Accent text */
```

### Borders
```css
border-color: var(--color-gray-200);  /* Default border */
border-color: var(--color-primary-500); /* Accent border */
```

---

## ✨ Animations

### Slide In (from bottom)
```css
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.element {
    animation: slideIn 0.4s ease-out;
}
```

### Fade In
```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.element {
    animation: fadeIn 0.5s ease-in;
}
```

### Pulse (for loading)
```css
@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.element {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

---

## 🌈 Gradient Presets

### Primary Gradient
```css
background: linear-gradient(135deg, var(--color-primary-500) 0%, var(--color-primary-600) 100%);
```

### Success Gradient
```css
background: linear-gradient(135deg, var(--color-success) 0%, #38a169 100%);
```

### Soft Gradient
```css
background: linear-gradient(135deg, var(--color-gray-50) 0%, #ffffff 100%);
```

### Text Gradient
```css
background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600));
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
```

---

## 🎭 State Styles

### Default State
```css
.button {
    background: var(--color-primary-500);
    box-shadow: var(--shadow-md);
    transition: all var(--transition-base);
}
```

### Hover State
```css
.button:hover {
    background: var(--color-primary-600);
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}
```

### Active State
```css
.button:active {
    transform: translateY(0);
    box-shadow: var(--shadow-sm);
}
```

### Focus State (Accessibility)
```css
.button:focus-visible {
    outline: 3px solid var(--color-primary-500);
    outline-offset: 2px;
}
```

### Disabled State
```css
.button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    box-shadow: none;
}
```

---

## 📱 Responsive Patterns

### Mobile-First Breakpoints
```css
/* Base styles (mobile) */
.element {
    padding: var(--space-4);
}

/* Tablet and up */
@media (min-width: 768px) {
    .element {
        padding: var(--space-6);
    }
}

/* Desktop and up */
@media (min-width: 1024px) {
    .element {
        padding: var(--space-8);
    }
}
```

---

## 🔧 Utility Patterns

### Centered Content
```css
.centered {
    display: flex;
    align-items: center;
    justify-content: center;
}
```

### Vertical Stack
```css
.stack {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
}
```

### Horizontal Row
```css
.row {
    display: flex;
    gap: var(--space-4);
    align-items: center;
}
```

### Grid Layout
```css
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--space-6);
}
```

---

## 🎨 Component Styling Examples

### Badge
```css
.badge {
    display: inline-block;
    padding: var(--space-1) var(--space-3);
    background: var(--color-primary-100);
    color: var(--color-primary-700);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
}
```

### Tooltip
```css
.tooltip {
    position: absolute;
    background: var(--color-gray-900);
    color: white;
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    box-shadow: var(--shadow-lg);
    z-index: var(--z-tooltip);
}
```

### Alert Box
```css
.alert {
    padding: var(--space-4);
    border-radius: var(--radius-lg);
    border-left: 4px solid;
    box-shadow: var(--shadow-sm);
}

.alert-success {
    background: var(--color-success-light);
    border-left-color: var(--color-success);
    color: var(--color-success);
}

.alert-warning {
    background: var(--color-warning-light);
    border-left-color: var(--color-warning);
    color: var(--color-warning);
}
```

### Loading Spinner
```css
@keyframes spin {
    to { transform: rotate(360deg); }
}

.spinner {
    border: 3px solid var(--color-gray-200);
    border-top-color: var(--color-primary-500);
    border-radius: var(--radius-full);
    width: 40px;
    height: 40px;
    animation: spin 0.8s linear infinite;
}
```

---

## 📊 Typography Hierarchy

### Heading 1
```css
font-size: var(--text-4xl);
font-weight: var(--font-bold);
color: var(--color-gray-800);
line-height: 1.2;
```

### Heading 2
```css
font-size: var(--text-2xl);
font-weight: var(--font-semibold);
color: var(--color-gray-800);
line-height: 1.3;
```

### Body Text
```css
font-size: var(--text-base);
font-weight: var(--font-normal);
color: var(--color-gray-700);
line-height: 1.6;
```

### Caption/Small Text
```css
font-size: var(--text-sm);
font-weight: var(--font-normal);
color: var(--color-gray-500);
line-height: 1.5;
```

---

## 🎯 Pro Tips

1. **Always use design tokens** instead of hardcoded values
2. **Layer shadows** for depth: `box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255,255,255,0.1);`
3. **Combine transitions** for smooth effects: `transition: all var(--transition-base);`
4. **Use focus-visible** instead of focus for better accessibility
5. **Gradient overlays** for depth: `background: linear-gradient(overlay), var(--color-primary-500);`

---

**Last Updated:** 2025-01-XX
