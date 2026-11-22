import { useEffect, useState } from "react";

/**
 * `useState` whose value is mirrored to `localStorage` under `key`.
 *
 * Collapses the repeated "read on init + write on change" boilerplate the store used
 * to carry. All storage access is guarded so SSR, private-mode, and corrupt/blocked
 * storage degrade to the in-memory fallback instead of throwing.
 */
export function usePersistentState<T>(key: string, fallback: T) {
  const [value, setValue] = useState<T>(() => readStorage(key, fallback));

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // Ignore quota/availability errors — state still works in memory.
    }
  }, [key, value]);

  return [value, setValue] as const;
}

export function readStorage<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") {
    return fallback;
  }
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) {
      return fallback;
    }
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}
