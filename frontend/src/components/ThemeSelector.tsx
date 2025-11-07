/**
 * ThemeSelector Component
 *
 * Allows users to browse, preview, and select themes from the theme library.
 * Features:
 * - Grid layout with theme preview cards
 * - Filter by category and style
 * - Live preview on hover
 * - Apply theme with one click
 */

import React, { useState, useMemo } from 'react';
import {
  Theme,
  ThemeCategory,
  ThemeStyle,
  themesByCategory,
  themesByStyle,
  applyTheme,
} from '../themes/themeLibrary';

interface ThemeSelectorProps {
  currentThemeId?: string;
  onThemeSelect: (theme: Theme) => void;
  showFilters?: boolean;
}

export const ThemeSelector: React.FC<ThemeSelectorProps> = ({
  currentThemeId,
  onThemeSelect,
  showFilters = true,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<ThemeCategory | 'all'>('all');
  const [selectedStyle, setSelectedStyle] = useState<ThemeStyle | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [previewTheme, setPreviewTheme] = useState<Theme | null>(null);

  // Get all themes
  const allThemes = useMemo(() => {
    const themes: Theme[] = [];
    Object.values(themesByCategory).forEach((categoryThemes) => {
      themes.push(...categoryThemes);
    });
    return themes;
  }, []);

  // Filter themes based on selected filters
  const filteredThemes = useMemo(() => {
    let themes = allThemes;

    // Filter by category
    if (selectedCategory !== 'all') {
      themes = themes.filter((theme) => theme.category === selectedCategory);
    }

    // Filter by style
    if (selectedStyle !== 'all') {
      themes = themes.filter((theme) => theme.style === selectedStyle);
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      themes = themes.filter(
        (theme) =>
          theme.name.toLowerCase().includes(query) ||
          theme.description.toLowerCase().includes(query)
      );
    }

    return themes;
  }, [allThemes, selectedCategory, selectedStyle, searchQuery]);

  const handleThemeSelect = (theme: Theme) => {
    onThemeSelect(theme);
    applyTheme(theme);
  };

  const handleThemeHover = (theme: Theme) => {
    setPreviewTheme(theme);
  };

  const handleThemeLeave = () => {
    setPreviewTheme(null);
  };

  return (
    <div className="theme-selector">
      <div className="theme-selector-header">
        <h2>Choose a Theme</h2>
        <p className="subtitle">
          Select from {allThemes.length} professionally designed themes inspired by leading
          academic journals
        </p>
      </div>

      {showFilters && (
        <div className="theme-filters">
          <div className="filter-group">
            <label htmlFor="search">Search</label>
            <input
              id="search"
              type="text"
              placeholder="Search themes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="filter-group">
            <label htmlFor="category">Category</label>
            <select
              id="category"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value as ThemeCategory | 'all')}
              className="filter-select"
            >
              <option value="all">All Categories</option>
              <option value="medical">Medical</option>
              <option value="scientific">Scientific</option>
              <option value="humanities">Humanities</option>
              <option value="technical">Technical</option>
              <option value="general">General</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="style">Style</label>
            <select
              id="style"
              value={selectedStyle}
              onChange={(e) => setSelectedStyle(e.target.value as ThemeStyle | 'all')}
              className="filter-select"
            >
              <option value="all">All Styles</option>
              <option value="modern">Modern</option>
              <option value="classic">Classic</option>
              <option value="minimal">Minimal</option>
              <option value="bold">Bold</option>
              <option value="academic">Academic</option>
            </select>
          </div>
        </div>
      )}

      <div className="theme-grid">
        {filteredThemes.map((theme) => (
          <ThemeCard
            key={theme.id}
            theme={theme}
            isSelected={theme.id === currentThemeId}
            onSelect={() => handleThemeSelect(theme)}
            onHover={() => handleThemeHover(theme)}
            onLeave={handleThemeLeave}
          />
        ))}
      </div>

      {filteredThemes.length === 0 && (
        <div className="no-results">
          <p>No themes found matching your criteria.</p>
          <button
            onClick={() => {
              setSearchQuery('');
              setSelectedCategory('all');
              setSelectedStyle('all');
            }}
            className="reset-filters-btn"
          >
            Reset Filters
          </button>
        </div>
      )}

      {previewTheme && (
        <div className="theme-preview-overlay">
          <div className="theme-preview-content">
            <h3>{previewTheme.name}</h3>
            <p>{previewTheme.description}</p>
            <div className="preview-colors">
              <div
                className="color-swatch"
                style={{ backgroundColor: previewTheme.colors.primary }}
                title="Primary"
              />
              <div
                className="color-swatch"
                style={{ backgroundColor: previewTheme.colors.secondary }}
                title="Secondary"
              />
              <div
                className="color-swatch"
                style={{ backgroundColor: previewTheme.colors.accent }}
                title="Accent"
              />
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .theme-selector {
          max-width: 1400px;
          margin: 0 auto;
          padding: 2rem;
        }

        .theme-selector-header {
          margin-bottom: 2rem;
          text-align: center;
        }

        .theme-selector-header h2 {
          font-size: 2rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
          color: var(--text-primary, #1a1a1a);
        }

        .subtitle {
          font-size: 1rem;
          color: var(--text-secondary, #666);
        }

        .theme-filters {
          display: grid;
          grid-template-columns: 2fr 1fr 1fr;
          gap: 1rem;
          margin-bottom: 2rem;
          padding: 1.5rem;
          background: var(--background-paper, #fff);
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .filter-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .filter-group label {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-primary, #1a1a1a);
        }

        .search-input,
        .filter-select {
          padding: 0.75rem;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 4px;
          font-size: 0.875rem;
          background: var(--background, #fff);
          color: var(--text-primary, #1a1a1a);
          transition: border-color 0.2s;
        }

        .search-input:focus,
        .filter-select:focus {
          outline: none;
          border-color: var(--primary-color, #1976d2);
        }

        .theme-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .no-results {
          text-align: center;
          padding: 4rem 2rem;
          color: var(--text-secondary, #666);
        }

        .reset-filters-btn {
          margin-top: 1rem;
          padding: 0.75rem 1.5rem;
          background: var(--primary-color, #1976d2);
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.875rem;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
        }

        .reset-filters-btn:hover {
          background: var(--primary-dark, #115293);
        }

        .theme-preview-overlay {
          position: fixed;
          bottom: 2rem;
          right: 2rem;
          background: var(--background-paper, #fff);
          padding: 1.5rem;
          border-radius: 8px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
          max-width: 300px;
          z-index: 1000;
        }

        .theme-preview-content h3 {
          font-size: 1.125rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
          color: var(--text-primary, #1a1a1a);
        }

        .theme-preview-content p {
          font-size: 0.875rem;
          color: var(--text-secondary, #666);
          margin-bottom: 1rem;
        }

        .preview-colors {
          display: flex;
          gap: 0.5rem;
        }

        .color-swatch {
          width: 40px;
          height: 40px;
          border-radius: 4px;
          border: 2px solid rgba(0, 0, 0, 0.1);
          cursor: help;
        }

        @media (max-width: 768px) {
          .theme-filters {
            grid-template-columns: 1fr;
          }

          .theme-grid {
            grid-template-columns: 1fr;
          }

          .theme-preview-overlay {
            bottom: 1rem;
            right: 1rem;
            left: 1rem;
            max-width: none;
          }
        }
      `}</style>
    </div>
  );
};

interface ThemeCardProps {
  theme: Theme;
  isSelected: boolean;
  onSelect: () => void;
  onHover: () => void;
  onLeave: () => void;
}

const ThemeCard: React.FC<ThemeCardProps> = ({
  theme,
  isSelected,
  onSelect,
  onHover,
  onLeave,
}) => {
  return (
    <div
      className={`theme-card ${isSelected ? 'selected' : ''}`}
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
      onClick={onSelect}
    >
      <div className="theme-card-preview" style={{ backgroundColor: theme.colors.background }}>
        <div className="preview-header" style={{ backgroundColor: theme.colors.primary }}>
          <div className="preview-logo" style={{ color: theme.colors.textOnPrimary }}>
            Journal
          </div>
        </div>
        <div className="preview-content" style={{ padding: '1rem' }}>
          <div
            className="preview-title"
            style={{
              color: theme.colors.textPrimary,
              fontFamily: theme.typography.fontFamily.heading,
            }}
          >
            Article Title
          </div>
          <div
            className="preview-text"
            style={{
              color: theme.colors.textSecondary,
              fontFamily: theme.typography.fontFamily.body,
            }}
          >
            Sample article text preview
          </div>
          <div
            className="preview-button"
            style={{
              backgroundColor: theme.colors.accent,
              color: theme.colors.textOnPrimary,
            }}
          >
            Read More
          </div>
        </div>
      </div>

      <div className="theme-card-info">
        <h3 className="theme-name">{theme.name}</h3>
        <p className="theme-description">{theme.description}</p>
        <div className="theme-meta">
          <span className="badge category-badge">{theme.category}</span>
          <span className="badge style-badge">{theme.style}</span>
        </div>
      </div>

      {isSelected && (
        <div className="selected-indicator">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="12" fill="currentColor" />
            <path
              d="M7 12l3 3 7-7"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      )}

      <style jsx>{`
        .theme-card {
          background: var(--background-paper, #fff);
          border: 2px solid var(--border-color, #e0e0e0);
          border-radius: 8px;
          overflow: hidden;
          cursor: pointer;
          transition: all 0.3s;
          position: relative;
        }

        .theme-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
          border-color: var(--primary-color, #1976d2);
        }

        .theme-card.selected {
          border-color: var(--primary-color, #1976d2);
          box-shadow: 0 4px 16px rgba(25, 118, 210, 0.2);
        }

        .theme-card-preview {
          height: 200px;
          overflow: hidden;
        }

        .preview-header {
          height: 50px;
          display: flex;
          align-items: center;
          padding: 0 1rem;
        }

        .preview-logo {
          font-weight: 700;
          font-size: 1.125rem;
        }

        .preview-title {
          font-size: 1rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
          line-height: 1.4;
        }

        .preview-text {
          font-size: 0.875rem;
          line-height: 1.5;
          margin-bottom: 0.75rem;
        }

        .preview-button {
          display: inline-block;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          font-size: 0.875rem;
          font-weight: 600;
        }

        .theme-card-info {
          padding: 1.25rem;
        }

        .theme-name {
          font-size: 1.125rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
          color: var(--text-primary, #1a1a1a);
        }

        .theme-description {
          font-size: 0.875rem;
          color: var(--text-secondary, #666);
          line-height: 1.5;
          margin-bottom: 0.75rem;
        }

        .theme-meta {
          display: flex;
          gap: 0.5rem;
        }

        .badge {
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: capitalize;
        }

        .category-badge {
          background: rgba(25, 118, 210, 0.1);
          color: var(--primary-color, #1976d2);
        }

        .style-badge {
          background: rgba(0, 0, 0, 0.05);
          color: var(--text-secondary, #666);
        }

        .selected-indicator {
          position: absolute;
          top: 1rem;
          right: 1rem;
          color: var(--primary-color, #1976d2);
          background: white;
          border-radius: 50%;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }
      `}</style>
    </div>
  );
};

export default ThemeSelector;
