/**
 * Theme Configuration System
 * Multiple pre-built themes for journal customization
 */

export interface ColorPalette {
  primary: {
    50: string;
    100: string;
    200: string;
    300: string;
    400: string;
    500: string; // Base color
    600: string;
    700: string;
    800: string;
    900: string;
  };
  gray: {
    50: string;
    100: string;
    200: string;
    300: string;
    400: string;
    500: string;
    600: string;
    700: string;
    800: string;
    900: string;
  };
  success: string;
  warning: string;
  error: string;
  info: string;
  background: string;
  surface: string;
  text: {
    primary: string;
    secondary: string;
    disabled: string;
  };
}

export interface Typography {
  fontFamily: {
    sans: string[];
    serif: string[];
    mono: string[];
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
    '5xl': string;
  };
  lineHeight: {
    tight: number;
    normal: number;
    relaxed: number;
  };
}

export interface ThemeConfig {
  id: string;
  name: string;
  description: string;
  colors: ColorPalette;
  typography: Typography;
  borderRadius: string;
  category: 'academic' | 'modern' | 'medical' | 'nature' | 'minimal' | 'humanities' | 'law' | 'technology' | 'social' | 'business' | 'bold';
}

// Default Theme (Indigo/Purple - Current)
export const defaultTheme: ThemeConfig = {
  id: 'default',
  name: 'Diamond Default',
  description: 'Modern indigo and purple gradient theme',
  category: 'modern',
  colors: {
    primary: {
      50: '#EEF2FF',
      100: '#E0E7FF',
      200: '#C7D2FE',
      300: '#A5B4FC',
      400: '#818CF8',
      500: '#6366F1',
      600: '#4F46E5',
      700: '#4338CA',
      800: '#3730A3',
      900: '#312E81',
    },
    gray: {
      50: '#F9FAFB',
      100: '#F3F4F6',
      200: '#E5E7EB',
      300: '#D1D5DB',
      400: '#9CA3AF',
      500: '#6B7280',
      600: '#4B5563',
      700: '#374151',
      800: '#1F2937',
      900: '#111827',
    },
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
    background: '#FFFFFF',
    surface: '#F9FAFB',
    text: {
      primary: '#111827',
      secondary: '#6B7280',
      disabled: '#9CA3AF',
    },
  },
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      serif: ['Merriweather', 'Georgia', 'serif'],
      mono: ['JetBrains Mono', 'Consolas', 'monospace'],
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
      '5xl': '3rem',
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  borderRadius: '0.5rem',
};

// Academic Classic Theme (Navy Blue)
export const academicClassicTheme: ThemeConfig = {
  id: 'academic-classic',
  name: 'Academic Classic',
  description: 'Traditional navy blue for established journals',
  category: 'academic',
  colors: {
    primary: {
      50: '#EFF6FF',
      100: '#DBEAFE',
      200: '#BFDBFE',
      300: '#93C5FD',
      400: '#60A5FA',
      500: '#1E40AF',
      600: '#1E3A8A',
      700: '#1E3A8A',
      800: '#1E3A8A',
      900: '#172554',
    },
    gray: {
      50: '#FAF8F5',
      100: '#F5F3F0',
      200: '#E8E5E1',
      300: '#D4CFC8',
      400: '#A8A29E',
      500: '#78716C',
      600: '#57534E',
      700: '#44403C',
      800: '#292524',
      900: '#1C1917',
    },
    success: '#059669',
    warning: '#D97706',
    error: '#DC2626',
    info: '#2563EB',
    background: '#FAF8F5',
    surface: '#FFFFFF',
    text: {
      primary: '#1C1917',
      secondary: '#57534E',
      disabled: '#A8A29E',
    },
  },
  typography: {
    fontFamily: {
      sans: ['Open Sans', 'system-ui', 'sans-serif'],
      serif: ['Merriweather', 'Georgia', 'Times New Roman', 'serif'],
      mono: ['Courier New', 'monospace'],
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
      '5xl': '3rem',
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.6,
      relaxed: 1.8,
    },
  },
  borderRadius: '0.25rem',
};

// Modern Science Theme (Teal)
export const modernScienceTheme: ThemeConfig = {
  id: 'modern-science',
  name: 'Modern Science',
  description: 'Fresh teal and orange for STEM journals',
  category: 'modern',
  colors: {
    primary: {
      50: '#F0FDFA',
      100: '#CCFBF1',
      200: '#99F6E4',
      300: '#5EEAD4',
      400: '#2DD4BF',
      500: '#0891B2',
      600: '#0E7490',
      700: '#155E75',
      800: '#164E63',
      900: '#134E4A',
    },
    gray: {
      50: '#F8FAFC',
      100: '#F1F5F9',
      200: '#E2E8F0',
      300: '#CBD5E1',
      400: '#94A3B8',
      500: '#64748B',
      600: '#475569',
      700: '#334155',
      800: '#1E293B',
      900: '#0F172A',
    },
    success: '#10B981',
    warning: '#F97316',
    error: '#EF4444',
    info: '#0EA5E9',
    background: '#FFFFFF',
    surface: '#F8FAFC',
    text: {
      primary: '#0F172A',
      secondary: '#475569',
      disabled: '#94A3B8',
    },
  },
  typography: {
    fontFamily: {
      sans: ['Inter', 'Helvetica Neue', 'Arial', 'sans-serif'],
      serif: ['PT Serif', 'Georgia', 'serif'],
      mono: ['Fira Code', 'monospace'],
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
      '5xl': '3rem',
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  borderRadius: '0.5rem',
};

// Medical Professional Theme (Blue)
export const medicalTheme: ThemeConfig = {
  id: 'medical',
  name: 'Medical Professional',
  description: 'Clean blue theme for health sciences',
  category: 'medical',
  colors: {
    primary: {
      50: '#EFF6FF',
      100: '#DBEAFE',
      200: '#BFDBFE',
      300: '#93C5FD',
      400: '#60A5FA',
      500: '#3B82F6',
      600: '#2563EB',
      700: '#1D4ED8',
      800: '#1E40AF',
      900: '#1E3A8A',
    },
    gray: {
      50: '#F9FAFB',
      100: '#F3F4F6',
      200: '#E5E7EB',
      300: '#D1D5DB',
      400: '#9CA3AF',
      500: '#6B7280',
      600: '#4B5563',
      700: '#374151',
      800: '#1F2937',
      900: '#111827',
    },
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#06B6D4',
    background: '#FFFFFF',
    surface: '#F9FAFB',
    text: {
      primary: '#111827',
      secondary: '#4B5563',
      disabled: '#9CA3AF',
    },
  },
  typography: {
    fontFamily: {
      sans: ['Roboto', 'Arial', 'sans-serif'],
      serif: ['Lora', 'Georgia', 'serif'],
      mono: ['Roboto Mono', 'monospace'],
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
      '5xl': '3rem',
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  borderRadius: '0.5rem',
};

// Nature & Environment Theme (Green)
export const natureTheme: ThemeConfig = {
  id: 'nature',
  name: 'Nature & Environment',
  description: 'Forest green for ecology journals',
  category: 'nature',
  colors: {
    primary: {
      50: '#F0FDF4',
      100: '#DCFCE7',
      200: '#BBF7D0',
      300: '#86EFAC',
      400: '#4ADE80',
      500: '#16A34A',
      600: '#166534',
      700: '#15803D',
      800: '#166534',
      900: '#14532D',
    },
    gray: {
      50: '#FAFAF9',
      100: '#F5F5F4',
      200: '#E7E5E4',
      300: '#D6D3D1',
      400: '#A8A29E',
      500: '#78716C',
      600: '#57534E',
      700: '#44403C',
      800: '#292524',
      900: '#1C1917',
    },
    success: '#22C55E',
    warning: '#EAB308',
    error: '#EF4444',
    info: '#0EA5E9',
    background: '#FAFAF9',
    surface: '#FFFFFF',
    text: {
      primary: '#1C1917',
      secondary: '#57534E',
      disabled: '#A8A29E',
    },
  },
  typography: {
    fontFamily: {
      sans: ['Lato', 'system-ui', 'sans-serif'],
      serif: ['Source Serif Pro', 'Georgia', 'serif'],
      mono: ['Source Code Pro', 'monospace'],
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
      '5xl': '3rem',
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.6,
      relaxed: 1.8,
    },
  },
  borderRadius: '0.375rem',
};

// Minimalist Theme (Black & White)
export const minimalistTheme: ThemeConfig = {
  id: 'minimalist',
  name: 'Minimalist Contemporary',
  description: 'Ultra-clean black and white',
  category: 'minimal',
  colors: {
    primary: {
      50: '#FAFAFA',
      100: '#F4F4F5',
      200: '#E4E4E7',
      300: '#D4D4D8',
      400: '#A1A1AA',
      500: '#71717A',
      600: '#52525B',
      700: '#3F3F46',
      800: '#27272A',
      900: '#18181B',
    },
    gray: {
      50: '#FAFAFA',
      100: '#F4F4F5',
      200: '#E4E4E7',
      300: '#D4D4D8',
      400: '#A1A1AA',
      500: '#71717A',
      600: '#52525B',
      700: '#3F3F46',
      800: '#27272A',
      900: '#18181B',
    },
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
    background: '#FFFFFF',
    surface: '#FAFAFA',
    text: {
      primary: '#18181B',
      secondary: '#52525B',
      disabled: '#A1A1AA',
    },
  },
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      serif: ['Crimson Pro', 'Georgia', 'serif'],
      mono: ['IBM Plex Mono', 'monospace'],
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
      '5xl': '3rem',
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  borderRadius: '0.125rem',
};

// Humanities & Arts Theme (Burgundy/Wine)
export const humanitiesTheme: ThemeConfig = {
  id: 'humanities',
  name: 'Humanities & Arts',
  description: 'Warm burgundy for humanities and arts journals',
  category: 'humanities',
  colors: {
    primary: {
      50: '#FDF2F8',
      100: '#FCE7F3',
      200: '#FBCFE8',
      300: '#F9A8D4',
      400: '#F472B6',
      500: '#881337',
      600: '#9F1239',
      700: '#881337',
      800: '#4C0519',
      900: '#3F0614',
    },
    gray: {
      50: '#FAF8F5',
      100: '#F5F3F0',
      200: '#E8E5E1',
      300: '#D4CFC8',
      400: '#A8A29E',
      500: '#78716C',
      600: '#57534E',
      700: '#44403C',
      800: '#292524',
      900: '#1C1917',
    },
    success: '#059669',
    warning: '#D97706',
    error: '#DC2626',
    info: '#2563EB',
    background: '#FFFBF5',
    surface: '#FFFFFF',
    text: {
      primary: '#1C1917',
      secondary: '#57534E',
      disabled: '#A8A29E',
    },
  },
  typography: {
    fontFamily: {
      sans: ['Playfair Display', 'Georgia', 'serif'],
      serif: ['Crimson Text', 'Georgia', 'Times New Roman', 'serif'],
      mono: ['Courier New', 'monospace'],
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
      '5xl': '3rem',
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.65,
      relaxed: 1.85,
    },
  },
  borderRadius: '0.25rem',
};

// Law & Justice Theme (Charcoal with Gold)
export const lawTheme: ThemeConfig = {
  id: 'law',
  name: 'Law & Justice',
  description: 'Professional charcoal and gold for law journals',
  category: 'law',
  colors: {
    primary: {
      50: '#F7F7F6',
      100: '#E3E3E0',
      200: '#C8C7C1',
      300: '#ADABA2',
      400: '#918F83',
      500: '#3A3731',
      600: '#2E2B26',
      700: '#23211D',
      800: '#1A1814',
      900: '#0F0E0B',
    },
    gray: {
      50: '#FAFAFA',
      100: '#F4F4F5',
      200: '#E4E4E7',
      300: '#D4D4D8',
      400: '#A1A1AA',
      500: '#71717A',
      600: '#52525B',
      700: '#3F3F46',
      800: '#27272A',
      900: '#18181B',
    },
    success: '#059669',
    warning: '#D97706',
    error: '#DC2626',
    info: '#2563EB',
    background: '#FFFFFF',
    surface: '#FAFAFA',
    text: {
      primary: '#0F0E0B',
      secondary: '#52525B',
      disabled: '#A1A1AA',
    },
  },
  typography: {
    fontFamily: {
      sans: ['EB Garamond', 'Georgia', 'serif'],
      serif: ['Baskerville', 'Georgia', 'Times New Roman', 'serif'],
      mono: ['Courier New', 'monospace'],
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
      '5xl': '3rem',
    },
    lineHeight: {
      tight: 1.3,
      normal: 1.7,
      relaxed: 1.9,
    },
  },
  borderRadius: '0.125rem',
};

// Technology & Engineering Theme (Orange/Tech Blue)
export const technologyTheme: ThemeConfig = {
  id: 'technology',
  name: 'Technology & Engineering',
  description: 'Vibrant orange and blue for tech journals',
  category: 'technology',
  colors: {
    primary: {
      50: '#FFF7ED',
      100: '#FFEDD5',
      200: '#FED7AA',
      300: '#FDBA74',
      400: '#FB923C',
      500: '#F97316',
      600: '#EA580C',
      700: '#C2410C',
      800: '#9A3412',
      900: '#7C2D12',
    },
    gray: {
      50: '#F8FAFC',
      100: '#F1F5F9',
      200: '#E2E8F0',
      300: '#CBD5E1',
      400: '#94A3B8',
      500: '#64748B',
      600: '#475569',
      700: '#334155',
      800: '#1E293B',
      900: '#0F172A',
    },
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#06B6D4',
    background: '#FFFFFF',
    surface: '#F8FAFC',
    text: {
      primary: '#0F172A',
      secondary: '#475569',
      disabled: '#94A3B8',
    },
  },
  typography: {
    fontFamily: {
      sans: ['Poppins', 'system-ui', 'sans-serif'],
      serif: ['PT Serif', 'Georgia', 'serif'],
      mono: ['JetBrains Mono', 'Consolas', 'monospace'],
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
      '5xl': '3rem',
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  borderRadius: '0.75rem',
};

// Social Sciences Theme (Purple/Violet)
export const socialSciencesTheme: ThemeConfig = {
  id: 'social-sciences',
  name: 'Social Sciences',
  description: 'Rich purple for social science journals',
  category: 'social',
  colors: {
    primary: {
      50: '#FAF5FF',
      100: '#F3E8FF',
      200: '#E9D5FF',
      300: '#D8B4FE',
      400: '#C084FC',
      500: '#7C3AED',
      600: '#7C3AED',
      700: '#6D28D9',
      800: '#5B21B6',
      900: '#4C1D95',
    },
    gray: {
      50: '#F9FAFB',
      100: '#F3F4F6',
      200: '#E5E7EB',
      300: '#D1D5DB',
      400: '#9CA3AF',
      500: '#6B7280',
      600: '#4B5563',
      700: '#374151',
      800: '#1F2937',
      900: '#111827',
    },
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
    background: '#FFFFFF',
    surface: '#FAF5FF',
    text: {
      primary: '#111827',
      secondary: '#4B5563',
      disabled: '#9CA3AF',
    },
  },
  typography: {
    fontFamily: {
      sans: ['Nunito Sans', 'system-ui', 'sans-serif'],
      serif: ['Source Serif Pro', 'Georgia', 'serif'],
      mono: ['Source Code Pro', 'monospace'],
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
      '5xl': '3rem',
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.6,
      relaxed: 1.8,
    },
  },
  borderRadius: '0.5rem',
};

// Business & Economics Theme (Navy with Gold)
export const businessTheme: ThemeConfig = {
  id: 'business',
  name: 'Business & Economics',
  description: 'Professional navy and gold for business journals',
  category: 'business',
  colors: {
    primary: {
      50: '#F0F9FF',
      100: '#E0F2FE',
      200: '#BAE6FD',
      300: '#7DD3FC',
      400: '#38BDF8',
      500: '#0C4A6E',
      600: '#075985',
      700: '#0369A1',
      800: '#0C4A6E',
      900: '#082F49',
    },
    gray: {
      50: '#F8FAFC',
      100: '#F1F5F9',
      200: '#E2E8F0',
      300: '#CBD5E1',
      400: '#94A3B8',
      500: '#64748B',
      600: '#475569',
      700: '#334155',
      800: '#1E293B',
      900: '#0F172A',
    },
    success: '#059669',
    warning: '#D97706',
    error: '#DC2626',
    info: '#0EA5E9',
    background: '#FFFFFF',
    surface: '#F8FAFC',
    text: {
      primary: '#0F172A',
      secondary: '#475569',
      disabled: '#94A3B8',
    },
  },
  typography: {
    fontFamily: {
      sans: ['Montserrat', 'system-ui', 'sans-serif'],
      serif: ['Lora', 'Georgia', 'serif'],
      mono: ['Roboto Mono', 'monospace'],
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
      '5xl': '3rem',
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.6,
      relaxed: 1.8,
    },
  },
  borderRadius: '0.375rem',
};

// Bright & Bold Theme (Vibrant Multi-Color)
export const brightBoldTheme: ThemeConfig = {
  id: 'bright-bold',
  name: 'Bright & Bold',
  description: 'Vibrant colors for modern interdisciplinary journals',
  category: 'bold',
  colors: {
    primary: {
      50: '#FDF4FF',
      100: '#FAE8FF',
      200: '#F5D0FE',
      300: '#F0ABFC',
      400: '#E879F9',
      500: '#D946EF',
      600: '#C026D3',
      700: '#A21CAF',
      800: '#86198F',
      900: '#701A75',
    },
    gray: {
      50: '#FAFAFA',
      100: '#F4F4F5',
      200: '#E4E4E7',
      300: '#D4D4D8',
      400: '#A1A1AA',
      500: '#71717A',
      600: '#52525B',
      700: '#3F3F46',
      800: '#27272A',
      900: '#18181B',
    },
    success: '#22C55E',
    warning: '#EAB308',
    error: '#EF4444',
    info: '#06B6D4',
    background: '#FFFFFF',
    surface: '#FAFAFA',
    text: {
      primary: '#18181B',
      secondary: '#52525B',
      disabled: '#A1A1AA',
    },
  },
  typography: {
    fontFamily: {
      sans: ['Work Sans', 'system-ui', 'sans-serif'],
      serif: ['Spectral', 'Georgia', 'serif'],
      mono: ['Fira Code', 'monospace'],
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
      '5xl': '3rem',
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  borderRadius: '1rem',
};

// Export all themes
export const themes: Record<string, ThemeConfig> = {
  default: defaultTheme,
  'academic-classic': academicClassicTheme,
  'modern-science': modernScienceTheme,
  medical: medicalTheme,
  nature: natureTheme,
  minimalist: minimalistTheme,
  humanities: humanitiesTheme,
  law: lawTheme,
  technology: technologyTheme,
  'social-sciences': socialSciencesTheme,
  business: businessTheme,
  'bright-bold': brightBoldTheme,
};

// Helper function to get theme by ID
export const getTheme = (themeId: string): ThemeConfig => {
  return themes[themeId] || defaultTheme;
};

// Helper function to get all themes by category
export const getThemesByCategory = (category: ThemeConfig['category']): ThemeConfig[] => {
  return Object.values(themes).filter((theme) => theme.category === category);
};

// Helper function to get theme names for dropdown
export const getThemeOptions = () => {
  return Object.values(themes).map((theme) => ({
    id: theme.id,
    name: theme.name,
    description: theme.description,
  }));
};
