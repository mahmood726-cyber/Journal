import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ThemeConfig, getTheme, defaultTheme } from '../config/themes';

interface ThemeContextType {
  currentTheme: ThemeConfig;
  themeId: string;
  setTheme: (themeId: string) => void;
  toggleDarkMode: () => void;
  isDarkMode: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [themeId, setThemeId] = useState<string>('default');
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);
  const [currentTheme, setCurrentTheme] = useState<ThemeConfig>(defaultTheme);

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('journalTheme');
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';

    if (savedTheme) {
      setThemeId(savedTheme);
      setCurrentTheme(getTheme(savedTheme));
    }

    if (savedDarkMode) {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  // Update theme
  const setTheme = (newThemeId: string) => {
    const theme = getTheme(newThemeId);
    setThemeId(newThemeId);
    setCurrentTheme(theme);
    localStorage.setItem('journalTheme', newThemeId);

    // Apply CSS custom properties to root
    applyThemeToDOM(theme);
  };

  // Toggle dark mode
  const toggleDarkMode = () => {
    const newDarkMode = !isDarkMode;
    setIsDarkMode(newDarkMode);
    localStorage.setItem('darkMode', String(newDarkMode));

    if (newDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  // Apply theme colors as CSS custom properties
  const applyThemeToDOM = (theme: ThemeConfig) => {
    const root = document.documentElement;

    // Apply primary colors
    Object.entries(theme.colors.primary).forEach(([shade, color]) => {
      root.style.setProperty(`--color-primary-${shade}`, color);
    });

    // Apply gray colors
    Object.entries(theme.colors.gray).forEach(([shade, color]) => {
      root.style.setProperty(`--color-gray-${shade}`, color);
    });

    // Apply semantic colors
    root.style.setProperty('--color-success', theme.colors.success);
    root.style.setProperty('--color-warning', theme.colors.warning);
    root.style.setProperty('--color-error', theme.colors.error);
    root.style.setProperty('--color-info', theme.colors.info);
    root.style.setProperty('--color-background', theme.colors.background);
    root.style.setProperty('--color-surface', theme.colors.surface);

    // Apply text colors
    root.style.setProperty('--color-text-primary', theme.colors.text.primary);
    root.style.setProperty('--color-text-secondary', theme.colors.text.secondary);
    root.style.setProperty('--color-text-disabled', theme.colors.text.disabled);

    // Apply typography
    root.style.setProperty('--font-sans', theme.typography.fontFamily.sans.join(', '));
    root.style.setProperty('--font-serif', theme.typography.fontFamily.serif.join(', '));
    root.style.setProperty('--font-mono', theme.typography.fontFamily.mono.join(', '));

    // Apply border radius
    root.style.setProperty('--border-radius', theme.borderRadius);
  };

  const value: ThemeContextType = {
    currentTheme,
    themeId,
    setTheme,
    toggleDarkMode,
    isDarkMode,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Hook to get current theme colors
export const useThemeColors = () => {
  const { currentTheme } = useTheme();
  return currentTheme.colors;
};

// Hook to get current typography
export const useThemeTypography = () => {
  const { currentTheme } = useTheme();
  return currentTheme.typography;
};
