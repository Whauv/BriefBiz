import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type { AuthUser, NotificationItem, Preferences } from "../types";
import { defaultPreferences, mockNotifications } from "../utils/mockData";
import { AUTH_TOKEN_KEY } from "../utils/query";

interface AppStoreValue {
  bookmarks: number[];
  dismissed: number[];
  preferences: Preferences;
  notifications: NotificationItem[];
  authToken: string | null;
  currentUser: AuthUser | null;
  isAuthenticated: boolean;
  toggleBookmark: (articleId: number) => void;
  dismissArticle: (articleId: number) => void;
  restoreDismissed: () => void;
  markNotificationsRead: () => void;
  setNotifications: (items: NotificationItem[]) => void;
  updatePreferences: (next: Partial<Preferences>) => void;
  followCompany: (name: string) => void;
  followInvestor: (name: string) => void;
  setSession: (token: string, user: AuthUser) => void;
  clearSession: () => void;
  setCurrentUser: (user: AuthUser | null) => void;
}

const AppStoreContext = createContext<AppStoreValue | null>(null);

const BOOKMARKS_KEY = "briefbiz-bookmarks";
const DISMISSED_KEY = "briefbiz-dismissed";
const PREFERENCES_KEY = "briefbiz-preferences";
const NOTIFICATIONS_KEY = "briefbiz-notifications";
const CURRENT_USER_KEY = "briefbiz-current-user";

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
  const [authToken, setAuthToken] = useState<string | null>(() => readStorage(AUTH_TOKEN_KEY, null));
  const [currentUser, setCurrentUserState] = useState<AuthUser | null>(() => readStorage(CURRENT_USER_KEY, null));

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

  useEffect(() => {
    if (authToken) {
      window.localStorage.setItem(AUTH_TOKEN_KEY, JSON.stringify(authToken));
    } else {
      window.localStorage.removeItem(AUTH_TOKEN_KEY);
    }
  }, [authToken]);

  useEffect(() => {
    if (currentUser) {
      window.localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(currentUser));
    } else {
      window.localStorage.removeItem(CURRENT_USER_KEY);
    }
  }, [currentUser]);

  const value = useMemo<AppStoreValue>(
    () => ({
      bookmarks,
      dismissed,
      preferences,
      notifications,
      authToken,
      currentUser,
      isAuthenticated: Boolean(authToken && currentUser),
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
      setNotifications,
      updatePreferences: (next) => {
        setPreferences((current) => {
          const merged = { ...current, ...next };
          if (currentUser) {
            setCurrentUserState({ ...currentUser, preferences: merged });
          }
          return merged;
        });
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
      setSession: (token, user) => {
        setAuthToken(token);
        setCurrentUserState(user);
        setPreferences(user.preferences);
      },
      clearSession: () => {
        setAuthToken(null);
        setCurrentUserState(null);
        setPreferences(defaultPreferences);
        setNotifications(mockNotifications);
      },
      setCurrentUser: (user) => {
        setCurrentUserState(user);
        if (user) {
          setPreferences(user.preferences);
        }
      },
    }),
    [authToken, bookmarks, currentUser, dismissed, notifications, preferences],
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
