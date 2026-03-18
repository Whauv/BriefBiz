import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type { NotificationItem, Preferences } from "../types";
import { defaultPreferences, mockNotifications } from "../utils/mockData";

interface AppStoreValue {
  bookmarks: number[];
  dismissed: number[];
  preferences: Preferences;
  notifications: NotificationItem[];
  toggleBookmark: (articleId: number) => void;
  dismissArticle: (articleId: number) => void;
  restoreDismissed: () => void;
  markNotificationsRead: () => void;
  updatePreferences: (next: Partial<Preferences>) => void;
  followCompany: (name: string) => void;
  followInvestor: (name: string) => void;
}

const AppStoreContext = createContext<AppStoreValue | null>(null);

const BOOKMARKS_KEY = "briefbiz-bookmarks";
const DISMISSED_KEY = "briefbiz-dismissed";
const PREFERENCES_KEY = "briefbiz-preferences";
const NOTIFICATIONS_KEY = "briefbiz-notifications";

function readStorage<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") {
    return fallback;
  }
  const value = window.localStorage.getItem(key);
  if (!value) {
    return fallback;
  }
  try {
    return JSON.parse(value) as T;
  } catch {
    return fallback;
  }
}

interface AppStoreProviderProps {
  children: ReactNode;
}

export function AppStoreProvider({ children }: AppStoreProviderProps) {
  const [bookmarks, setBookmarks] = useState<number[]>(() => readStorage(BOOKMARKS_KEY, [101, 103]));
  const [dismissed, setDismissed] = useState<number[]>(() => readStorage(DISMISSED_KEY, []));
  const [preferences, setPreferences] = useState<Preferences>(() =>
    readStorage(PREFERENCES_KEY, defaultPreferences),
  );
  const [notifications, setNotifications] = useState<NotificationItem[]>(() =>
    readStorage(NOTIFICATIONS_KEY, mockNotifications),
  );

  useEffect(() => {
    window.localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
  }, [bookmarks]);

  useEffect(() => {
    window.localStorage.setItem(DISMISSED_KEY, JSON.stringify(dismissed));
  }, [dismissed]);

  useEffect(() => {
    window.localStorage.setItem(PREFERENCES_KEY, JSON.stringify(preferences));
  }, [preferences]);

  useEffect(() => {
    window.localStorage.setItem(NOTIFICATIONS_KEY, JSON.stringify(notifications));
  }, [notifications]);

  const value = useMemo<AppStoreValue>(
    () => ({
      bookmarks,
      dismissed,
      preferences,
      notifications,
      toggleBookmark: (articleId) => {
        setBookmarks((current) =>
          current.includes(articleId) ? current.filter((id) => id !== articleId) : [...current, articleId],
        );
      },
      dismissArticle: (articleId) => {
        setDismissed((current) => (current.includes(articleId) ? current : [...current, articleId]));
      },
      restoreDismissed: () => setDismissed([]),
      markNotificationsRead: () => {
        setNotifications((current) => current.map((item) => ({ ...item, read: true })));
      },
      updatePreferences: (next) => {
        setPreferences((current) => ({ ...current, ...next }));
      },
      followCompany: (name) => {
        const normalized = name.trim();
        if (!normalized) return;
        setPreferences((current) => ({
          ...current,
          followed_companies: current.followed_companies.includes(normalized)
            ? current.followed_companies
            : [...current.followed_companies, normalized],
        }));
      },
      followInvestor: (name) => {
        const normalized = name.trim();
        if (!normalized) return;
        setPreferences((current) => ({
          ...current,
          followed_investors: current.followed_investors.includes(normalized)
            ? current.followed_investors
            : [...current.followed_investors, normalized],
        }));
      },
    }),
    [bookmarks, dismissed, notifications, preferences],
  );

  return <AppStoreContext.Provider value={value}>{children}</AppStoreContext.Provider>;
}

export function useAppStore() {
  const context = useContext(AppStoreContext);
  if (!context) {
    throw new Error("useAppStore must be used within AppStoreProvider");
  }
  return context;
}
