import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  DocumentTextIcon,
  UserGroupIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  Bars3Icon,
  XMarkIcon,
  BellIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';

interface NavItem {
  name: string;
  path: string;
  icon: React.ReactNode;
  badge?: number;
}

interface MobileNavProps {
  userRole?: 'admin' | 'editor' | 'author' | 'reviewer';
  userName?: string;
  notificationCount?: number;
}

const MobileNav: React.FC<MobileNavProps> = ({
  userRole = 'author',
  userName = 'User',
  notificationCount = 0,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const getNavItems = (): NavItem[] => {
    const commonItems: NavItem[] = [
      {
        name: 'Dashboard',
        path: '/dashboard',
        icon: <HomeIcon className="h-6 w-6" />,
      },
      {
        name: 'Manuscripts',
        path: '/manuscripts',
        icon: <DocumentTextIcon className="h-6 w-6" />,
      },
    ];

    if (userRole === 'admin' || userRole === 'editor') {
      return [
        ...commonItems,
        {
          name: 'Task Queue',
          path: '/task-queue',
          icon: <ChartBarIcon className="h-6 w-6" />,
        },
        {
          name: 'Users',
          path: '/users',
          icon: <UserGroupIcon className="h-6 w-6" />,
        },
        {
          name: 'Settings',
          path: '/settings',
          icon: <Cog6ToothIcon className="h-6 w-6" />,
        },
      ];
    }

    return commonItems;
  };

  const navItems = getNavItems();

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  };

  return (
    <>
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-40 bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center justify-between px-4 py-3">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="h-10 w-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-xl font-bold text-white">J</span>
            </div>
            <span className="text-lg font-bold text-gray-900">Journal</span>
          </Link>

          {/* Actions */}
          <div className="flex items-center space-x-3">
            {/* Notifications */}
            <button className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
              <BellIcon className="h-6 w-6" />
              {notificationCount > 0 && (
                <span className="absolute top-1 right-1 h-5 w-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                  {notificationCount > 9 ? '9+' : notificationCount}
                </span>
              )}
            </button>

            {/* Menu Toggle */}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              {isOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 z-30 bg-black bg-opacity-50"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Mobile Menu Drawer */}
      <div
        className={`lg:hidden fixed top-16 right-0 bottom-0 z-30 w-80 bg-white shadow-xl transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* User Info */}
        <div className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
              {userName
                .split(' ')
                .map((n) => n[0])
                .join('')
                .substring(0, 2)
                .toUpperCase()}
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-900">{userName}</p>
              <p className="text-xs text-gray-600 capitalize">{userRole}</p>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="py-4">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setIsOpen(false)}
              className={`flex items-center space-x-3 px-6 py-3 text-base font-medium transition-colors ${
                isActive(item.path)
                  ? 'bg-blue-50 text-blue-600 border-l-4 border-blue-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <span className={isActive(item.path) ? 'text-blue-600' : 'text-gray-400'}>
                {item.icon}
              </span>
              <span>{item.name}</span>
              {item.badge && (
                <span className="ml-auto bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                  {item.badge}
                </span>
              )}
            </Link>
          ))}
        </nav>

        {/* Profile & Logout */}
        <div className="absolute bottom-0 left-0 right-0 border-t border-gray-200 p-4 space-y-2">
          <Link
            to="/profile"
            onClick={() => setIsOpen(false)}
            className="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg"
          >
            <UserCircleIcon className="h-6 w-6 text-gray-400" />
            <span className="text-sm font-medium">My Profile</span>
          </Link>
          <button
            onClick={() => {
              setIsOpen(false);
              // Add logout logic here
              localStorage.removeItem('token');
              localStorage.removeItem('user');
              window.location.href = '/login';
            }}
            className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-red-50 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              />
            </svg>
            <span className="text-sm font-medium">Sign Out</span>
          </button>
        </div>
      </div>

      {/* Bottom Navigation Bar (Mobile) */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-gray-200 shadow-lg">
        <div className="grid grid-cols-4 gap-1">
          {navItems.slice(0, 4).map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center justify-center py-3 text-xs font-medium transition-colors ${
                isActive(item.path)
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <span className="mb-1">{item.icon}</span>
              <span className="truncate max-w-full px-1">{item.name}</span>
              {item.badge && (
                <span className="absolute top-1 right-2 h-4 w-4 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                  {item.badge > 9 ? '9+' : item.badge}
                </span>
              )}
            </Link>
          ))}
        </div>
      </div>

      {/* Spacer for fixed header and bottom nav */}
      <div className="lg:hidden h-16" /> {/* Top spacer */}
      <div className="lg:hidden h-16" /> {/* Bottom spacer */}
    </>
  );
};

export default MobileNav;
