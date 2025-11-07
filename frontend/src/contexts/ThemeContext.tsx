/**
 * Theme Context
 *
 * Provides global theme state management for the application.
 * Features:
 * - Current theme selection
 * - Dark mode toggle
 * - Theme customization
 * - Persist theme preferences to localStorage
 * - Apply theme to DOM
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import {
  Theme,
  getThemeById,
  applyTheme,
  nejm_blue,
} from '../themes/themeLibrary';

interface ThemeContextType {
  currentTheme: Theme;
  isDarkMode: boolean;
  customTheme: Theme | null;
  setTheme: (theme: Theme) => void;
  setThemeById: (themeId: string) => void;
  toggleDarkMode: () => void;
  setDarkMode: (enabled: boolean) => void;
  updateTheme: (updates: Partial<Theme>) => void;
  resetTheme: () => void;
  exportTheme: () => string;
  importTheme: (themeJson: string) => boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const STORAGE_KEYS = {
  THEME_ID: 'journal_theme_id',
  DARK_MODE: 'journal_dark_mode',
  CUSTOM_THEME: 'journal_custom_theme',
};

interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: Theme;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultTheme = nejm_blue,
}) => {
  const [currentTheme, setCurrentTheme] = useState<Theme>(defaultTheme);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [customTheme, setCustomTheme] = useState<Theme | null>(null);

  // Load theme preferences from localStorage on mount
  useEffect(() => {
    loadThemePreferences();
  }, []);

  // Apply theme whenever it changes
  useEffect(() => {
    applyTheme(currentTheme, isDarkMode);
  }, [currentTheme, isDarkMode]);

  // Save theme preferences to localStorage
  useEffect(() => {
    saveThemePreferences();
  }, [currentTheme, isDarkMode, customTheme]);

  const loadThemePreferences = () => {
    try {
      // Load dark mode preference
      const savedDarkMode = localStorage.getItem(STORAGE_KEYS.DARK_MODE);
      if (savedDarkMode !== null) {
        setIsDarkMode(savedDarkMode === 'true');
      }

      // Load custom theme if exists
      const savedCustomTheme = localStorage.getItem(STORAGE_KEYS.CUSTOM_THEME);
      if (savedCustomTheme) {
        const parsed = JSON.parse(savedCustomTheme) as Theme;
        setCustomTheme(parsed);
        setCurrentTheme(parsed);
        return;
      }

      // Load theme by ID
      const savedThemeId = localStorage.getItem(STORAGE_KEYS.THEME_ID);
      if (savedThemeId) {
        const theme = getThemeById(savedThemeId);
        if (theme) {
          setCurrentTheme(theme);
          return;
        }
      }

      // Use default theme
      setCurrentTheme(defaultTheme);
    } catch (error) {
      console.error('Failed to load theme preferences:', error);
      setCurrentTheme(defaultTheme);
    }
  };

  const saveThemePreferences = () => {
    try {
      localStorage.setItem(STORAGE_KEYS.THEME_ID, currentTheme.id);
      localStorage.setItem(STORAGE_KEYS.DARK_MODE, isDarkMode.toString());

      if (customTheme) {
        localStorage.setItem(STORAGE_KEYS.CUSTOM_THEME, JSON.stringify(customTheme));
      } else {
        localStorage.removeItem(STORAGE_KEYS.CUSTOM_THEME);
      }
    } catch (error) {
      console.error('Failed to save theme preferences:', error);
    }
  };

  const setTheme = (theme: Theme) => {
    setCurrentTheme(theme);
    setCustomTheme(null);
  };

  const setThemeById = (themeId: string) => {
    const theme = getThemeById(themeId);
    if (theme) {
      setTheme(theme);
    } else {
      console.warn(`Theme with id "${themeId}" not found`);
    }
  };

  const toggleDarkMode = () => {
    setIsDarkMode((prev) => !prev);
  };

  const setDarkMode = (enabled: boolean) => {
    setIsDarkMode(enabled);
  };

  const updateTheme = (updates: Partial<Theme>) => {
    const updatedTheme = {
      ...currentTheme,
      ...updates,
      colors: updates.colors ? { ...currentTheme.colors, ...updates.colors } : currentTheme.colors,
      typography: updates.typography
        ? { ...currentTheme.typography, ...updates.typography }
        : currentTheme.typography,
      layout: updates.layout ? { ...currentTheme.layout, ...updates.layout } : currentTheme.layout,
    };

    setCurrentTheme(updatedTheme);
    setCustomTheme(updatedTheme);
  };

  const resetTheme = () => {
    const originalTheme = getThemeById(currentTheme.id);
    if (originalTheme) {
      setCurrentTheme(originalTheme);
      setCustomTheme(null);
    }
  };

  const exportTheme = (): string => {
    const themeToExport = customTheme || currentTheme;
    return JSON.stringify(themeToExport, null, 2);
  };

  const importTheme = (themeJson: string): boolean => {
    try {
      const parsed = JSON.parse(themeJson) as Theme;

      // Validate theme structure
      if (!parsed.id || !parsed.name || !parsed.colors || !parsed.typography || !parsed.layout) {
        console.error('Invalid theme structure');
        return false;
      }

      setCurrentTheme(parsed);
      setCustomTheme(parsed);
      return true;
    } catch (error) {
      console.error('Failed to import theme:', error);
      return false;
    }
  };

  const value: ThemeContextType = {
    currentTheme,
    isDarkMode,
    customTheme,
    setTheme,
    setThemeById,
    toggleDarkMode,
    setDarkMode,
    updateTheme,
    resetTheme,
    exportTheme,
    importTheme,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

// Custom hook for using theme context
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// HOC for components that need theme
export function withTheme<P extends object>(
  Component: React.ComponentType<P & { theme: Theme; isDarkMode: boolean }>
) {
  return function ThemedComponent(props: P) {
    const { currentTheme, isDarkMode } = useTheme();
    return <Component {...props} theme={currentTheme} isDarkMode={isDarkMode} />;
  };
}

export default ThemeContext;
