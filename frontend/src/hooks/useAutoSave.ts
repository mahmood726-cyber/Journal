/**
 * Auto-save hook for manuscript forms.
 *
 * Features:
 * - Automatic saving every 10 seconds
 * - Debounced to prevent excessive saves
 * - Visual save status indicator
 * - Error handling and retry logic
 * - Local storage backup as fallback
 */
import { useEffect, useRef, useState, useCallback } from 'react';

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

interface UseAutoSaveOptions<T> {
  data: T;
  onSave: (data: T) => Promise<void>;
  debounceMs?: number;
  localStorageKey?: string;
  enabled?: boolean;
}

interface UseAutoSaveReturn {
  saveStatus: SaveStatus;
  lastSaved: Date | null;
  saveNow: () => Promise<void>;
  error: string | null;
}

export const useAutoSave = <T extends Record<string, any>>({
  data,
  onSave,
  debounceMs = 10000, // 10 seconds
  localStorageKey,
  enabled = true,
}: UseAutoSaveOptions<T>): UseAutoSaveReturn => {
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const previousDataRef = useRef<string>('');
  const isSavingRef = useRef(false);

  const saveNow = useCallback(async () => {
    if (isSavingRef.current || !enabled) return;

    const currentDataString = JSON.stringify(data);

    // Skip if data hasn't changed
    if (currentDataString === previousDataRef.current) {
      return;
    }

    isSavingRef.current = true;
    setSaveStatus('saving');
    setError(null);

    try {
      // Save to server
      await onSave(data);

      // Save to local storage as backup
      if (localStorageKey) {
        localStorage.setItem(localStorageKey, currentDataString);
        localStorage.setItem(`${localStorageKey}_timestamp`, new Date().toISOString());
      }

      previousDataRef.current = currentDataString;
      setSaveStatus('saved');
      setLastSaved(new Date());

      // Reset status after 2 seconds
      setTimeout(() => {
        setSaveStatus('idle');
      }, 2000);
    } catch (err) {
      console.error('[AutoSave] Save failed:', err);
      setSaveStatus('error');
      setError(err instanceof Error ? err.message : 'Save failed');

      // Still save to local storage as fallback
      if (localStorageKey) {
        try {
          localStorage.setItem(localStorageKey, currentDataString);
          localStorage.setItem(`${localStorageKey}_timestamp`, new Date().toISOString());
          console.log('[AutoSave] Saved to local storage as fallback');
        } catch (storageErr) {
          console.error('[AutoSave] Local storage save failed:', storageErr);
        }
      }
    } finally {
      isSavingRef.current = false;
    }
  }, [data, onSave, enabled, localStorageKey]);

  // Debounced auto-save
  useEffect(() => {
    if (!enabled) return;

    // Clear existing timeout
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    // Schedule save
    saveTimeoutRef.current = setTimeout(() => {
      saveNow();
    }, debounceMs);

    // Cleanup
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [data, debounceMs, enabled, saveNow]);

  // Save on page unload
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (saveStatus === 'saving') {
        e.preventDefault();
        e.returnValue = 'Your changes are being saved...';
        return e.returnValue;
      }

      const currentDataString = JSON.stringify(data);
      if (currentDataString !== previousDataRef.current && enabled) {
        // Try to save synchronously (may not work in all browsers)
        if (localStorageKey) {
          localStorage.setItem(localStorageKey, currentDataString);
          localStorage.setItem(`${localStorageKey}_timestamp`, new Date().toISOString());
        }
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [data, enabled, localStorageKey, saveStatus]);

  return {
    saveStatus,
    lastSaved,
    saveNow,
    error,
  };
};

/**
 * Load auto-saved data from local storage.
 */
export const loadAutoSavedData = <T>(localStorageKey: string): { data: T | null; timestamp: Date | null } => {
  try {
    const savedData = localStorage.getItem(localStorageKey);
    const savedTimestamp = localStorage.getItem(`${localStorageKey}_timestamp`);

    if (savedData && savedTimestamp) {
      return {
        data: JSON.parse(savedData) as T,
        timestamp: new Date(savedTimestamp),
      };
    }
  } catch (error) {
    console.error('[AutoSave] Failed to load auto-saved data:', error);
  }

  return { data: null, timestamp: null };
};

/**
 * Clear auto-saved data from local storage.
 */
export const clearAutoSavedData = (localStorageKey: string): void => {
  try {
    localStorage.removeItem(localStorageKey);
    localStorage.removeItem(`${localStorageKey}_timestamp`);
  } catch (error) {
    console.error('[AutoSave] Failed to clear auto-saved data:', error);
  }
};
