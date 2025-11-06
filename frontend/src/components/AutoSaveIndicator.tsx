/**
 * Auto-Save Status Indicator Component
 *
 * Visual indicator showing save status and last save time.
 */
import React from 'react';
import { Cloud, CloudOff, Check, AlertCircle } from 'lucide-react';
import { SaveStatus } from '../hooks/useAutoSave';

interface AutoSaveIndicatorProps {
  status: SaveStatus;
  lastSaved: Date | null;
  error: string | null;
  onRetry?: () => void;
}

const AutoSaveIndicator: React.FC<AutoSaveIndicatorProps> = ({
  status,
  lastSaved,
  error,
  onRetry,
}) => {
  const formatLastSaved = (date: Date | null): string => {
    if (!date) return 'Never';

    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);

    if (diffSec < 10) return 'Just now';
    if (diffSec < 60) return `${diffSec} seconds ago`;
    if (diffMin === 1) return '1 minute ago';
    if (diffMin < 60) return `${diffMin} minutes ago`;

    return date.toLocaleTimeString();
  };

  const getStatusDisplay = () => {
    switch (status) {
      case 'saving':
        return {
          icon: <Cloud className="w-4 h-4 animate-pulse" />,
          text: 'Saving...',
          className: 'text-blue-600',
        };
      case 'saved':
        return {
          icon: <Check className="w-4 h-4" />,
          text: 'Saved',
          className: 'text-green-600',
        };
      case 'error':
        return {
          icon: <AlertCircle className="w-4 h-4" />,
          text: 'Save failed',
          className: 'text-red-600',
        };
      default:
        return {
          icon: <CloudOff className="w-4 h-4" />,
          text: 'Not saved',
          className: 'text-gray-400',
        };
    }
  };

  const statusDisplay = getStatusDisplay();

  return (
    <div className="flex items-center space-x-2 text-sm">
      <div className={`flex items-center space-x-1 ${statusDisplay.className}`}>
        {statusDisplay.icon}
        <span>{statusDisplay.text}</span>
      </div>

      {lastSaved && status !== 'saving' && (
        <span className="text-gray-500">
          • {formatLastSaved(lastSaved)}
        </span>
      )}

      {status === 'error' && error && onRetry && (
        <button
          onClick={onRetry}
          className="ml-2 px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
        >
          Retry
        </button>
      )}

      {status === 'error' && error && (
        <div className="ml-2 text-xs text-red-600 max-w-xs truncate" title={error}>
          ({error})
        </div>
      )}
    </div>
  );
};

export default AutoSaveIndicator;
