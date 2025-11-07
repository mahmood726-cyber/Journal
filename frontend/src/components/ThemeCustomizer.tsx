/**
 * ThemeCustomizer Component
 *
 * Visual editor for customizing theme properties.
 * Features:
 * - Color picker for all theme colors
 * - Typography controls (fonts, sizes, weights)
 * - Layout controls (spacing, borders)
 * - Live preview of changes
 * - Export/import custom themes
 * - Reset to default theme
 */

import React, { useState, useEffect } from 'react';
import { Theme, ThemeColors, ThemeTypography, ThemeLayout } from '../themes/themeLibrary';

interface ThemeCustomizerProps {
  theme: Theme;
  onChange: (updatedTheme: Theme) => void;
  onReset?: () => void;
  onExport?: (theme: Theme) => void;
  onImport?: () => void;
}

type CustomizerTab = 'colors' | 'typography' | 'layout';

export const ThemeCustomizer: React.FC<ThemeCustomizerProps> = ({
  theme,
  onChange,
  onReset,
  onExport,
  onImport,
}) => {
  const [activeTab, setActiveTab] = useState<CustomizerTab>('colors');
  const [customTheme, setCustomTheme] = useState<Theme>(theme);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    setCustomTheme(theme);
    setHasChanges(false);
  }, [theme]);

  const handleColorChange = (colorKey: keyof ThemeColors, value: string) => {
    const updatedTheme = {
      ...customTheme,
      colors: {
        ...customTheme.colors,
        [colorKey]: value,
      },
    };
    setCustomTheme(updatedTheme);
    setHasChanges(true);
    onChange(updatedTheme);
  };

  const handleTypographyChange = (
    section: keyof ThemeTypography,
    key: string,
    value: string | number
  ) => {
    const updatedTheme = {
      ...customTheme,
      typography: {
        ...customTheme.typography,
        [section]:
          typeof customTheme.typography[section] === 'object'
            ? {
                ...(customTheme.typography[section] as any),
                [key]: value,
              }
            : value,
      },
    };
    setCustomTheme(updatedTheme);
    setHasChanges(true);
    onChange(updatedTheme);
  };

  const handleLayoutChange = (key: keyof ThemeLayout, value: string) => {
    const updatedTheme = {
      ...customTheme,
      layout: {
        ...customTheme.layout,
        [key]: value,
      },
    };
    setCustomTheme(updatedTheme);
    setHasChanges(true);
    onChange(updatedTheme);
  };

  const handleReset = () => {
    if (onReset) {
      onReset();
      setHasChanges(false);
    }
  };

  const handleExport = () => {
    if (onExport) {
      onExport(customTheme);
    } else {
      // Default export as JSON
      const dataStr = JSON.stringify(customTheme, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
      const exportFileDefaultName = `${customTheme.id}-custom.json`;

      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    }
  };

  return (
    <div className="theme-customizer">
      <div className="customizer-header">
        <h3>Customize Theme</h3>
        <div className="header-actions">
          {hasChanges && (
            <span className="changes-indicator">Unsaved changes</span>
          )}
          <button onClick={handleExport} className="btn-secondary" title="Export theme">
            Export
          </button>
          {onImport && (
            <button onClick={onImport} className="btn-secondary" title="Import theme">
              Import
            </button>
          )}
          {onReset && (
            <button onClick={handleReset} className="btn-secondary" title="Reset to original">
              Reset
            </button>
          )}
        </div>
      </div>

      <div className="customizer-tabs">
        <button
          className={`tab ${activeTab === 'colors' ? 'active' : ''}`}
          onClick={() => setActiveTab('colors')}
        >
          Colors
        </button>
        <button
          className={`tab ${activeTab === 'typography' ? 'active' : ''}`}
          onClick={() => setActiveTab('typography')}
        >
          Typography
        </button>
        <button
          className={`tab ${activeTab === 'layout' ? 'active' : ''}`}
          onClick={() => setActiveTab('layout')}
        >
          Layout
        </button>
      </div>

      <div className="customizer-content">
        {activeTab === 'colors' && (
          <ColorsPanel colors={customTheme.colors} onChange={handleColorChange} />
        )}
        {activeTab === 'typography' && (
          <TypographyPanel
            typography={customTheme.typography}
            onChange={handleTypographyChange}
          />
        )}
        {activeTab === 'layout' && (
          <LayoutPanel layout={customTheme.layout} onChange={handleLayoutChange} />
        )}
      </div>

      <style jsx>{`
        .theme-customizer {
          background: var(--background-paper, #fff);
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 8px;
          overflow: hidden;
        }

        .customizer-header {
          padding: 1.5rem;
          border-bottom: 1px solid var(--border-color, #e0e0e0);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .customizer-header h3 {
          font-size: 1.25rem;
          font-weight: 700;
          margin: 0;
          color: var(--text-primary, #1a1a1a);
        }

        .header-actions {
          display: flex;
          gap: 0.75rem;
          align-items: center;
        }

        .changes-indicator {
          font-size: 0.875rem;
          color: var(--warning-color, #ff9800);
          font-weight: 600;
        }

        .btn-secondary {
          padding: 0.5rem 1rem;
          background: transparent;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 4px;
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-primary, #1a1a1a);
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-secondary:hover {
          background: var(--background-hover, #f5f5f5);
          border-color: var(--primary-color, #1976d2);
        }

        .customizer-tabs {
          display: flex;
          border-bottom: 1px solid var(--border-color, #e0e0e0);
          background: var(--background, #fafafa);
        }

        .tab {
          flex: 1;
          padding: 1rem;
          background: transparent;
          border: none;
          border-bottom: 2px solid transparent;
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-secondary, #666);
          cursor: pointer;
          transition: all 0.2s;
        }

        .tab:hover {
          background: var(--background-hover, #f5f5f5);
          color: var(--text-primary, #1a1a1a);
        }

        .tab.active {
          background: var(--background-paper, #fff);
          border-bottom-color: var(--primary-color, #1976d2);
          color: var(--primary-color, #1976d2);
        }

        .customizer-content {
          padding: 1.5rem;
          max-height: 600px;
          overflow-y: auto;
        }

        @media (max-width: 768px) {
          .customizer-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
          }

          .header-actions {
            width: 100%;
            justify-content: flex-end;
          }
        }
      `}</style>
    </div>
  );
};

// Colors Panel Component
interface ColorsPanelProps {
  colors: ThemeColors;
  onChange: (colorKey: keyof ThemeColors, value: string) => void;
}

const ColorsPanel: React.FC<ColorsPanelProps> = ({ colors, onChange }) => {
  const colorGroups = [
    {
      title: 'Primary Colors',
      colors: [
        { key: 'primary' as keyof ThemeColors, label: 'Primary' },
        { key: 'primaryDark' as keyof ThemeColors, label: 'Primary Dark' },
        { key: 'primaryLight' as keyof ThemeColors, label: 'Primary Light' },
      ],
    },
    {
      title: 'Secondary Colors',
      colors: [
        { key: 'secondary' as keyof ThemeColors, label: 'Secondary' },
        { key: 'accent' as keyof ThemeColors, label: 'Accent' },
      ],
    },
    {
      title: 'Background Colors',
      colors: [
        { key: 'background' as keyof ThemeColors, label: 'Background' },
        { key: 'backgroundPaper' as keyof ThemeColors, label: 'Paper' },
      ],
    },
    {
      title: 'Text Colors',
      colors: [
        { key: 'textPrimary' as keyof ThemeColors, label: 'Text Primary' },
        { key: 'textSecondary' as keyof ThemeColors, label: 'Text Secondary' },
        { key: 'textOnPrimary' as keyof ThemeColors, label: 'Text on Primary' },
      ],
    },
    {
      title: 'Semantic Colors',
      colors: [
        { key: 'success' as keyof ThemeColors, label: 'Success' },
        { key: 'warning' as keyof ThemeColors, label: 'Warning' },
        { key: 'error' as keyof ThemeColors, label: 'Error' },
        { key: 'info' as keyof ThemeColors, label: 'Info' },
      ],
    },
    {
      title: 'UI Colors',
      colors: [
        { key: 'border' as keyof ThemeColors, label: 'Border' },
        { key: 'divider' as keyof ThemeColors, label: 'Divider' },
      ],
    },
  ];

  return (
    <div className="colors-panel">
      {colorGroups.map((group) => (
        <div key={group.title} className="color-group">
          <h4 className="group-title">{group.title}</h4>
          <div className="color-controls">
            {group.colors.map(({ key, label }) => (
              <div key={key} className="color-control">
                <label htmlFor={`color-${key}`}>{label}</label>
                <div className="color-input-wrapper">
                  <input
                    id={`color-${key}`}
                    type="color"
                    value={colors[key]}
                    onChange={(e) => onChange(key, e.target.value)}
                    className="color-picker"
                  />
                  <input
                    type="text"
                    value={colors[key]}
                    onChange={(e) => onChange(key, e.target.value)}
                    className="color-text"
                    placeholder="#000000"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      <style jsx>{`
        .colors-panel {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .color-group {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .group-title {
          font-size: 1rem;
          font-weight: 700;
          color: var(--text-primary, #1a1a1a);
          margin: 0;
        }

        .color-controls {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
        }

        .color-control {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .color-control label {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-secondary, #666);
        }

        .color-input-wrapper {
          display: flex;
          gap: 0.5rem;
          align-items: center;
        }

        .color-picker {
          width: 48px;
          height: 48px;
          border: 2px solid var(--border-color, #e0e0e0);
          border-radius: 4px;
          cursor: pointer;
        }

        .color-text {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 4px;
          font-size: 0.875rem;
          font-family: monospace;
          color: var(--text-primary, #1a1a1a);
        }

        .color-text:focus {
          outline: none;
          border-color: var(--primary-color, #1976d2);
        }
      `}</style>
    </div>
  );
};

// Typography Panel Component
interface TypographyPanelProps {
  typography: ThemeTypography;
  onChange: (section: keyof ThemeTypography, key: string, value: string | number) => void;
}

const TypographyPanel: React.FC<TypographyPanelProps> = ({ typography, onChange }) => {
  const fontFamilies = [
    { value: '"Inter", sans-serif', label: 'Inter' },
    { value: '"Roboto", sans-serif', label: 'Roboto' },
    { value: '"Open Sans", sans-serif', label: 'Open Sans' },
    { value: '"Lato", sans-serif', label: 'Lato' },
    { value: '"Merriweather", serif', label: 'Merriweather' },
    { value: '"Georgia", serif', label: 'Georgia' },
    { value: '"Playfair Display", serif', label: 'Playfair Display' },
    { value: '"Source Sans Pro", sans-serif', label: 'Source Sans Pro' },
    { value: '"Montserrat", sans-serif', label: 'Montserrat' },
  ];

  return (
    <div className="typography-panel">
      <div className="typography-section">
        <h4 className="section-title">Font Families</h4>
        <div className="font-controls">
          <div className="control-group">
            <label>Heading Font</label>
            <select
              value={typography.fontFamily.heading}
              onChange={(e) => onChange('fontFamily', 'heading', e.target.value)}
              className="select-input"
            >
              {fontFamilies.map((font) => (
                <option key={font.value} value={font.value}>
                  {font.label}
                </option>
              ))}
            </select>
          </div>
          <div className="control-group">
            <label>Body Font</label>
            <select
              value={typography.fontFamily.body}
              onChange={(e) => onChange('fontFamily', 'body', e.target.value)}
              className="select-input"
            >
              {fontFamilies.map((font) => (
                <option key={font.value} value={font.value}>
                  {font.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="typography-section">
        <h4 className="section-title">Font Sizes (rem)</h4>
        <div className="size-controls">
          {Object.entries(typography.fontSize).map(([key, value]) => (
            <div key={key} className="control-group">
              <label>{key}</label>
              <input
                type="number"
                value={parseFloat(value)}
                onChange={(e) => onChange('fontSize', key, `${e.target.value}rem`)}
                step="0.125"
                min="0.5"
                max="4"
                className="number-input"
              />
            </div>
          ))}
        </div>
      </div>

      <div className="typography-section">
        <h4 className="section-title">Font Weights</h4>
        <div className="weight-controls">
          {Object.entries(typography.fontWeight).map(([key, value]) => (
            <div key={key} className="control-group">
              <label>{key}</label>
              <select
                value={value}
                onChange={(e) => onChange('fontWeight', key, parseInt(e.target.value))}
                className="select-input"
              >
                <option value="300">Light (300)</option>
                <option value="400">Regular (400)</option>
                <option value="500">Medium (500)</option>
                <option value="600">Semibold (600)</option>
                <option value="700">Bold (700)</option>
                <option value="800">Extrabold (800)</option>
              </select>
            </div>
          ))}
        </div>
      </div>

      <style jsx>{`
        .typography-panel {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .typography-section {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .section-title {
          font-size: 1rem;
          font-weight: 700;
          color: var(--text-primary, #1a1a1a);
          margin: 0;
        }

        .font-controls,
        .size-controls,
        .weight-controls {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
        }

        .control-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .control-group label {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-secondary, #666);
          text-transform: capitalize;
        }

        .select-input,
        .number-input {
          padding: 0.75rem;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 4px;
          font-size: 0.875rem;
          color: var(--text-primary, #1a1a1a);
          background: var(--background, #fff);
        }

        .select-input:focus,
        .number-input:focus {
          outline: none;
          border-color: var(--primary-color, #1976d2);
        }
      `}</style>
    </div>
  );
};

// Layout Panel Component
interface LayoutPanelProps {
  layout: ThemeLayout;
  onChange: (key: keyof ThemeLayout, value: string) => void;
}

const LayoutPanel: React.FC<LayoutPanelProps> = ({ layout, onChange }) => {
  return (
    <div className="layout-panel">
      <div className="layout-section">
        <h4 className="section-title">Dimensions</h4>
        <div className="layout-controls">
          <div className="control-group">
            <label>Max Width</label>
            <input
              type="text"
              value={layout.maxWidth}
              onChange={(e) => onChange('maxWidth', e.target.value)}
              placeholder="1200px"
              className="text-input"
            />
          </div>
          <div className="control-group">
            <label>Sidebar Width</label>
            <input
              type="text"
              value={layout.sidebarWidth}
              onChange={(e) => onChange('sidebarWidth', e.target.value)}
              placeholder="280px"
              className="text-input"
            />
          </div>
          <div className="control-group">
            <label>Header Height</label>
            <input
              type="text"
              value={layout.headerHeight}
              onChange={(e) => onChange('headerHeight', e.target.value)}
              placeholder="80px"
              className="text-input"
            />
          </div>
        </div>
      </div>

      <div className="layout-section">
        <h4 className="section-title">Spacing Scale (rem)</h4>
        <div className="spacing-controls">
          {Object.entries(layout.spacing).map(([key, value]) => (
            <div key={key} className="control-group">
              <label>Spacing {key}</label>
              <input
                type="number"
                value={parseFloat(value)}
                onChange={(e) =>
                  onChange(
                    'spacing',
                    JSON.stringify({
                      ...layout.spacing,
                      [key]: `${e.target.value}rem`,
                    })
                  )
                }
                step="0.25"
                min="0"
                max="8"
                className="number-input"
              />
            </div>
          ))}
        </div>
      </div>

      <div className="layout-section">
        <h4 className="section-title">Border Radius (px)</h4>
        <div className="radius-controls">
          {Object.entries(layout.borderRadius).map(([key, value]) => (
            <div key={key} className="control-group">
              <label>Radius {key}</label>
              <input
                type="number"
                value={parseInt(value)}
                onChange={(e) =>
                  onChange(
                    'borderRadius',
                    JSON.stringify({
                      ...layout.borderRadius,
                      [key]: `${e.target.value}px`,
                    })
                  )
                }
                step="2"
                min="0"
                max="32"
                className="number-input"
              />
            </div>
          ))}
        </div>
      </div>

      <style jsx>{`
        .layout-panel {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .layout-section {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .section-title {
          font-size: 1rem;
          font-weight: 700;
          color: var(--text-primary, #1a1a1a);
          margin: 0;
        }

        .layout-controls,
        .spacing-controls,
        .radius-controls {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
        }

        .control-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .control-group label {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-secondary, #666);
        }

        .text-input,
        .number-input {
          padding: 0.75rem;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 4px;
          font-size: 0.875rem;
          color: var(--text-primary, #1a1a1a);
          background: var(--background, #fff);
        }

        .text-input:focus,
        .number-input:focus {
          outline: none;
          border-color: var(--primary-color, #1976d2);
        }
      `}</style>
    </div>
  );
};

export default ThemeCustomizer;
