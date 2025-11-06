import React, { useEffect, useRef } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface SidePanelProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  width?: 'narrow' | 'medium' | 'wide' | 'full';
  showHeader?: boolean;
  headerActions?: React.ReactNode;
  className?: string;
}

const SidePanel: React.FC<SidePanelProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  width = 'medium',
  showHeader = true,
  headerActions,
  className = '',
}) => {
  const panelRef = useRef<HTMLDivElement>(null);

  // Handle Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Prevent body scroll when panel is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  // Click outside to close
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
      onClose();
    }
  };

  const getWidthClass = () => {
    const widthClasses = {
      narrow: 'max-w-md',
      medium: 'max-w-2xl',
      wide: 'max-w-4xl',
      full: 'max-w-full',
    };
    return widthClasses[width] || widthClasses.medium;
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 overflow-hidden"
      aria-labelledby="side-panel-title"
      role="dialog"
      aria-modal="true"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50 transition-opacity duration-300 ease-in-out"
        onClick={handleBackdropClick}
        aria-hidden="true"
      />

      {/* Panel Container */}
      <div className="fixed inset-y-0 right-0 flex max-w-full">
        <div
          ref={panelRef}
          className={`w-screen ${getWidthClass()} transform transition-transform duration-300 ease-in-out ${className}`}
        >
          <div className="flex h-full flex-col bg-white shadow-xl">
            {/* Header */}
            {showHeader && (
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-4 border-b border-gray-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {title && (
                      <h2
                        id="side-panel-title"
                        className="text-xl font-bold text-gray-900"
                      >
                        {title}
                      </h2>
                    )}
                    {subtitle && (
                      <p className="mt-1 text-sm text-gray-600">{subtitle}</p>
                    )}
                  </div>

                  <div className="ml-4 flex items-center space-x-2">
                    {headerActions && <div className="mr-2">{headerActions}</div>}
                    <button
                      type="button"
                      className="rounded-lg p-2 text-gray-400 hover:text-gray-600 hover:bg-white transition-colors"
                      onClick={onClose}
                      aria-label="Close panel"
                    >
                      <XMarkIcon className="h-6 w-6" />
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Content */}
            <div className="flex-1 overflow-y-auto">
              <div className="relative">{children}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SidePanel;
