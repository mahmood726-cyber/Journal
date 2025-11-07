/**
 * Professional Theme Library
 *
 * Inspired by OJS, NEJM, Lancet, Nature, Science, PLOS, and other top journals.
 * 12 carefully crafted themes covering different disciplines and design styles.
 */

export interface ThemeColors {
  primary: string;
  primaryDark: string;
  primaryLight: string;
  secondary: string;
  secondaryDark: string;
  secondaryLight: string;
  accent: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  border: string;
  success: string;
  warning: string;
  error: string;
  info: string;
}

export interface ThemeTypography {
  fontFamily: {
    heading: string;
    body: string;
    mono: string;
  };
  fontSize: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
    '4xl': string;
  };
  fontWeight: {
    normal: number;
    medium: number;
    semibold: number;
    bold: number;
  };
  lineHeight: {
    tight: number;
    normal: number;
    relaxed: number;
  };
}

export interface ThemeLayout {
  maxWidth: string;
  sidebarWidth: string;
  headerHeight: string;
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
    full: string;
  };
}

export interface Theme {
  id: string;
  name: string;
  description: string;
  category: 'medical' | 'scientific' | 'humanities' | 'technical' | 'general';
  style: 'modern' | 'classic' | 'minimal' | 'bold' | 'academic';
  colors: ThemeColors;
  typography: ThemeTypography;
  layout: ThemeLayout;
  darkMode?: ThemeColors;
  preview: string; // URL to preview image
}

// ==================== THEME 1: NEJM Blue (Medical Classic) ====================

export const nejm_blue: Theme = {
  id: 'nejm-blue',
  name: 'NEJM Blue',
  description: 'Classic medical journal style inspired by New England Journal of Medicine',
  category: 'medical',
  style: 'classic',
  colors: {
    primary: '#003d7a',      // NEJM deep blue
    primaryDark: '#002a54',
    primaryLight: '#0052a3',
    secondary: '#d32f2f',    // Red accent for importance
    secondaryDark: '#9a0007',
    secondaryLight: '#ff6659',
    accent: '#ffa726',       // Warm orange
    background: '#ffffff',
    surface: '#f8f9fa',
    text: '#1a1a1a',
    textSecondary: '#5f6368',
    border: '#e0e0e0',
    success: '#2e7d32',
    warning: '#f57c00',
    error: '#c62828',
    info: '#1976d2',
  },
  typography: {
    fontFamily: {
      heading: '"Merriweather", "Georgia", serif',
      body: '"Source Sans Pro", "Helvetica Neue", sans-serif',
      mono: '"Courier New", monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.6,
      relaxed: 1.8,
    },
  },
  layout: {
    maxWidth: '1200px',
    sidebarWidth: '280px',
    headerHeight: '80px',
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
    },
    borderRadius: {
      sm: '0.25rem',
      md: '0.375rem',
      lg: '0.5rem',
      full: '9999px',
    },
  },
  preview: '/themes/nejm-blue.jpg',
};

// ==================== THEME 2: Lancet Red (Medical Bold) ====================

export const lancet_red: Theme = {
  id: 'lancet-red',
  name: 'Lancet Red',
  description: 'Bold medical design inspired by The Lancet',
  category: 'medical',
  style: 'bold',
  colors: {
    primary: '#c8102e',      // Lancet red
    primaryDark: '#8b0000',
    primaryLight: '#e53935',
    secondary: '#1a1a1a',    // Deep black
    secondaryDark: '#000000',
    secondaryLight: '#424242',
    accent: '#ff9800',       // Amber accent
    background: '#ffffff',
    surface: '#fafafa',
    text: '#212121',
    textSecondary: '#757575',
    border: '#e0e0e0',
    success: '#388e3c',
    warning: '#f57c00',
    error: '#d32f2f',
    info: '#1976d2',
  },
  typography: {
    fontFamily: {
      heading: '"Playfair Display", "Times New Roman", serif',
      body: '"Lato", "Arial", sans-serif',
      mono: '"Roboto Mono", monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.625rem',
      '3xl': '2rem',
      '4xl': '2.5rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.3,
      normal: 1.65,
      relaxed: 1.85,
    },
  },
  layout: {
    maxWidth: '1280px',
    sidebarWidth: '300px',
    headerHeight: '90px',
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.75rem',
      xl: '2.5rem',
    },
    borderRadius: {
      sm: '0.125rem',
      md: '0.25rem',
      lg: '0.375rem',
      full: '9999px',
    },
  },
  preview: '/themes/lancet-red.jpg',
};

// ==================== THEME 3: Nature Green (Scientific Modern) ====================

export const nature_green: Theme = {
  id: 'nature-green',
  name: 'Nature Green',
  description: 'Clean scientific design inspired by Nature journal',
  category: 'scientific',
  style: 'modern',
  colors: {
    primary: '#006400',      // Nature dark green
    primaryDark: '#004d00',
    primaryLight: '#228b22',
    secondary: '#0277bd',    // Blue accent
    secondaryDark: '#01579b',
    secondaryLight: '#039be5',
    accent: '#ff6f00',       // Orange highlight
    background: '#ffffff',
    surface: '#f5f5f5',
    text: '#263238',
    textSecondary: '#546e7a',
    border: '#cfd8dc',
    success: '#43a047',
    warning: '#fb8c00',
    error: '#e53935',
    info: '#039be5',
  },
  typography: {
    fontFamily: {
      heading: '"Harding", "Helvetica Neue", sans-serif',
      body: '"Merriweather Sans", "Arial", sans-serif',
      mono: '"Fira Code", monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.3,
      normal: 1.6,
      relaxed: 1.75,
    },
  },
  layout: {
    maxWidth: '1200px',
    sidebarWidth: '260px',
    headerHeight: '75px',
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
    },
    borderRadius: {
      sm: '0.25rem',
      md: '0.5rem',
      lg: '0.75rem',
      full: '9999px',
    },
  },
  preview: '/themes/nature-green.jpg',
};

// ==================== THEME 4: Science Blue (Scientific Classic) ====================

export const science_blue: Theme = {
  id: 'science-blue',
  name: 'Science Blue',
  description: 'Authoritative scientific style inspired by Science magazine',
  category: 'scientific',
  style: 'classic',
  colors: {
    primary: '#1e3a8a',      // Deep blue
    primaryDark: '#1e293b',
    primaryLight: '#3b82f6',
    secondary: '#991b1b',    // Deep red
    secondaryDark: '#7f1d1d',
    secondaryLight: '#dc2626',
    accent: '#059669',       // Emerald green
    background: '#ffffff',
    surface: '#f9fafb',
    text: '#111827',
    textSecondary: '#6b7280',
    border: '#d1d5db',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
  },
  typography: {
    fontFamily: {
      heading: '"Crimson Pro", "Georgia", serif',
      body: '"Inter", "Segoe UI", sans-serif',
      mono: '"JetBrains Mono", monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.625,
      relaxed: 1.75,
    },
  },
  layout: {
    maxWidth: '1200px',
    sidebarWidth: '280px',
    headerHeight: '80px',
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
    },
    borderRadius: {
      sm: '0.25rem',
      md: '0.375rem',
      lg: '0.5rem',
      full: '9999px',
    },
  },
  preview: '/themes/science-blue.jpg',
};

// ==================== THEME 5: PLOS Minimal (Open Access) ====================

export const plos_minimal: Theme = {
  id: 'plos-minimal',
  name: 'PLOS Minimal',
  description: 'Clean open access design inspired by PLOS journals',
  category: 'scientific',
  style: 'minimal',
  colors: {
    primary: '#f68212',      // PLOS orange
    primaryDark: '#cc6600',
    primaryLight: '#ff9933',
    secondary: '#3c6e97',    // Blue
    secondaryDark: '#2c5577',
    secondaryLight: '#5a8bb7',
    accent: '#009688',       // Teal
    background: '#ffffff',
    surface: '#fafafa',
    text: '#333333',
    textSecondary: '#666666',
    border: '#eeeeee',
    success: '#4caf50',
    warning: '#ff9800',
    error: '#f44336',
    info: '#2196f3',
  },
  typography: {
    fontFamily: {
      heading: '"Source Sans Pro", "Helvetica", sans-serif',
      body: '"Source Sans Pro", "Arial", sans-serif',
      mono: '"Source Code Pro", monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.3,
      normal: 1.6,
      relaxed: 1.8,
    },
  },
  layout: {
    maxWidth: '1140px',
    sidebarWidth: '260px',
    headerHeight: '70px',
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
    },
    borderRadius: {
      sm: '0.25rem',
      md: '0.5rem',
      lg: '0.75rem',
      full: '9999px',
    },
  },
  preview: '/themes/plos-minimal.jpg',
};

// ==================== THEME 6: Oxford Academic (Humanities Classic) ====================

export const oxford_academic: Theme = {
  id: 'oxford-academic',
  name: 'Oxford Academic',
  description: 'Traditional humanities style inspired by Oxford University Press',
  category: 'humanities',
  style: 'classic',
  colors: {
    primary: '#002147',      // Oxford blue
    primaryDark: '#001530',
    primaryLight: '#003d7a',
    secondary: '#8b4513',    // Saddle brown
    secondaryDark: '#654321',
    secondaryLight: '#a0522d',
    accent: '#8b0000',       // Dark red
    background: '#fffef7',   // Cream
    surface: '#f9f8f0',
    text: '#2c2c2c',
    textSecondary: '#5c5c5c',
    border: '#d4d0c8',
    success: '#556b2f',
    warning: '#b8860b',
    error: '#8b0000',
    info: '#4682b4',
  },
  typography: {
    fontFamily: {
      heading: '"Baskerville", "Libre Baskerville", serif',
      body: '"Palatino", "Palatino Linotype", serif',
      mono: '"Courier New", monospace',
    },
    fontSize: {
      xs: '0.8125rem',
      sm: '0.9375rem',
      base: '1.0625rem',
      lg: '1.1875rem',
      xl: '1.375rem',
      '2xl': '1.625rem',
      '3xl': '2rem',
      '4xl': '2.5rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.4,
      normal: 1.75,
      relaxed: 1.95,
    },
  },
  layout: {
    maxWidth: '1000px',
    sidebarWidth: '240px',
    headerHeight: '90px',
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
    },
    borderRadius: {
      sm: '0.125rem',
      md: '0.25rem',
      lg: '0.375rem',
      full: '9999px',
    },
  },
  preview: '/themes/oxford-academic.jpg',
};

// ==================== THEME 7: MIT Tech (Technical Modern) ====================

export const mit_tech: Theme = {
  id: 'mit-tech',
  name: 'MIT Tech',
  description: 'Modern technical design inspired by MIT Press',
  category: 'technical',
  style: 'modern',
  colors: {
    primary: '#8a2432',      // MIT red
    primaryDark: '#6d1c28',
    primaryLight: '#a13240',
    secondary: '#2c3e50',    // Dark gray blue
    secondaryDark: '#1a252f',
    secondaryLight: '#34495e',
    accent: '#16a085',       // Turquoise
    background: '#ffffff',
    surface: '#f8f9fa',
    text: '#2c3e50',
    textSecondary: '#7f8c8d',
    border: '#bdc3c7',
    success: '#27ae60',
    warning: '#f39c12',
    error: '#c0392b',
    info: '#3498db',
  },
  typography: {
    fontFamily: {
      heading: '"Montserrat", "Helvetica Neue", sans-serif',
      body: '"Open Sans", "Segoe UI", sans-serif',
      mono: '"Inconsolata", "Consolas", monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.3,
      normal: 1.6,
      relaxed: 1.75,
    },
  },
  layout: {
    maxWidth: '1280px',
    sidebarWidth: '280px',
    headerHeight: '70px',
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
    },
    borderRadius: {
      sm: '0.375rem',
      md: '0.5rem',
      lg: '0.75rem',
      full: '9999px',
    },
  },
  preview: '/themes/mit-tech.jpg',
};

// ==================== THEME 8: Springer Professional (Multi-discipline) ====================

export const springer_pro: Theme = {
  id: 'springer-pro',
  name: 'Springer Professional',
  description: 'Professional multi-discipline design inspired by Springer',
  category: 'general',
  style: 'modern',
  colors: {
    primary: '#003e74',      // Springer blue
    primaryDark: '#002952',
    primaryLight: '#005396',
    secondary: '#e66f00',    // Orange
    secondaryDark: '#cc6200',
    secondaryLight: '#ff7c00',
    accent: '#7cb342',       // Light green
    background: '#ffffff',
    surface: '#f5f5f5',
    text: '#212121',
    textSecondary: '#616161',
    border: '#e0e0e0',
    success: '#43a047',
    warning: '#fb8c00',
    error: '#e53935',
    info: '#1e88e5',
  },
  typography: {
    fontFamily: {
      heading: '"PT Serif", "Georgia", serif',
      body: '"PT Sans", "Arial", sans-serif',
      mono: '"PT Mono", monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.3,
      normal: 1.6,
      relaxed: 1.8,
    },
  },
  layout: {
    maxWidth: '1200px',
    sidebarWidth: '280px',
    headerHeight: '80px',
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
    },
    borderRadius: {
      sm: '0.25rem',
      md: '0.375rem',
      lg: '0.5rem',
      full: '9999px',
    },
  },
  preview: '/themes/springer-pro.jpg',
};

// ==================== THEME 9: Elsevier Modern (General Modern) ====================

export const elsevier_modern: Theme = {
  id: 'elsevier-modern',
  name: 'Elsevier Modern',
  description: 'Clean modern design inspired by Elsevier journals',
  category: 'general',
  style: 'modern',
  colors: {
    primary: '#ff6c00',      // Elsevier orange
    primaryDark: '#e65100',
    primaryLight: '#ff8c1a',
    secondary: '#0c7489',    // Teal
    secondaryDark: '#085463',
    secondaryLight: '#0e94af',
    accent: '#7e57c2',       // Deep purple
    background: '#ffffff',
    surface: '#fafafa',
    text: '#1a1a1a',
    textSecondary: '#5f6368',
    border: '#e0e0e0',
    success: '#00897b',
    warning: '#ffb300',
    error: '#d32f2f',
    info: '#1976d2',
  },
  typography: {
    fontFamily: {
      heading: '"Nunito", "Trebuchet MS", sans-serif',
      body: '"Roboto", "Helvetica", sans-serif',
      mono: '"Roboto Mono", monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.3,
      normal: 1.6,
      relaxed: 1.75,
    },
  },
  layout: {
    maxWidth: '1240px',
    sidebarWidth: '280px',
    headerHeight: '70px',
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
    },
    borderRadius: {
      sm: '0.375rem',
      md: '0.5rem',
      lg: '0.75rem',
      full: '9999px',
    },
  },
  preview: '/themes/elsevier-modern.jpg',
};

// ==================== THEME 10: BMJ Clinical (Medical Minimal) ====================

export const bmj_clinical: Theme = {
  id: 'bmj-clinical',
  name: 'BMJ Clinical',
  description: 'Clean clinical design inspired by British Medical Journal',
  category: 'medical',
  style: 'minimal',
  colors: {
    primary: '#005eb8',      // NHS blue
    primaryDark: '#003d7a',
    primaryLight: '#0072ce',
    secondary: '#d5281b',    // Emergency red
    secondaryDark: '#b71c1c',
    secondaryLight: '#e53935',
    accent: '#00a499',       // Teal
    background: '#ffffff',
    surface: '#f0f4f5',
    text: '#212b32',
    textSecondary: '#425563',
    border: '#d8dde0',
    success: '#007f3b',
    warning: '#ffb81c',
    error: '#da291c',
    info: '#005eb8',
  },
  typography: {
    fontFamily: {
      heading: '"Frutiger", "Arial", sans-serif',
      body: '"Arial", "Helvetica", sans-serif',
      mono: '"Courier New", monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.3,
      normal: 1.6,
      relaxed: 1.75,
    },
  },
  layout: {
    maxWidth: '1200px',
    sidebarWidth: '260px',
    headerHeight: '70px',
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
    },
    borderRadius: {
      sm: '0.25rem',
      md: '0.375rem',
      lg: '0.5rem',
      full: '9999px',
    },
  },
  preview: '/themes/bmj-clinical.jpg',
};

// ==================== THEME 11: IEEE Tech Blue (Technical Academic) ====================

export const ieee_tech: Theme = {
  id: 'ieee-tech',
  name: 'IEEE Tech Blue',
  description: 'Technical academic style inspired by IEEE journals',
  category: 'technical',
  style: 'academic',
  colors: {
    primary: '#00629b',      // IEEE blue
    primaryDark: '#004771',
    primaryLight: '#0077c5',
    secondary: '#007fab',    // Lighter blue
    secondaryDark: '#005f84',
    secondaryLight: '#0099d5',
    accent: '#ffc72c',       // Gold
    background: '#ffffff',
    surface: '#f5f7fa',
    text: '#2c3e50',
    textSecondary: '#718096',
    border: '#cbd5e0',
    success: '#38a169',
    warning: '#dd6b20',
    error: '#e53e3e',
    info: '#3182ce',
  },
  typography: {
    fontFamily: {
      heading: '"Computer Modern Serif", "Times New Roman", serif',
      body: '"Verdana", "Geneva", sans-serif',
      mono: '"Consolas", "Monaco", monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.3,
      normal: 1.65,
      relaxed: 1.8,
    },
  },
  layout: {
    maxWidth: '1200px',
    sidebarWidth: '280px',
    headerHeight: '75px',
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
    },
    borderRadius: {
      sm: '0.25rem',
      md: '0.375rem',
      lg: '0.5rem',
      full: '9999px',
    },
  },
  preview: '/themes/ieee-tech.jpg',
};

// ==================== THEME 12: JSTOR Humanities (Humanities Modern) ====================

export const jstor_humanities: Theme = {
  id: 'jstor-humanities',
  name: 'JSTOR Humanities',
  description: 'Modern humanities design inspired by JSTOR',
  category: 'humanities',
  style: 'modern',
  colors: {
    primary: '#8b1a1a',      // Deep crimson
    primaryDark: '#6d1414',
    primaryLight: '#a52020',
    secondary: '#2c5f7c',    // Slate blue
    secondaryDark: '#1f4459',
    secondaryLight: '#3a7a9f',
    accent: '#c9850c',       // Golden brown
    background: '#fffef9',   // Warm white
    surface: '#f8f7f3',
    text: '#2d2d2d',
    textSecondary: '#666666',
    border: '#d9d5cf',
    success: '#4a7c59',
    warning: '#bf8c3f',
    error: '#c14543',
    info: '#4682b4',
  },
  typography: {
    fontFamily: {
      heading: '"Spectral", "Garamond", serif',
      body: '"Lora", "Georgia", serif',
      mono: '"Courier Prime", monospace',
    },
    fontSize: {
      xs: '0.8125rem',
      sm: '0.9375rem',
      base: '1.0625rem',
      lg: '1.1875rem',
      xl: '1.375rem',
      '2xl': '1.625rem',
      '3xl': '2rem',
      '4xl': '2.5rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.4,
      normal: 1.75,
      relaxed: 1.9,
    },
  },
  layout: {
    maxWidth: '1100px',
    sidebarWidth: '260px',
    headerHeight: '80px',
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
    },
    borderRadius: {
      sm: '0.25rem',
      md: '0.375rem',
      lg: '0.5rem',
      full: '9999px',
    },
  },
  preview: '/themes/jstor-humanities.jpg',
};

// ==================== Theme Collection ====================

export const themes: Theme[] = [
  nejm_blue,
  lancet_red,
  nature_green,
  science_blue,
  plos_minimal,
  oxford_academic,
  mit_tech,
  springer_pro,
  elsevier_modern,
  bmj_clinical,
  ieee_tech,
  jstor_humanities,
];

export const themesByCategory = {
  medical: themes.filter(t => t.category === 'medical'),
  scientific: themes.filter(t => t.category === 'scientific'),
  humanities: themes.filter(t => t.category === 'humanities'),
  technical: themes.filter(t => t.category === 'technical'),
  general: themes.filter(t => t.category === 'general'),
};

export const themesByStyle = {
  modern: themes.filter(t => t.style === 'modern'),
  classic: themes.filter(t => t.style === 'classic'),
  minimal: themes.filter(t => t.style === 'minimal'),
  bold: themes.filter(t => t.style === 'bold'),
  academic: themes.filter(t => t.style === 'academic'),
};

// Default theme
export const defaultTheme = nejm_blue;

// Helper function to get theme by ID
export function getThemeById(id: string): Theme | undefined {
  return themes.find(theme => theme.id === id);
}

// Helper function to apply theme to document
export function applyTheme(theme: Theme, useDarkMode: boolean = false): void {
  const colors = useDarkMode && theme.darkMode ? theme.darkMode : theme.colors;
  const root = document.documentElement;

  // Apply colors
  root.style.setProperty('--color-primary', colors.primary);
  root.style.setProperty('--color-primary-dark', colors.primaryDark);
  root.style.setProperty('--color-primary-light', colors.primaryLight);
  root.style.setProperty('--color-secondary', colors.secondary);
  root.style.setProperty('--color-secondary-dark', colors.secondaryDark);
  root.style.setProperty('--color-secondary-light', colors.secondaryLight);
  root.style.setProperty('--color-accent', colors.accent);
  root.style.setProperty('--color-background', colors.background);
  root.style.setProperty('--color-surface', colors.surface);
  root.style.setProperty('--color-text', colors.text);
  root.style.setProperty('--color-text-secondary', colors.textSecondary);
  root.style.setProperty('--color-border', colors.border);
  root.style.setProperty('--color-success', colors.success);
  root.style.setProperty('--color-warning', colors.warning);
  root.style.setProperty('--color-error', colors.error);
  root.style.setProperty('--color-info', colors.info);

  // Apply typography
  root.style.setProperty('--font-heading', theme.typography.fontFamily.heading);
  root.style.setProperty('--font-body', theme.typography.fontFamily.body);
  root.style.setProperty('--font-mono', theme.typography.fontFamily.mono);

  // Apply layout
  root.style.setProperty('--max-width', theme.layout.maxWidth);
  root.style.setProperty('--sidebar-width', theme.layout.sidebarWidth);
  root.style.setProperty('--header-height', theme.layout.headerHeight);

  // Save to localStorage
  localStorage.setItem('selectedTheme', theme.id);
  localStorage.setItem('darkMode', useDarkMode.toString());
}
