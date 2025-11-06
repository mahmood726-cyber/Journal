/**
 * Mega Navigation Menu
 *
 * Modern navigation with:
 * - Mega dropdowns with categories
 * - Instant search
 * - User menu (personalized)
 * - Sticky header with smart hiding
 * - Mobile responsive with hamburger
 * - Breadcrumbs navigation
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  Search, Menu, X, ChevronDown, User, Bell, Settings,
  BookOpen, FileText, Users, TrendingUp, Calendar,
  Award, MessageSquare, Download, Info, Mail, LogOut,
  Home, ChevronRight
} from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

interface NavCategory {
  id: string;
  label: string;
  icon: React.ReactNode;
  items: NavItem[];
}

interface NavItem {
  label: string;
  href: string;
  description?: string;
  badge?: string;
}

interface MegaNavigationProps {
  journalName: string;
  journalLogo?: string;
  unreadNotifications?: number;
}

const MegaNavigation: React.FC<MegaNavigationProps> = ({
  journalName,
  journalLogo,
  unreadNotifications = 0
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isScrollingUp, setIsScrollingUp] = useState(true);
  const [prevScrollPos, setPrevScrollPos] = useState(0);
  const location = useLocation();
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Navigation categories
  const categories: NavCategory[] = [
    {
      id: 'browse',
      label: 'Browse',
      icon: <BookOpen className="w-5 h-5" />,
      items: [
        { label: 'Current Issue', href: '/issues/current', description: 'Latest published articles' },
        { label: 'All Issues', href: '/issues', description: 'Browse archive' },
        { label: 'Articles', href: '/articles', description: 'Search all articles' },
        { label: 'By Topic', href: '/topics', description: 'Browse by subject' },
        { label: 'Collections', href: '/collections', description: 'Curated article collections' },
        { label: 'Early View', href: '/early-view', description: 'Articles ahead of print', badge: 'New' },
      ]
    },
    {
      id: 'authors',
      label: 'For Authors',
      icon: <FileText className="w-5 h-5" />,
      items: [
        { label: 'Submit Manuscript', href: '/submit', description: 'One-click submission' },
        { label: 'Author Guidelines', href: '/guidelines', description: 'Preparation & formatting' },
        { label: 'Peer Review Process', href: '/peer-review', description: 'How review works' },
        { label: 'Article Processing', href: '/processing', description: 'After acceptance' },
        { label: 'Open Access Policy', href: '/open-access', description: 'Diamond OA model' },
        { label: 'Track Your Submission', href: '/dashboard/submissions', description: 'Check manuscript status' },
      ]
    },
    {
      id: 'reviewers',
      label: 'For Reviewers',
      icon: <Users className="w-5 h-5" />,
      items: [
        { label: 'Become a Reviewer', href: '/reviewers/join', description: 'Join our review panel' },
        { label: 'Reviewer Guidelines', href: '/reviewers/guidelines', description: 'Best practices' },
        { label: 'Review Dashboard', href: '/dashboard/reviews', description: 'Pending reviews' },
        { label: 'Reviewer Recognition', href: '/reviewers/recognition', description: 'Badges & certificates' },
      ]
    },
    {
      id: 'about',
      label: 'About',
      icon: <Info className="w-5 h-5" />,
      items: [
        { label: 'About the Journal', href: '/about', description: 'Mission & scope' },
        { label: 'Editorial Board', href: '/editorial-board', description: 'Meet our editors' },
        { label: 'Policies', href: '/policies', description: 'Editorial policies' },
        { label: 'Metrics & Impact', href: '/metrics', description: 'Journal statistics' },
        { label: 'Contact Us', href: '/contact', description: 'Get in touch' },
      ]
    },
  ];

  // Handle scroll for sticky header
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollPos = window.pageYOffset;
      const scrollingUp = prevScrollPos > currentScrollPos;

      setIsScrollingUp(scrollingUp || currentScrollPos < 10);
      setPrevScrollPos(currentScrollPos);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [prevScrollPos]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setActiveDropdown(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
    setActiveDropdown(null);
  }, [location]);

  const handleDropdownToggle = (categoryId: string) => {
    setActiveDropdown(activeDropdown === categoryId ? null : categoryId);
  };

  return (
    <>
      {/* Sticky Navigation */}
      <nav
        className={`
          fixed top-0 left-0 right-0 z-50 bg-white shadow-md
          transition-transform duration-300
          ${isScrollingUp ? 'translate-y-0' : '-translate-y-full'}
        `}
      >
        {/* Top Bar */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-2 px-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between text-sm">
            <div className="flex items-center space-x-4">
              <span>🔓 Diamond Open Access</span>
              <span className="hidden md:inline">•</span>
              <span className="hidden md:inline">Free to Read & Publish</span>
            </div>
            <div className="flex items-center space-x-4">
              <a href="/contact" className="hover:underline flex items-center">
                <Mail className="w-4 h-4 mr-1" />
                Contact
              </a>
              <a href="/alerts" className="hover:underline hidden md:inline">Subscribe to Alerts</a>
            </div>
          </div>
        </div>

        {/* Main Navigation */}
        <div className="border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex items-center justify-between h-16">
              {/* Logo */}
              <Link to="/" className="flex items-center space-x-3">
                {journalLogo ? (
                  <img src={journalLogo} alt={journalName} className="h-10 w-auto" />
                ) : (
                  <div className="h-10 w-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
                    <BookOpen className="w-6 h-6 text-white" />
                  </div>
                )}
                <span className="text-xl font-bold text-gray-900 hidden md:inline">
                  {journalName}
                </span>
              </Link>

              {/* Desktop Navigation */}
              <div className="hidden lg:flex items-center space-x-1" ref={dropdownRef}>
                {categories.map((category) => (
                  <div key={category.id} className="relative">
                    <button
                      onClick={() => handleDropdownToggle(category.id)}
                      className={`
                        flex items-center space-x-1 px-4 py-2 rounded-lg
                        transition-colors duration-200
                        ${activeDropdown === category.id
                          ? 'bg-indigo-50 text-indigo-600'
                          : 'text-gray-700 hover:bg-gray-100'
                        }
                      `}
                    >
                      {category.icon}
                      <span className="font-medium">{category.label}</span>
                      <ChevronDown className={`w-4 h-4 transition-transform ${activeDropdown === category.id ? 'rotate-180' : ''}`} />
                    </button>

                    {/* Mega Dropdown */}
                    {activeDropdown === category.id && (
                      <div className="absolute top-full left-0 mt-2 w-96 bg-white rounded-lg shadow-2xl border border-gray-200 py-4">
                        <div className="px-4 pb-2 mb-2 border-b border-gray-100">
                          <div className="flex items-center space-x-2 text-indigo-600">
                            {category.icon}
                            <h3 className="font-bold text-lg">{category.label}</h3>
                          </div>
                        </div>
                        <div className="space-y-1 px-2">
                          {category.items.map((item) => (
                            <Link
                              key={item.href}
                              to={item.href}
                              className="block px-3 py-2 rounded-md hover:bg-gray-50 transition-colors group"
                            >
                              <div className="flex items-center justify-between">
                                <div>
                                  <div className="font-medium text-gray-900 group-hover:text-indigo-600 flex items-center">
                                    {item.label}
                                    {item.badge && (
                                      <span className="ml-2 px-2 py-0.5 bg-indigo-100 text-indigo-600 text-xs font-semibold rounded-full">
                                        {item.badge}
                                      </span>
                                    )}
                                  </div>
                                  {item.description && (
                                    <p className="text-sm text-gray-500 mt-0.5">
                                      {item.description}
                                    </p>
                                  )}
                                </div>
                                <ChevronRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                              </div>
                            </Link>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Right Actions */}
              <div className="flex items-center space-x-2">
                {/* Search */}
                <button
                  onClick={() => setIsSearchOpen(!isSearchOpen)}
                  className="p-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
                  aria-label="Search"
                >
                  <Search className="w-5 h-5" />
                </button>

                {/* Notifications */}
                <Link
                  to="/notifications"
                  className="p-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors relative"
                  aria-label="Notifications"
                >
                  <Bell className="w-5 h-5" />
                  {unreadNotifications > 0 && (
                    <span className="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                      {unreadNotifications > 9 ? '9+' : unreadNotifications}
                    </span>
                  )}
                </Link>

                {/* User Menu */}
                <UserMenu />

                {/* Mobile Menu Toggle */}
                <button
                  onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                  className="lg:hidden p-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
                  aria-label="Menu"
                >
                  {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Search Bar (Expanded) */}
        {isSearchOpen && (
          <div className="border-b border-gray-200 bg-gray-50 py-4 px-4">
            <div className="max-w-7xl mx-auto">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search articles, authors, topics..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  autoFocus
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
              {searchQuery && <InstantSearchResults query={searchQuery} />}
            </div>
          </div>
        )}
      </nav>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsMobileMenuOpen(false)} />
          <div className="fixed top-0 right-0 bottom-0 w-80 bg-white shadow-xl overflow-y-auto">
            <div className="p-4">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Menu</h2>
                <button
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="p-2 rounded-lg text-gray-700 hover:bg-gray-100"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Mobile Categories */}
              {categories.map((category) => (
                <div key={category.id} className="mb-4">
                  <button
                    onClick={() => handleDropdownToggle(category.id)}
                    className="w-full flex items-center justify-between px-4 py-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      {category.icon}
                      <span className="font-medium text-gray-900">{category.label}</span>
                    </div>
                    <ChevronDown className={`w-5 h-5 transition-transform ${activeDropdown === category.id ? 'rotate-180' : ''}`} />
                  </button>

                  {activeDropdown === category.id && (
                    <div className="mt-2 space-y-1 pl-4">
                      {category.items.map((item) => (
                        <Link
                          key={item.href}
                          to={item.href}
                          className="block px-4 py-2 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          <div className="font-medium">{item.label}</div>
                          {item.description && (
                            <div className="text-sm text-gray-500">{item.description}</div>
                          )}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Spacer to prevent content jump */}
      <div className="h-28" />
    </>
  );
};

/**
 * User Menu Dropdown
 */
const UserMenu: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 p-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
      >
        <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </div>
        <ChevronDown className={`w-4 h-4 hidden md:inline transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-64 bg-white rounded-lg shadow-2xl border border-gray-200 py-2">
          {/* User Info */}
          <div className="px-4 py-3 border-b border-gray-100">
            <div className="font-medium text-gray-900">Dr. John Smith</div>
            <div className="text-sm text-gray-500">john.smith@university.edu</div>
          </div>

          {/* Menu Items */}
          <div className="py-2">
            <Link
              to="/dashboard"
              className="flex items-center space-x-3 px-4 py-2 text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Home className="w-5 h-5" />
              <span>Dashboard</span>
            </Link>
            <Link
              to="/dashboard/submissions"
              className="flex items-center space-x-3 px-4 py-2 text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <FileText className="w-5 h-5" />
              <span>My Submissions</span>
            </Link>
            <Link
              to="/dashboard/reviews"
              className="flex items-center space-x-3 px-4 py-2 text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Users className="w-5 h-5" />
              <span>My Reviews</span>
            </Link>
            <Link
              to="/settings"
              className="flex items-center space-x-3 px-4 py-2 text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Settings className="w-5 h-5" />
              <span>Settings</span>
            </Link>
          </div>

          {/* Logout */}
          <div className="border-t border-gray-100 pt-2">
            <button className="flex items-center space-x-3 px-4 py-2 text-red-600 hover:bg-red-50 transition-colors w-full">
              <LogOut className="w-5 h-5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Instant Search Results
 */
const InstantSearchResults: React.FC<{ query: string }> = ({ query }) => {
  // Mock results - replace with actual search API
  const results = [
    {
      type: 'article',
      title: 'Novel Approaches to Cancer Treatment Using CRISPR',
      authors: 'Smith J, Doe J',
      journal: 'Vol 10, Issue 2 (2024)',
    },
    {
      type: 'article',
      title: 'Machine Learning in Genomic Research',
      authors: 'Johnson R, Williams M',
      journal: 'Vol 10, Issue 1 (2024)',
    },
  ];

  return (
    <div className="mt-4 bg-white rounded-lg shadow-lg border border-gray-200 max-h-96 overflow-y-auto">
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 mb-3">
          Search Results for "{query}"
        </h3>
        <div className="space-y-3">
          {results.map((result, idx) => (
            <div
              key={idx}
              className="p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <h4 className="font-medium text-gray-900 mb-1">{result.title}</h4>
              <p className="text-sm text-gray-600">{result.authors}</p>
              <p className="text-xs text-gray-500 mt-1">{result.journal}</p>
            </div>
          ))}
        </div>
        <div className="mt-4 pt-4 border-t border-gray-200">
          <Link
            to={`/search?q=${encodeURIComponent(query)}`}
            className="text-indigo-600 hover:text-indigo-800 font-medium text-sm flex items-center"
          >
            View all results
            <ChevronRight className="w-4 h-4 ml-1" />
          </Link>
        </div>
      </div>
    </div>
  );
};

/**
 * Breadcrumbs Navigation
 */
export const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const pathSegments = location.pathname.split('/').filter(Boolean);

  if (pathSegments.length === 0) return null;

  return (
    <div className="bg-gray-50 border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <nav className="flex items-center space-x-2 text-sm">
          <Link
            to="/"
            className="text-gray-600 hover:text-indigo-600 transition-colors flex items-center"
          >
            <Home className="w-4 h-4 mr-1" />
            Home
          </Link>
          {pathSegments.map((segment, idx) => {
            const path = `/${pathSegments.slice(0, idx + 1).join('/')}`;
            const isLast = idx === pathSegments.length - 1;
            const label = segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');

            return (
              <React.Fragment key={path}>
                <ChevronRight className="w-4 h-4 text-gray-400" />
                {isLast ? (
                  <span className="text-gray-900 font-medium">{label}</span>
                ) : (
                  <Link
                    to={path}
                    className="text-gray-600 hover:text-indigo-600 transition-colors"
                  >
                    {label}
                  </Link>
                )}
              </React.Fragment>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

export default MegaNavigation;
