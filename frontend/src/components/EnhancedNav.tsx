import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  MagnifyingGlassIcon,
  Bars3Icon,
  XMarkIcon,
  ChevronDownIcon,
  SunIcon,
  MoonIcon,
  SwatchIcon,
} from '@heroicons/react/24/outline';
import { useTheme } from '../context/ThemeContext';
import { getThemeOptions } from '../config/themes';

interface NavDropdownItem {
  name: string;
  href: string;
  description?: string;
}

interface NavItem {
  name: string;
  href?: string;
  dropdownItems?: NavDropdownItem[];
}

const EnhancedNav: React.FC = React.memo(() => {
  const location = useLocation();
  const { themeId, setTheme, toggleDarkMode, isDarkMode, currentTheme } = useTheme();
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [showThemeSelector, setShowThemeSelector] = useState(false);

  // Handle scroll effect for nav bar
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
    setActiveDropdown(null);
  }, [location.pathname]);

  // Memoize navigation array - doesn't change
  const navigation: NavItem[] = useMemo(() => [
    { name: 'Home', href: '/' },
    {
      name: 'Articles',
      dropdownItems: [
        { name: 'Browse All Articles', href: '/articles', description: 'Explore published research' },
        { name: 'Current Issue', href: '/issues/current', description: 'Latest publications' },
        { name: 'Archive', href: '/archive', description: 'Past issues' },
        { name: 'Search', href: '/search', description: 'Advanced search' },
      ],
    },
    {
      name: 'For Authors',
      dropdownItems: [
        { name: 'Submit Manuscript', href: '/dashboard/manuscripts/submit', description: 'Start submission' },
        { name: 'Author Guidelines', href: '/author-guidelines', description: 'Submission requirements' },
        { name: 'Submission Process', href: '/submission-process', description: 'Step-by-step guide' },
        { name: 'Publication Fees', href: '/fees', description: 'Diamond OA - Free!' },
      ],
    },
    {
      name: 'About',
      dropdownItems: [
        { name: 'About Us', href: '/about', description: 'Our mission and vision' },
        { name: 'Editorial Board', href: '/editorial-board', description: 'Meet our editors' },
        { name: 'Policies', href: '/policies', description: 'Editorial policies' },
        { name: 'Indexing', href: '/indexing', description: 'Where we are indexed' },
      ],
    },
    { name: 'Contact', href: '/contact' },
  ], []);

  // Memoize theme options - rarely changes
  const themeOptions = useMemo(() => getThemeOptions(), []);

  // Memoize callback functions
  const isCurrentPath = useCallback((href: string) => location.pathname === href, [location.pathname]);

  return (
    <>
      {/* Header with glassmorphism effect when scrolled */}
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled
            ? 'bg-white/90 backdrop-blur-md shadow-lg border-b border-gray-200'
            : 'bg-white border-b border-gray-100'
        }`}
      >
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center group">
              <div
                className="h-10 w-10 rounded-lg flex items-center justify-center transition-transform duration-200 group-hover:scale-105 shadow-md"
                style={{
                  background: `linear-gradient(135deg, ${currentTheme.colors.primary[500]}, ${currentTheme.colors.primary[700]})`,
                }}
              >
                <span className="text-xl font-bold text-white">J</span>
              </div>
              <span
                className="ml-3 text-xl font-bold transition-colors duration-200"
                style={{ color: currentTheme.colors.text.primary }}
              >
                Diamond OA Journal
              </span>
            </Link>

            {/* Desktop navigation */}
            <div className="hidden lg:flex items-center space-x-1">
              {navigation.map((item) =>
                item.dropdownItems ? (
                  <div
                    key={item.name}
                    className="relative"
                    onMouseEnter={() => setActiveDropdown(item.name)}
                    onMouseLeave={() => setActiveDropdown(null)}
                  >
                    <button
                      className={`px-4 py-2 rounded-md font-medium transition-all duration-200 flex items-center ${
                        activeDropdown === item.name
                          ? `bg-opacity-10`
                          : 'hover:bg-opacity-5'
                      }`}
                      style={{
                        color: activeDropdown === item.name
                          ? currentTheme.colors.primary[600]
                          : currentTheme.colors.text.secondary,
                        backgroundColor: activeDropdown === item.name
                          ? currentTheme.colors.primary[500] + '10'
                          : 'transparent',
                      }}
                    >
                      {item.name}
                      <ChevronDownIcon
                        className={`ml-1 h-4 w-4 transition-transform duration-200 ${
                          activeDropdown === item.name ? 'rotate-180' : ''
                        }`}
                      />
                    </button>

                    {/* Dropdown Menu */}
                    {activeDropdown === item.name && (
                      <div className="absolute left-0 mt-2 w-72 bg-white rounded-lg shadow-xl border border-gray-100 py-2 animate-fade-in">
                        {item.dropdownItems.map((dropdownItem) => (
                          <Link
                            key={dropdownItem.name}
                            to={dropdownItem.href}
                            className="block px-4 py-3 hover:bg-gray-50 transition-colors duration-150"
                          >
                            <div
                              className="font-medium text-sm"
                              style={{ color: currentTheme.colors.text.primary }}
                            >
                              {dropdownItem.name}
                            </div>
                            {dropdownItem.description && (
                              <div
                                className="text-xs mt-1"
                                style={{ color: currentTheme.colors.text.secondary }}
                              >
                                {dropdownItem.description}
                              </div>
                            )}
                          </Link>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <Link
                    key={item.name}
                    to={item.href!}
                    className={`px-4 py-2 rounded-md font-medium transition-all duration-200 ${
                      isCurrentPath(item.href!)
                        ? 'bg-opacity-10'
                        : 'hover:bg-opacity-5'
                    }`}
                    style={{
                      color: isCurrentPath(item.href!)
                        ? currentTheme.colors.primary[600]
                        : currentTheme.colors.text.secondary,
                      backgroundColor: isCurrentPath(item.href!)
                        ? currentTheme.colors.primary[500] + '10'
                        : 'transparent',
                    }}
                  >
                    {item.name}
                  </Link>
                )
              )}
            </div>

            {/* Right side actions */}
            <div className="flex items-center space-x-3">
              {/* Search button */}
              <button
                className="p-2 rounded-md transition-colors duration-200 hover:bg-gray-100"
                aria-label="Search"
              >
                <MagnifyingGlassIcon className="h-5 w-5" style={{ color: currentTheme.colors.text.secondary }} />
              </button>

              {/* Dark mode toggle */}
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-md transition-colors duration-200 hover:bg-gray-100"
                aria-label="Toggle dark mode"
              >
                {isDarkMode ? (
                  <SunIcon className="h-5 w-5" style={{ color: currentTheme.colors.text.secondary }} />
                ) : (
                  <MoonIcon className="h-5 w-5" style={{ color: currentTheme.colors.text.secondary }} />
                )}
              </button>

              {/* Theme selector */}
              <div className="relative hidden md:block">
                <button
                  onClick={() => setShowThemeSelector(!showThemeSelector)}
                  className="p-2 rounded-md transition-colors duration-200 hover:bg-gray-100"
                  aria-label="Change theme"
                >
                  <SwatchIcon className="h-5 w-5" style={{ color: currentTheme.colors.text.secondary }} />
                </button>

                {showThemeSelector && (
                  <>
                    <div
                      className="fixed inset-0 z-40"
                      onClick={() => setShowThemeSelector(false)}
                    />
                    <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-100 py-2 z-50 max-h-96 overflow-y-auto">
                      <div className="px-4 py-2 border-b border-gray-100">
                        <h3 className="font-semibold text-sm" style={{ color: currentTheme.colors.text.primary }}>
                          Choose Theme
                        </h3>
                        <p className="text-xs mt-1" style={{ color: currentTheme.colors.text.secondary }}>
                          {themeOptions.length} beautiful themes available
                        </p>
                      </div>
                      <div className="py-1">
                        {themeOptions.map((theme) => (
                          <button
                            key={theme.id}
                            onClick={() => {
                              setTheme(theme.id);
                              setShowThemeSelector(false);
                            }}
                            className={`w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors duration-150 ${
                              themeId === theme.id ? 'bg-gray-50' : ''
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <div>
                                <div
                                  className="font-medium text-sm"
                                  style={{ color: currentTheme.colors.text.primary }}
                                >
                                  {theme.name}
                                </div>
                                <div
                                  className="text-xs mt-1"
                                  style={{ color: currentTheme.colors.text.secondary }}
                                >
                                  {theme.description}
                                </div>
                              </div>
                              {themeId === theme.id && (
                                <div
                                  className="h-2 w-2 rounded-full"
                                  style={{ backgroundColor: currentTheme.colors.primary[500] }}
                                />
                              )}
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </div>

              {/* Sign in / Get Started */}
              <div className="hidden md:flex items-center space-x-3">
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-md font-medium transition-colors duration-200"
                  style={{ color: currentTheme.colors.text.secondary }}
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 rounded-md font-medium text-white transition-all duration-200 hover:shadow-lg"
                  style={{ backgroundColor: currentTheme.colors.primary[600] }}
                >
                  Get Started
                </Link>
              </div>

              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden p-2 rounded-md transition-colors duration-200 hover:bg-gray-100"
                aria-label="Toggle menu"
              >
                {mobileMenuOpen ? (
                  <XMarkIcon className="h-6 w-6" style={{ color: currentTheme.colors.text.secondary }} />
                ) : (
                  <Bars3Icon className="h-6 w-6" style={{ color: currentTheme.colors.text.secondary }} />
                )}
              </button>
            </div>
          </div>
        </nav>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-gray-200 bg-white shadow-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 space-y-2">
              {navigation.map((item) =>
                item.dropdownItems ? (
                  <div key={item.name}>
                    <button
                      onClick={() =>
                        setActiveDropdown(activeDropdown === item.name ? null : item.name)
                      }
                      className="w-full text-left px-3 py-2 rounded-md font-medium flex items-center justify-between"
                      style={{ color: currentTheme.colors.text.secondary }}
                    >
                      {item.name}
                      <ChevronDownIcon
                        className={`h-4 w-4 transition-transform duration-200 ${
                          activeDropdown === item.name ? 'rotate-180' : ''
                        }`}
                      />
                    </button>
                    {activeDropdown === item.name && (
                      <div className="pl-4 mt-1 space-y-1">
                        {item.dropdownItems.map((dropdownItem) => (
                          <Link
                            key={dropdownItem.name}
                            to={dropdownItem.href}
                            className="block px-3 py-2 rounded-md text-sm"
                            style={{ color: currentTheme.colors.text.secondary }}
                          >
                            {dropdownItem.name}
                          </Link>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <Link
                    key={item.name}
                    to={item.href!}
                    className="block px-3 py-2 rounded-md font-medium"
                    style={{
                      color: isCurrentPath(item.href!)
                        ? currentTheme.colors.primary[600]
                        : currentTheme.colors.text.secondary,
                      backgroundColor: isCurrentPath(item.href!)
                        ? currentTheme.colors.primary[500] + '10'
                        : 'transparent',
                    }}
                  >
                    {item.name}
                  </Link>
                )
              )}

              <div className="pt-4 border-t border-gray-200 flex items-center justify-between">
                <Link
                  to="/login"
                  className="flex-1 px-4 py-2 rounded-md font-medium text-center mr-2"
                  style={{ color: currentTheme.colors.text.secondary }}
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="flex-1 px-4 py-2 rounded-md font-medium text-white text-center"
                  style={{ backgroundColor: currentTheme.colors.primary[600] }}
                >
                  Get Started
                </Link>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Spacer to prevent content from going under fixed header */}
      <div className="h-16" />
    </>
  );
});

EnhancedNav.displayName = 'EnhancedNav';

export default EnhancedNav;
