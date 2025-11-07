# Theme System Integration Guide

This guide explains how to integrate the new theme system into your Next.js application.

## Overview

The theme system provides:
- **12 Professional Themes** - Inspired by NEJM, Lancet, Nature, Science, PLOS, Oxford, MIT, Springer, Elsevier, BMJ, IEEE, JSTOR
- **Full Customization** - Colors, typography, layout
- **Dark Mode Support** - Built-in dark mode for all themes
- **Live Preview** - See changes instantly
- **Persistent Preferences** - Themes saved to localStorage
- **Export/Import** - Share custom themes

## File Structure

```
frontend/src/
├── themes/
│   └── themeLibrary.ts          # 12 theme definitions + helpers
├── contexts/
│   └── ThemeContext.tsx         # Global theme state management
├── components/
│   ├── ThemeSelector.tsx        # Browse and select themes
│   ├── ThemeCustomizer.tsx      # Customize theme properties
│   └── ThemePreview.tsx         # Live theme preview
└── pages/
    └── admin/
        └── ThemeManagement.tsx  # Admin theme management page
```

## Step 1: Wrap Your App with ThemeProvider

### For Next.js App Router (`app/layout.tsx`)

```tsx
import { ThemeProvider } from '@/contexts/ThemeContext';
import { nejm_blue } from '@/themes/themeLibrary';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider defaultTheme={nejm_blue}>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

### For Next.js Pages Router (`_app.tsx`)

```tsx
import type { AppProps } from 'next/app';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { nejm_blue } from '@/themes/themeLibrary';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider defaultTheme={nejm_blue}>
      <Component {...pageProps} />
    </ThemeProvider>
  );
}
```

## Step 2: Use Theme in Components

### Using the `useTheme` Hook

```tsx
import { useTheme } from '@/contexts/ThemeContext';

export const MyComponent = () => {
  const {
    currentTheme,
    isDarkMode,
    setThemeById,
    toggleDarkMode,
  } = useTheme();

  return (
    <div style={{ backgroundColor: currentTheme.colors.background }}>
      <h1
        style={{
          color: currentTheme.colors.textPrimary,
          fontFamily: currentTheme.typography.fontFamily.heading,
        }}
      >
        Hello World
      </h1>

      <button onClick={toggleDarkMode}>
        Toggle Dark Mode
      </button>

      <button onClick={() => setThemeById('nature-green')}>
        Switch to Nature Theme
      </button>
    </div>
  );
};
```

### Using CSS Custom Properties

The theme system automatically applies CSS custom properties to the document root:

```tsx
// Component using CSS custom properties
export const StyledComponent = () => {
  return (
    <div className="container">
      <h1>Styled with CSS Variables</h1>
      <button className="primary-button">Click Me</button>
    </div>
  );
};

// CSS (or styled-jsx)
const styles = `
  .container {
    background: var(--background);
    color: var(--text-primary);
    padding: var(--spacing-lg);
    border-radius: var(--border-radius-md);
  }

  h1 {
    font-family: var(--font-heading);
    font-size: var(--font-size-h1);
    font-weight: var(--font-weight-bold);
    color: var(--primary);
  }

  .primary-button {
    background: var(--primary);
    color: var(--text-on-primary);
    padding: var(--spacing-sm) var(--spacing-md);
    border: none;
    border-radius: var(--border-radius-sm);
    font-weight: var(--font-weight-semibold);
  }
`;
```

### Available CSS Custom Properties

**Colors:**
- `--primary`, `--primary-dark`, `--primary-light`
- `--secondary`, `--accent`
- `--background`, `--background-paper`
- `--text-primary`, `--text-secondary`, `--text-on-primary`
- `--success`, `--warning`, `--error`, `--info`
- `--border`, `--divider`

**Typography:**
- `--font-heading`, `--font-body`, `--font-mono`
- `--font-size-xs`, `--font-size-sm`, `--font-size-base`, `--font-size-lg`, `--font-size-xl`, `--font-size-h1`, `--font-size-h2`, `--font-size-h3`
- `--font-weight-normal`, `--font-weight-medium`, `--font-weight-semibold`, `--font-weight-bold`
- `--line-height-tight`, `--line-height-normal`, `--line-height-relaxed`

**Layout:**
- `--max-width`, `--sidebar-width`, `--header-height`
- `--spacing-xs`, `--spacing-sm`, `--spacing-md`, `--spacing-lg`, `--spacing-xl`
- `--border-radius-sm`, `--border-radius-md`, `--border-radius-lg`

## Step 3: Add Theme Management to Admin

Add a route for the theme management page:

### App Router (`app/admin/themes/page.tsx`)

```tsx
import ThemeManagement from '@/pages/admin/ThemeManagement';

export default function ThemesPage() {
  return <ThemeManagement />;
}
```

### Pages Router (`pages/admin/themes.tsx`)

```tsx
import ThemeManagement from '@/pages/admin/ThemeManagement';

export default ThemeManagement;
```

## Step 4: Add Theme Switcher to UI

Create a simple theme switcher component:

```tsx
import { useTheme } from '@/contexts/ThemeContext';
import { allThemes } from '@/themes/themeLibrary';

export const ThemeSwitcher = () => {
  const { currentTheme, isDarkMode, setTheme, toggleDarkMode } = useTheme();

  return (
    <div className="theme-switcher">
      <select
        value={currentTheme.id}
        onChange={(e) => {
          const theme = allThemes.find((t) => t.id === e.target.value);
          if (theme) setTheme(theme);
        }}
      >
        {allThemes.map((theme) => (
          <option key={theme.id} value={theme.id}>
            {theme.name}
          </option>
        ))}
      </select>

      <label>
        <input
          type="checkbox"
          checked={isDarkMode}
          onChange={toggleDarkMode}
        />
        Dark Mode
      </label>
    </div>
  );
};
```

## Advanced Usage

### Programmatic Theme Updates

```tsx
import { useTheme } from '@/contexts/ThemeContext';

export const CustomizeColors = () => {
  const { updateTheme } = useTheme();

  const changePrimaryColor = (color: string) => {
    updateTheme({
      colors: {
        primary: color,
      },
    });
  };

  return (
    <input
      type="color"
      onChange={(e) => changePrimaryColor(e.target.value)}
    />
  );
};
```

### Export/Import Themes

```tsx
import { useTheme } from '@/contexts/ThemeContext';

export const ThemeIOComponent = () => {
  const { exportTheme, importTheme } = useTheme();

  const handleExport = () => {
    const themeJson = exportTheme();
    // Download or send to server
    const blob = new Blob([themeJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'custom-theme.json';
    a.click();
  };

  const handleImport = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const json = e.target?.result as string;
      const success = importTheme(json);
      if (success) {
        alert('Theme imported successfully!');
      } else {
        alert('Failed to import theme');
      }
    };
    reader.readAsText(file);
  };

  return (
    <div>
      <button onClick={handleExport}>Export Theme</button>
      <input
        type="file"
        accept=".json"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleImport(file);
        }}
      />
    </div>
  );
};
```

### Using with Tailwind CSS

If you're using Tailwind, you can extend it with theme colors:

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: 'var(--primary)',
        secondary: 'var(--secondary)',
        accent: 'var(--accent)',
      },
      fontFamily: {
        heading: 'var(--font-heading)',
        body: 'var(--font-body)',
      },
    },
  },
};
```

Then use in components:

```tsx
<div className="bg-primary text-white p-4 rounded-md">
  <h1 className="font-heading text-2xl">Hello World</h1>
</div>
```

### Server-Side Rendering Considerations

For SSR, ensure themes are applied on the client side:

```tsx
'use client'; // Next.js 13+ App Router

import { useEffect } from 'react';
import { useTheme } from '@/contexts/ThemeContext';

export const ClientOnlyTheme = () => {
  const { currentTheme, isDarkMode } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null; // Avoid hydration mismatch
  }

  return (
    <div style={{ backgroundColor: currentTheme.colors.background }}>
      {/* Your content */}
    </div>
  );
};
```

## Available Themes

| Theme | Category | Style | Description |
|-------|----------|-------|-------------|
| NEJM Blue | Medical | Classic | New England Journal of Medicine style |
| Lancet Red | Medical | Bold | The Lancet's distinctive red theme |
| BMJ Clinical | Medical | Minimal | British Medical Journal clean style |
| Nature Green | Scientific | Modern | Nature's fresh green aesthetic |
| Science Blue | Scientific | Classic | Science magazine traditional look |
| PLOS Minimal | Scientific | Minimal | PLOS open access simplicity |
| Oxford Academic | Humanities | Classic | Oxford University Press style |
| JSTOR Humanities | Humanities | Modern | JSTOR's modern humanities theme |
| MIT Tech | Technical | Modern | MIT Technology Review style |
| IEEE Tech Blue | Technical | Academic | IEEE publication standard |
| Springer Professional | General | Modern | Springer Nature professional look |
| Elsevier Modern | General | Modern | Elsevier's contemporary design |

## Theme Context API Reference

### `useTheme()` Returns

```typescript
{
  currentTheme: Theme;              // Current active theme
  isDarkMode: boolean;              // Dark mode state
  customTheme: Theme | null;        // Custom theme if modified
  setTheme: (theme: Theme) => void; // Set theme object
  setThemeById: (id: string) => void; // Set theme by ID
  toggleDarkMode: () => void;       // Toggle dark mode
  setDarkMode: (enabled: boolean) => void; // Set dark mode
  updateTheme: (updates: Partial<Theme>) => void; // Update theme
  resetTheme: () => void;           // Reset to original
  exportTheme: () => string;        // Export as JSON
  importTheme: (json: string) => boolean; // Import from JSON
}
```

## Troubleshooting

### Themes not persisting across page refreshes

Make sure localStorage is available:

```tsx
if (typeof window !== 'undefined') {
  // localStorage operations
}
```

### CSS custom properties not updating

Ensure the ThemeProvider is wrapping your entire app and the `applyTheme` function is being called.

### Dark mode not working

Check if the theme has a `darkMode` property defined. Not all themes may have dark mode variants.

### Performance issues with theme switching

Themes are applied using CSS custom properties for optimal performance. If you experience issues, ensure you're not triggering unnecessary re-renders.

## Next Steps

1. Visit `/admin/themes` to explore and customize themes
2. Add a theme switcher to your navigation
3. Customize colors to match your brand
4. Export and share custom themes
5. Create your own themes by extending the base theme structure

## Support

For issues or questions about the theme system, please refer to:
- Theme Library: `frontend/src/themes/themeLibrary.ts`
- Context Implementation: `frontend/src/contexts/ThemeContext.tsx`
- Component Examples: `frontend/src/components/Theme*.tsx`
