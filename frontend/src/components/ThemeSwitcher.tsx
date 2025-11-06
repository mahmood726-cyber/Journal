import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { themes } from '../config/themes';
import {
  SwatchIcon,
  CheckIcon,
  SunIcon,
  MoonIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

const ThemeSwitcher: React.FC = () => {
  const { themeId, setTheme, isDarkMode, toggleDarkMode } = useTheme();
  const [isOpen, setIsOpen] = useState(false);

  const handleThemeSelect = (newThemeId: string) => {
    setTheme(newThemeId);
    setIsOpen(false);
  };

  return (
    <>
      {/* Theme Switcher Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 p-4 bg-white dark:bg-gray-800 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 border-2 border-gray-200 dark:border-gray-700"
        title="Change Theme"
      >
        <SwatchIcon className="h-6 w-6 text-gray-700 dark:text-gray-200" />
      </button>

      {/* Theme Picker Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Choose Your Theme
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Select a theme that matches your journal's style
                </p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors duration-200"
              >
                <XMarkIcon className="h-6 w-6 text-gray-500 dark:text-gray-400" />
              </button>
            </div>

            {/* Dark Mode Toggle */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                    Dark Mode
                  </h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    Reduce eye strain in low-light environments
                  </p>
                </div>
                <button
                  onClick={toggleDarkMode}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 ${
                    isDarkMode ? 'bg-indigo-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${
                      isDarkMode ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  >
                    {isDarkMode ? (
                      <MoonIcon className="h-4 w-4 text-indigo-600" />
                    ) : (
                      <SunIcon className="h-4 w-4 text-gray-400" />
                    )}
                  </span>
                </button>
              </div>
            </div>

            {/* Theme Grid */}
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.values(themes).map((theme) => (
                  <button
                    key={theme.id}
                    onClick={() => handleThemeSelect(theme.id)}
                    className={`relative p-4 rounded-lg border-2 transition-all duration-200 text-left ${
                      themeId === theme.id
                        ? 'border-indigo-500 ring-2 ring-indigo-200'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    {/* Selected Indicator */}
                    {themeId === theme.id && (
                      <div className="absolute top-2 right-2 bg-indigo-500 rounded-full p-1">
                        <CheckIcon className="h-4 w-4 text-white" />
                      </div>
                    )}

                    {/* Theme Preview */}
                    <div className="mb-3">
                      <div className="flex space-x-1 mb-2">
                        {/* Color swatches */}
                        <div
                          className="w-8 h-8 rounded"
                          style={{ backgroundColor: theme.colors.primary[500] }}
                        />
                        <div
                          className="w-8 h-8 rounded"
                          style={{ backgroundColor: theme.colors.primary[300] }}
                        />
                        <div
                          className="w-8 h-8 rounded"
                          style={{ backgroundColor: theme.colors.gray[600] }}
                        />
                      </div>
                    </div>

                    {/* Theme Info */}
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                        {theme.name}
                      </h3>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {theme.description}
                      </p>
                      <div className="mt-2">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 capitalize">
                          {theme.category}
                        </span>
                      </div>
                    </div>

                    {/* Hover Effect */}
                    <div className="absolute inset-0 rounded-lg transition-opacity duration-200 opacity-0 hover:opacity-100 bg-gradient-to-t from-black/5 to-transparent pointer-events-none" />
                  </button>
                ))}
              </div>
            </div>

            {/* Footer */}
            <div className="p-6 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Changes are saved automatically and apply across your journal
                </p>
                <button
                  onClick={() => setIsOpen(false)}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors duration-200"
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ThemeSwitcher;
