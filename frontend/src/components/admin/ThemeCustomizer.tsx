import React, { useState, useEffect } from 'react';
import { useTheme } from '../../context/ThemeContext';
import { themes, ThemeConfig, ColorPalette } from '../../config/themes';
import {
  SwatchIcon,
  PaintBrushIcon,
  EyeIcon,
  CheckCircleIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

interface ColorPickerProps {
  label: string;
  color: string;
  onChange: (color: string) => void;
}

const ColorPicker: React.FC<ColorPickerProps> = ({ label, color, onChange }) => {
  return (
    <div className="flex items-center justify-between">
      <label className="text-sm font-medium text-gray-700">{label}</label>
      <div className="flex items-center space-x-2">
        <input
          type="color"
          value={color}
          onChange={(e) => onChange(e.target.value)}
          className="h-10 w-20 rounded border-2 border-gray-300 cursor-pointer"
        />
        <input
          type="text"
          value={color}
          onChange={(e) => onChange(e.target.value)}
          className="px-3 py-2 text-sm border border-gray-300 rounded-md w-28 font-mono"
        />
      </div>
    </div>
  );
};

const ThemeCustomizer: React.FC = () => {
  const { currentTheme, setTheme, isDarkMode, toggleDarkMode } = useTheme();
  const [selectedThemeId, setSelectedThemeId] = useState(currentTheme.id);
  const [activeTab, setActiveTab] = useState<'select' | 'customize' | 'preview'>('select');
  const [customColors, setCustomColors] = useState<Partial<ColorPalette>>(currentTheme.colors);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  useEffect(() => {
    setCustomColors(currentTheme.colors);
  }, [currentTheme]);

  const handleThemeSelect = (themeId: string) => {
    setSelectedThemeId(themeId);
    setTheme(themeId);
    setCustomColors(themes[themeId].colors);
    setHasUnsavedChanges(false);
  };

  const handleColorChange = (colorPath: string, value: string) => {
    setCustomColors((prev) => {
      const updated = { ...prev };
      const keys = colorPath.split('.');
      let current: any = updated;

      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {};
        current = current[keys[i]];
      }

      current[keys[keys.length - 1]] = value;
      return updated;
    });
    setHasUnsavedChanges(true);
  };

  const handleSaveCustomTheme = () => {
    // In production, this would save to backend
    console.log('Saving custom theme:', customColors);
    // Apply custom colors to current theme
    const customTheme: ThemeConfig = {
      ...currentTheme,
      id: 'custom',
      name: 'Custom Theme',
      colors: customColors as ColorPalette,
    };
    localStorage.setItem('customTheme', JSON.stringify(customTheme));
    setHasUnsavedChanges(false);
    alert('Custom theme saved successfully!');
  };

  const handleResetToDefault = () => {
    if (confirm('Reset all customizations to default theme colors?')) {
      setCustomColors(themes[selectedThemeId].colors);
      setHasUnsavedChanges(false);
    }
  };

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      academic: 'Academic',
      modern: 'Modern',
      medical: 'Medical',
      nature: 'Nature',
      minimal: 'Minimal',
      humanities: 'Humanities',
      law: 'Law',
      technology: 'Technology',
      social: 'Social Sciences',
      business: 'Business',
      bold: 'Bold',
    };
    return labels[category] || category;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <PaintBrushIcon className="h-6 w-6 text-indigo-600" />
            <h2 className="text-xl font-semibold text-gray-900">Theme Customizer</h2>
          </div>
          {hasUnsavedChanges && (
            <span className="px-3 py-1 text-sm bg-yellow-100 text-yellow-800 rounded-full">
              Unsaved changes
            </span>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex -mb-px">
          <button
            onClick={() => setActiveTab('select')}
            className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'select'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <SwatchIcon className="h-5 w-5" />
              <span>Select Theme</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('customize')}
            className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'customize'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <PaintBrushIcon className="h-5 w-5" />
              <span>Customize Colors</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('preview')}
            className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'preview'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <EyeIcon className="h-5 w-5" />
              <span>Preview</span>
            </div>
          </button>
        </nav>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Select Theme Tab */}
        {activeTab === 'select' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600 mb-6">
              Choose from {Object.keys(themes).length} professionally designed themes. You can
              further customize colors in the next tab.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.values(themes).map((theme) => (
                <div
                  key={theme.id}
                  className={`relative border-2 rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${
                    selectedThemeId === theme.id
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleThemeSelect(theme.id)}
                >
                  {selectedThemeId === theme.id && (
                    <div className="absolute top-3 right-3">
                      <CheckCircleIcon className="h-6 w-6 text-indigo-600" />
                    </div>
                  )}

                  <div className="mb-3">
                    <h3 className="font-semibold text-gray-900">{theme.name}</h3>
                    <p className="text-xs text-gray-500 mt-1">{theme.description}</p>
                    <span className="inline-block mt-2 px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                      {getCategoryLabel(theme.category)}
                    </span>
                  </div>

                  {/* Color swatches */}
                  <div className="flex space-x-1">
                    {[50, 300, 500, 700, 900].map((shade) => (
                      <div
                        key={shade}
                        className="h-6 w-6 rounded border border-gray-200"
                        style={{ backgroundColor: theme.colors.primary[shade as keyof typeof theme.colors.primary] }}
                        title={`Primary ${shade}`}
                      />
                    ))}
                  </div>

                  {/* Typography preview */}
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p
                      className="text-xs text-gray-600"
                      style={{ fontFamily: theme.typography.fontFamily.sans.join(', ') }}
                    >
                      Sans: {theme.typography.fontFamily.sans[0]}
                    </p>
                    <p
                      className="text-xs text-gray-600"
                      style={{ fontFamily: theme.typography.fontFamily.serif.join(', ') }}
                    >
                      Serif: {theme.typography.fontFamily.serif[0]}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Customize Colors Tab */}
        {activeTab === 'customize' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Customize the color palette for the selected theme. Changes are applied in real-time.
              </p>
              <div className="flex space-x-2">
                <button
                  onClick={handleResetToDefault}
                  className="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 flex items-center space-x-2"
                >
                  <ArrowPathIcon className="h-4 w-4" />
                  <span>Reset</span>
                </button>
                <button
                  onClick={handleSaveCustomTheme}
                  disabled={!hasUnsavedChanges}
                  className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Save Custom Theme
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Primary Colors */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Primary Colors</h3>
                <div className="space-y-3">
                  {[50, 100, 200, 300, 400, 500, 600, 700, 800, 900].map((shade) => (
                    <ColorPicker
                      key={shade}
                      label={`${shade}`}
                      color={customColors.primary?.[shade as keyof typeof customColors.primary] || '#000000'}
                      onChange={(value) => handleColorChange(`primary.${shade}`, value)}
                    />
                  ))}
                </div>
              </div>

              {/* Gray Scale */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Gray Scale</h3>
                <div className="space-y-3">
                  {[50, 100, 200, 300, 400, 500, 600, 700, 800, 900].map((shade) => (
                    <ColorPicker
                      key={shade}
                      label={`${shade}`}
                      color={customColors.gray?.[shade as keyof typeof customColors.gray] || '#000000'}
                      onChange={(value) => handleColorChange(`gray.${shade}`, value)}
                    />
                  ))}
                </div>
              </div>

              {/* Semantic Colors */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Semantic Colors</h3>
                <div className="space-y-3">
                  <ColorPicker
                    label="Success"
                    color={customColors.success || '#000000'}
                    onChange={(value) => handleColorChange('success', value)}
                  />
                  <ColorPicker
                    label="Warning"
                    color={customColors.warning || '#000000'}
                    onChange={(value) => handleColorChange('warning', value)}
                  />
                  <ColorPicker
                    label="Error"
                    color={customColors.error || '#000000'}
                    onChange={(value) => handleColorChange('error', value)}
                  />
                  <ColorPicker
                    label="Info"
                    color={customColors.info || '#000000'}
                    onChange={(value) => handleColorChange('info', value)}
                  />
                </div>
              </div>

              {/* Surface Colors */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Surface & Text</h3>
                <div className="space-y-3">
                  <ColorPicker
                    label="Background"
                    color={customColors.background || '#FFFFFF'}
                    onChange={(value) => handleColorChange('background', value)}
                  />
                  <ColorPicker
                    label="Surface"
                    color={customColors.surface || '#F9FAFB'}
                    onChange={(value) => handleColorChange('surface', value)}
                  />
                  <ColorPicker
                    label="Text Primary"
                    color={customColors.text?.primary || '#111827'}
                    onChange={(value) => handleColorChange('text.primary', value)}
                  />
                  <ColorPicker
                    label="Text Secondary"
                    color={customColors.text?.secondary || '#6B7280'}
                    onChange={(value) => handleColorChange('text.secondary', value)}
                  />
                  <ColorPicker
                    label="Text Disabled"
                    color={customColors.text?.disabled || '#9CA3AF'}
                    onChange={(value) => handleColorChange('text.disabled', value)}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Preview Tab */}
        {activeTab === 'preview' && (
          <div className="space-y-6">
            <p className="text-sm text-gray-600 mb-6">
              Preview how your theme looks across different components. Toggle dark mode to see both variants.
            </p>

            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Component Preview</h3>
              <label className="flex items-center space-x-3 cursor-pointer">
                <span className="text-sm text-gray-700">Dark Mode</span>
                <div
                  className={`relative inline-block w-12 h-6 rounded-full transition-colors ${
                    isDarkMode ? 'bg-indigo-600' : 'bg-gray-300'
                  }`}
                  onClick={toggleDarkMode}
                >
                  <div
                    className={`absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                      isDarkMode ? 'transform translate-x-6' : ''
                    }`}
                  />
                </div>
              </label>
            </div>

            {/* Preview Components */}
            <div className="space-y-6">
              {/* Buttons */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-sm font-semibold text-gray-900 mb-4">Buttons</h4>
                <div className="flex flex-wrap gap-3">
                  <button
                    className="px-4 py-2 rounded-md text-white"
                    style={{ backgroundColor: customColors.primary?.[500] }}
                  >
                    Primary Button
                  </button>
                  <button
                    className="px-4 py-2 rounded-md text-white"
                    style={{ backgroundColor: customColors.success }}
                  >
                    Success Button
                  </button>
                  <button
                    className="px-4 py-2 rounded-md text-white"
                    style={{ backgroundColor: customColors.warning }}
                  >
                    Warning Button
                  </button>
                  <button
                    className="px-4 py-2 rounded-md text-white"
                    style={{ backgroundColor: customColors.error }}
                  >
                    Error Button
                  </button>
                  <button
                    className="px-4 py-2 rounded-md border-2"
                    style={{
                      borderColor: customColors.primary?.[500],
                      color: customColors.primary?.[500],
                    }}
                  >
                    Outline Button
                  </button>
                </div>
              </div>

              {/* Typography */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-sm font-semibold text-gray-900 mb-4">Typography</h4>
                <div className="space-y-3">
                  <h1
                    className="text-4xl font-bold"
                    style={{ color: customColors.text?.primary }}
                  >
                    Heading 1
                  </h1>
                  <h2
                    className="text-3xl font-semibold"
                    style={{ color: customColors.text?.primary }}
                  >
                    Heading 2
                  </h2>
                  <h3
                    className="text-2xl font-medium"
                    style={{ color: customColors.text?.primary }}
                  >
                    Heading 3
                  </h3>
                  <p style={{ color: customColors.text?.primary }}>
                    Primary body text. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                  </p>
                  <p style={{ color: customColors.text?.secondary }}>
                    Secondary body text. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                  </p>
                </div>
              </div>

              {/* Cards */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-sm font-semibold text-gray-900 mb-4">Cards</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div
                    className="rounded-lg p-4 border"
                    style={{
                      backgroundColor: customColors.surface,
                      borderColor: customColors.gray?.[200],
                    }}
                  >
                    <h5
                      className="font-semibold mb-2"
                      style={{ color: customColors.text?.primary }}
                    >
                      Article Card
                    </h5>
                    <p
                      className="text-sm"
                      style={{ color: customColors.text?.secondary }}
                    >
                      This is how article cards will look with your theme.
                    </p>
                    <button
                      className="mt-3 px-3 py-1 text-sm rounded"
                      style={{
                        backgroundColor: customColors.primary?.[500],
                        color: '#FFFFFF',
                      }}
                    >
                      Read More
                    </button>
                  </div>
                  <div
                    className="rounded-lg p-4 border"
                    style={{
                      backgroundColor: customColors.surface,
                      borderColor: customColors.gray?.[200],
                    }}
                  >
                    <h5
                      className="font-semibold mb-2"
                      style={{ color: customColors.text?.primary }}
                    >
                      Submission Card
                    </h5>
                    <p
                      className="text-sm"
                      style={{ color: customColors.text?.secondary }}
                    >
                      Preview of submission management cards.
                    </p>
                    <div className="mt-3 flex space-x-2">
                      <span
                        className="px-2 py-1 text-xs rounded"
                        style={{
                          backgroundColor: customColors.success,
                          color: '#FFFFFF',
                        }}
                      >
                        Accepted
                      </span>
                    </div>
                  </div>
                  <div
                    className="rounded-lg p-4 border"
                    style={{
                      backgroundColor: customColors.surface,
                      borderColor: customColors.gray?.[200],
                    }}
                  >
                    <h5
                      className="font-semibold mb-2"
                      style={{ color: customColors.text?.primary }}
                    >
                      Review Card
                    </h5>
                    <p
                      className="text-sm"
                      style={{ color: customColors.text?.secondary }}
                    >
                      How review cards appear to editors.
                    </p>
                    <div className="mt-3 flex space-x-2">
                      <span
                        className="px-2 py-1 text-xs rounded"
                        style={{
                          backgroundColor: customColors.warning,
                          color: '#FFFFFF',
                        }}
                      >
                        Pending
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Forms */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-sm font-semibold text-gray-900 mb-4">Form Elements</h4>
                <div className="space-y-4 max-w-md">
                  <div>
                    <label
                      className="block text-sm font-medium mb-1"
                      style={{ color: customColors.text?.primary }}
                    >
                      Input Field
                    </label>
                    <input
                      type="text"
                      placeholder="Enter text..."
                      className="w-full px-3 py-2 rounded-md border"
                      style={{ borderColor: customColors.gray?.[300] }}
                    />
                  </div>
                  <div>
                    <label
                      className="block text-sm font-medium mb-1"
                      style={{ color: customColors.text?.primary }}
                    >
                      Select Field
                    </label>
                    <select
                      className="w-full px-3 py-2 rounded-md border"
                      style={{ borderColor: customColors.gray?.[300] }}
                    >
                      <option>Option 1</option>
                      <option>Option 2</option>
                      <option>Option 3</option>
                    </select>
                  </div>
                  <div>
                    <label
                      className="block text-sm font-medium mb-1"
                      style={{ color: customColors.text?.primary }}
                    >
                      Textarea
                    </label>
                    <textarea
                      placeholder="Enter longer text..."
                      rows={3}
                      className="w-full px-3 py-2 rounded-md border"
                      style={{ borderColor: customColors.gray?.[300] }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ThemeCustomizer;
