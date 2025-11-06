import React from 'react';
import { Outlet } from 'react-router-dom';
import EnhancedNav from '../components/EnhancedNav';
import EnhancedFooter from '../components/EnhancedFooter';
import { useTheme } from '../context/ThemeContext';

const PublicLayout: React.FC = () => {
  const { currentTheme } = useTheme();

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: currentTheme.colors.background }}>
      {/* Enhanced Navigation */}
      <EnhancedNav />

      {/* Main content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Enhanced Footer */}
      <EnhancedFooter />
    </div>
  );
};

export default PublicLayout;
