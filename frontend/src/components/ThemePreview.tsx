/**
 * ThemePreview Component
 *
 * Shows a live preview of a theme with sample content.
 * Features:
 * - Full page preview with header, sidebar, content
 * - Sample article layout
 * - Interactive elements (buttons, forms, cards)
 * - Responsive preview modes (desktop, tablet, mobile)
 * - Dark mode toggle
 */

import React, { useState, useEffect } from 'react';
import { Theme, applyTheme } from '../themes/themeLibrary';

interface ThemePreviewProps {
  theme: Theme;
  useDarkMode?: boolean;
  viewportMode?: 'desktop' | 'tablet' | 'mobile';
  showControls?: boolean;
}

export const ThemePreview: React.FC<ThemePreviewProps> = ({
  theme,
  useDarkMode = false,
  viewportMode = 'desktop',
  showControls = true,
}) => {
  const [previewDarkMode, setPreviewDarkMode] = useState(useDarkMode);
  const [previewViewport, setPreviewViewport] = useState(viewportMode);

  useEffect(() => {
    setPreviewDarkMode(useDarkMode);
  }, [useDarkMode]);

  useEffect(() => {
    setPreviewViewport(viewportMode);
  }, [viewportMode]);

  const getViewportClass = () => {
    switch (previewViewport) {
      case 'mobile':
        return 'viewport-mobile';
      case 'tablet':
        return 'viewport-tablet';
      default:
        return 'viewport-desktop';
    }
  };

  const colors = previewDarkMode && theme.darkMode ? theme.darkMode : theme.colors;

  return (
    <div className="theme-preview-container">
      {showControls && (
        <div className="preview-controls">
          <div className="control-group">
            <label>Viewport:</label>
            <div className="viewport-buttons">
              <button
                className={previewViewport === 'desktop' ? 'active' : ''}
                onClick={() => setPreviewViewport('desktop')}
                title="Desktop"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <rect x="2" y="3" width="20" height="14" rx="2" strokeWidth="2" />
                  <line x1="8" y1="21" x2="16" y2="21" strokeWidth="2" />
                  <line x1="12" y1="17" x2="12" y2="21" strokeWidth="2" />
                </svg>
              </button>
              <button
                className={previewViewport === 'tablet' ? 'active' : ''}
                onClick={() => setPreviewViewport('tablet')}
                title="Tablet"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <rect x="5" y="2" width="14" height="20" rx="2" strokeWidth="2" />
                  <line x1="12" y1="18" x2="12.01" y2="18" strokeWidth="2" />
                </svg>
              </button>
              <button
                className={previewViewport === 'mobile' ? 'active' : ''}
                onClick={() => setPreviewViewport('mobile')}
                title="Mobile"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <rect x="7" y="2" width="10" height="20" rx="2" strokeWidth="2" />
                  <line x1="12" y1="18" x2="12.01" y2="18" strokeWidth="2" />
                </svg>
              </button>
            </div>
          </div>
          {theme.darkMode && (
            <div className="control-group">
              <label>
                <input
                  type="checkbox"
                  checked={previewDarkMode}
                  onChange={(e) => setPreviewDarkMode(e.target.checked)}
                />
                Dark Mode
              </label>
            </div>
          )}
        </div>
      )}

      <div className={`preview-wrapper ${getViewportClass()}`}>
        <div className="preview-frame" style={{ backgroundColor: colors.background }}>
          {/* Header */}
          <header
            className="preview-header"
            style={{
              backgroundColor: colors.primary,
              color: colors.textOnPrimary,
              height: theme.layout.headerHeight,
            }}
          >
            <div className="header-content">
              <div
                className="logo"
                style={{ fontFamily: theme.typography.fontFamily.heading }}
              >
                Journal Name
              </div>
              <nav className="nav">
                <a href="#" style={{ color: colors.textOnPrimary }}>
                  Home
                </a>
                <a href="#" style={{ color: colors.textOnPrimary }}>
                  Articles
                </a>
                <a href="#" style={{ color: colors.textOnPrimary }}>
                  About
                </a>
              </nav>
            </div>
          </header>

          {/* Main Content */}
          <div className="preview-main">
            {/* Sidebar */}
            <aside
              className="preview-sidebar"
              style={{
                backgroundColor: colors.backgroundPaper,
                borderRight: `1px solid ${colors.border}`,
                width: theme.layout.sidebarWidth,
              }}
            >
              <div className="sidebar-section">
                <h3
                  style={{
                    color: colors.textPrimary,
                    fontFamily: theme.typography.fontFamily.heading,
                  }}
                >
                  Categories
                </h3>
                <ul className="sidebar-list">
                  {['Research', 'Reviews', 'Case Studies', 'Editorials'].map((item) => (
                    <li
                      key={item}
                      style={{
                        color: colors.textSecondary,
                        fontFamily: theme.typography.fontFamily.body,
                      }}
                    >
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="sidebar-section">
                <h3
                  style={{
                    color: colors.textPrimary,
                    fontFamily: theme.typography.fontFamily.heading,
                  }}
                >
                  Quick Links
                </h3>
                <button
                  className="sidebar-button"
                  style={{
                    backgroundColor: colors.accent,
                    color: colors.textOnPrimary,
                    borderRadius: theme.layout.borderRadius.sm,
                  }}
                >
                  Submit Article
                </button>
              </div>
            </aside>

            {/* Content */}
            <main className="preview-content" style={{ maxWidth: theme.layout.maxWidth }}>
              {/* Article Card */}
              <article
                className="article-card"
                style={{
                  backgroundColor: colors.backgroundPaper,
                  borderRadius: theme.layout.borderRadius.md,
                  border: `1px solid ${colors.border}`,
                }}
              >
                <div className="article-header">
                  <span
                    className="article-badge"
                    style={{
                      backgroundColor: colors.info,
                      color: '#fff',
                      borderRadius: theme.layout.borderRadius.sm,
                    }}
                  >
                    Research Article
                  </span>
                  <h1
                    className="article-title"
                    style={{
                      color: colors.textPrimary,
                      fontFamily: theme.typography.fontFamily.heading,
                      fontSize: theme.typography.fontSize.h1,
                      fontWeight: theme.typography.fontWeight.bold,
                    }}
                  >
                    Sample Article Title: A Comprehensive Study
                  </h1>
                  <p
                    className="article-meta"
                    style={{
                      color: colors.textSecondary,
                      fontFamily: theme.typography.fontFamily.body,
                      fontSize: theme.typography.fontSize.sm,
                    }}
                  >
                    John Doe, Jane Smith • Published March 15, 2024
                  </p>
                </div>

                <div className="article-body">
                  <p
                    style={{
                      color: colors.textPrimary,
                      fontFamily: theme.typography.fontFamily.body,
                      fontSize: theme.typography.fontSize.base,
                      lineHeight: theme.typography.lineHeight.relaxed,
                    }}
                  >
                    This is a sample paragraph to demonstrate the theme's typography and color
                    scheme. The text should be easily readable with appropriate contrast and
                    spacing. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                  </p>

                  <div
                    className="article-highlight"
                    style={{
                      backgroundColor: colors.background,
                      borderLeft: `4px solid ${colors.primary}`,
                      borderRadius: theme.layout.borderRadius.sm,
                      padding: theme.layout.spacing.lg,
                    }}
                  >
                    <p
                      style={{
                        color: colors.textPrimary,
                        fontFamily: theme.typography.fontFamily.body,
                        fontSize: theme.typography.fontSize.base,
                        margin: 0,
                      }}
                    >
                      This is a highlighted section demonstrating accent colors and borders.
                    </p>
                  </div>

                  <div className="article-actions">
                    <button
                      className="action-button primary"
                      style={{
                        backgroundColor: colors.primary,
                        color: colors.textOnPrimary,
                        borderRadius: theme.layout.borderRadius.sm,
                        fontFamily: theme.typography.fontFamily.body,
                        fontWeight: theme.typography.fontWeight.semibold,
                      }}
                    >
                      Download PDF
                    </button>
                    <button
                      className="action-button secondary"
                      style={{
                        backgroundColor: 'transparent',
                        color: colors.primary,
                        border: `1px solid ${colors.primary}`,
                        borderRadius: theme.layout.borderRadius.sm,
                        fontFamily: theme.typography.fontFamily.body,
                        fontWeight: theme.typography.fontWeight.semibold,
                      }}
                    >
                      Cite Article
                    </button>
                  </div>
                </div>
              </article>

              {/* Stats Grid */}
              <div className="stats-grid">
                {[
                  { label: 'Views', value: '1,234', color: colors.info },
                  { label: 'Downloads', value: '567', color: colors.success },
                  { label: 'Citations', value: '89', color: colors.warning },
                ].map((stat) => (
                  <div
                    key={stat.label}
                    className="stat-card"
                    style={{
                      backgroundColor: colors.backgroundPaper,
                      borderRadius: theme.layout.borderRadius.md,
                      border: `1px solid ${colors.border}`,
                    }}
                  >
                    <div className="stat-value" style={{ color: stat.color }}>
                      {stat.value}
                    </div>
                    <div
                      className="stat-label"
                      style={{
                        color: colors.textSecondary,
                        fontFamily: theme.typography.fontFamily.body,
                      }}
                    >
                      {stat.label}
                    </div>
                  </div>
                ))}
              </div>
            </main>
          </div>
        </div>
      </div>

      <style jsx>{`
        .theme-preview-container {
          width: 100%;
        }

        .preview-controls {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background: var(--background-paper, #fff);
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 8px 8px 0 0;
          border-bottom: none;
        }

        .control-group {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .control-group label {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-primary, #1a1a1a);
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .viewport-buttons {
          display: flex;
          gap: 0.5rem;
        }

        .viewport-buttons button {
          padding: 0.5rem;
          background: transparent;
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 4px;
          cursor: pointer;
          color: var(--text-secondary, #666);
          transition: all 0.2s;
        }

        .viewport-buttons button:hover {
          background: var(--background-hover, #f5f5f5);
          border-color: var(--primary-color, #1976d2);
          color: var(--primary-color, #1976d2);
        }

        .viewport-buttons button.active {
          background: var(--primary-color, #1976d2);
          border-color: var(--primary-color, #1976d2);
          color: white;
        }

        .preview-wrapper {
          border: 1px solid var(--border-color, #e0e0e0);
          border-radius: 0 0 8px 8px;
          overflow: hidden;
          transition: all 0.3s;
        }

        .viewport-desktop {
          width: 100%;
        }

        .viewport-tablet {
          width: 768px;
          margin: 0 auto;
        }

        .viewport-mobile {
          width: 375px;
          margin: 0 auto;
        }

        .preview-frame {
          width: 100%;
          min-height: 600px;
          overflow-y: auto;
        }

        .preview-header {
          position: sticky;
          top: 0;
          z-index: 10;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0 2rem;
          height: 100%;
          max-width: 1400px;
          margin: 0 auto;
        }

        .logo {
          font-size: 1.5rem;
          font-weight: 700;
        }

        .nav {
          display: flex;
          gap: 2rem;
        }

        .nav a {
          text-decoration: none;
          font-weight: 500;
          transition: opacity 0.2s;
        }

        .nav a:hover {
          opacity: 0.8;
        }

        .preview-main {
          display: flex;
          min-height: calc(100vh - 80px);
        }

        .preview-sidebar {
          flex-shrink: 0;
          padding: 2rem 1.5rem;
        }

        .sidebar-section {
          margin-bottom: 2rem;
        }

        .sidebar-section h3 {
          font-size: 1rem;
          font-weight: 700;
          margin: 0 0 1rem 0;
        }

        .sidebar-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .sidebar-list li {
          padding: 0.5rem 0;
          font-size: 0.875rem;
          cursor: pointer;
          transition: opacity 0.2s;
        }

        .sidebar-list li:hover {
          opacity: 0.7;
        }

        .sidebar-button {
          width: 100%;
          padding: 0.75rem 1rem;
          border: none;
          font-weight: 600;
          cursor: pointer;
          transition: opacity 0.2s;
        }

        .sidebar-button:hover {
          opacity: 0.9;
        }

        .preview-content {
          flex: 1;
          padding: 2rem;
          margin: 0 auto;
          width: 100%;
        }

        .article-card {
          padding: 2rem;
          margin-bottom: 2rem;
        }

        .article-header {
          margin-bottom: 2rem;
        }

        .article-badge {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 1rem;
        }

        .article-title {
          margin: 0.5rem 0;
          line-height: 1.3;
        }

        .article-meta {
          margin: 0.5rem 0;
        }

        .article-body {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .article-highlight {
          margin: 1rem 0;
        }

        .article-actions {
          display: flex;
          gap: 1rem;
          margin-top: 1rem;
        }

        .action-button {
          padding: 0.75rem 1.5rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .action-button:hover {
          opacity: 0.9;
          transform: translateY(-1px);
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 1rem;
        }

        .stat-card {
          padding: 1.5rem;
          text-align: center;
        }

        .stat-value {
          font-size: 2rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
        }

        .stat-label {
          font-size: 0.875rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        @media (max-width: 768px) {
          .preview-sidebar {
            display: none;
          }

          .stats-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default ThemePreview;
