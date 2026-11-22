import {
  createContext,
  useContext,
  useMemo,
  type ReactNode,
} from "react";

import { usePersistentState } from "../hooks/usePersistentState";
import type { AuthUser, NotificationItem, Preferences } from "../types";
import { setApiAuthToken } from "../utils/api";
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

interface AppStoreProviderProps {
  children: ReactNode;
}

export function AppStoreProvider({ children }: AppStoreProviderProps) {
  const [bookmarks, setBookmarks] = usePersistentState<number[]>(BOOKMARKS_KEY, [101, 103]);
  const [dismissed, setDismissed] = usePersistentState<number[]>(DISMISSED_KEY, []);
  const [preferences, setPreferences] = usePersistentState<Preferences>(PREFERENCES_KEY, defaultPreferences);
  const [notifications, setNotifications] = usePersistentState<NotificationItem[]>(
    NOTIFICATIONS_KEY,
    mockNotifications,
  );
  const [authToken, setAuthToken] = usePersistentState<string | null>(AUTH_TOKEN_KEY, null);
  const [currentUser, setCurrentUserState] = usePersistentState<AuthUser | null>(CURRENT_USER_KEY, null);

  // Keep the API client's bearer token in sync with the store (single source of truth).
  // Done during render so the token is set before children fire their first request.
  setApiAuthToken(authToken);

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
