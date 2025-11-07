/**
 * Theme Management Page
 *
 * Admin page for managing journal themes.
 * Features:
 * - Browse and select from 12 professional themes
 * - Customize colors, typography, and layout
 * - Live preview of changes
 * - Export/import custom themes
 * - Dark mode support
 */

import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import ThemeSelector from '../../components/ThemeSelector';
import ThemeCustomizer from '../../components/ThemeCustomizer';
import ThemePreview from '../../components/ThemePreview';
import { Theme } from '../../themes/themeLibrary';

type ManagementView = 'selector' | 'customizer' | 'preview';

export const ThemeManagement: React.FC = () => {
  const {
    currentTheme,
    isDarkMode,
    customTheme,
    setTheme,
    toggleDarkMode,
    updateTheme,
    resetTheme,
    exportTheme,
    importTheme,
  } = useTheme();

  const [activeView, setActiveView] = useState<ManagementView>('selector');
  const [previewTheme, setPreviewTheme] = useState<Theme>(currentTheme);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);

  const handleThemeSelect = (theme: Theme) => {
    setTheme(theme);
    setPreviewTheme(theme);
    showSuccess();
  };

  const handleThemeUpdate = (updatedTheme: Theme) => {
    updateTheme(updatedTheme);
    setPreviewTheme(updatedTheme);
  };

  const handleReset = () => {
    resetTheme();
    setPreviewTheme(currentTheme);
    showSuccess();
  };

  const handleExport = (theme: Theme) => {
    const themeJson = JSON.stringify(theme, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(themeJson);
    const exportFileDefaultName = `${theme.id}-custom.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();

    showSuccess();
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';

    input.onchange = (e: any) => {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const themeJson = event.target?.result as string;
          if (importTheme(themeJson)) {
            showSuccess();
          } else {
            alert('Failed to import theme. Please check the file format.');
          }
        } catch (error) {
          alert('Failed to import theme. Invalid JSON file.');
        }
      };
      reader.readAsText(file);
    };

    input.click();
  };

  const showSuccess = () => {
    setShowSuccessMessage(true);
    setTimeout(() => setShowSuccessMessage(false), 3000);
  };

  return (
    <div className="theme-management">
      <div className="management-header">
        <div>
          <h1>Theme Management</h1>
          <p className="subtitle">
            Customize your journal's appearance with professional themes
            {customTheme && <span className="custom-badge">Custom Theme Active</span>}
          </p>
        </div>

        <div className="header-actions">
          <label className="dark-mode-toggle">
            <input type="checkbox" checked={isDarkMode} onChange={toggleDarkMode} />
            <span>Dark Mode</span>
          </label>
        </div>
      </div>

      {showSuccessMessage && (
        <div className="success-message">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              d="M22 11.08V12a10 10 0 1 1-5.93-9.14"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <polyline points="22 4 12 14.01 9 11.01" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Theme saved successfully!
        </div>
      )}

      <div className="management-tabs">
        <button
          className={`tab ${activeView === 'selector' ? 'active' : ''}`}
          onClick={() => setActiveView('selector')}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="3" y="3" width="7" height="7" strokeWidth="2" />
            <rect x="14" y="3" width="7" height="7" strokeWidth="2" />
            <rect x="3" y="14" width="7" height="7" strokeWidth="2" />
            <rect x="14" y="14" width="7" height="7" strokeWidth="2" />
          </svg>
          Browse Themes
        </button>
        <button
          className={`tab ${activeView === 'customizer' ? 'active' : ''}`}
          onClick={() => setActiveView('customizer')}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="3" strokeWidth="2" />
            <path
              d="M12 1v6m0 6v6M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M5.64 18.36l4.24-4.24m4.24-4.24l4.24-4.24"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
          Customize
        </button>
        <button
          className={`tab ${activeView === 'preview' ? 'active' : ''}`}
          onClick={() => setActiveView('preview')}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" strokeWidth="2" />
            <circle cx="12" cy="12" r="3" strokeWidth="2" />
          </svg>
          Preview
        </button>
      </div>

      <div className="management-content">
        {activeView === 'selector' && (
          <div className="view-container">
            <ThemeSelector
              currentThemeId={currentTheme.id}
              onThemeSelect={handleThemeSelect}
              showFilters={true}
            />
          </div>
        )}

        {activeView === 'customizer' && (
          <div className="view-container">
            <div className="customizer-layout">
              <div className="customizer-panel">
                <ThemeCustomizer
                  theme={previewTheme}
                  onChange={handleThemeUpdate}
                  onReset={handleReset}
                  onExport={handleExport}
                  onImport={handleImport}
                />
              </div>
              <div className="preview-panel">
                <h3>Live Preview</h3>
                <ThemePreview
                  theme={previewTheme}
                  useDarkMode={isDarkMode}
                  showControls={true}
                />
              </div>
            </div>
          </div>
        )}

        {activeView === 'preview' && (
          <div className="view-container preview-full">
            <ThemePreview
              theme={previewTheme}
              useDarkMode={isDarkMode}
              showControls={true}
            />
          </div>
        )}
      </div>

      <style jsx>{`
        .theme-management {
          max-width: 1600px;
          margin: 0 auto;
          padding: 2rem;
        }

        .management-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 2rem;
          padding-bottom: 2rem;
          border-bottom: 2px solid var(--border-color, #e0e0e0);
        }

        .management-header h1 {
          font-size: 2.5rem;
          font-weight: 700;
          margin: 0 0 0.5rem 0;
          color: var(--text-primary, #1a1a1a);
        }

        .subtitle {
          font-size: 1rem;
          color: var(--text-secondary, #666);
          margin: 0;
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .custom-badge {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          background: var(--warning-color, #ff9800);
          color: white;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
        }

        .header-actions {
          display: flex;
          gap: 1rem;
          align-items: center;
        }

        .dark-mode-toggle {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          background: var(--background-paper, #fff);
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .dark-mode-toggle:hover {
          background: var(--background-hover, #f5f5f5);
          border-color: var(--primary-color, #1976d2);
        }

        .dark-mode-toggle input {
          cursor: pointer;
        }

        .dark-mode-toggle span {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-primary, #1a1a1a);
        }

        .success-message {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem 1.5rem;
          background: var(--success-color, #4caf50);
          color: white;
          border-radius: 8px;
          margin-bottom: 2rem;
          font-weight: 600;
          animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
          from {
            transform: translateY(-20px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        .management-tabs {
          display: flex;
          gap: 1rem;
          margin-bottom: 2rem;
          background: var(--background-paper, #fff);
          padding: 0.5rem;
          border-radius: 8px;
          border: 1px solid var(--border-color, #e0e0e0);
        }

        .tab {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
          padding: 1rem;
          background: transparent;
          border: none;
          border-radius: 6px;
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
          background: var(--primary-color, #1976d2);
          color: white;
        }

        .management-content {
          min-height: 600px;
        }

        .view-container {
          background: var(--background-paper, #fff);
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 8px;
          padding: 2rem;
        }

        .view-container.preview-full {
          padding: 0;
          overflow: hidden;
        }

        .customizer-layout {
          display: grid;
          grid-template-columns: 400px 1fr;
          gap: 2rem;
        }

        .customizer-panel h3,
        .preview-panel h3 {
          font-size: 1.25rem;
          font-weight: 700;
          margin: 0 0 1.5rem 0;
          color: var(--text-primary, #1a1a1a);
        }

        .preview-panel {
          position: sticky;
          top: 2rem;
          height: fit-content;
        }

        @media (max-width: 1200px) {
          .customizer-layout {
            grid-template-columns: 1fr;
          }

          .preview-panel {
            position: static;
          }
        }

        @media (max-width: 768px) {
          .theme-management {
            padding: 1rem;
          }

          .management-header {
            flex-direction: column;
            gap: 1rem;
          }

          .management-tabs {
            flex-direction: column;
          }

          .tab {
            justify-content: flex-start;
          }

          .view-container {
            padding: 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default ThemeManagement;
