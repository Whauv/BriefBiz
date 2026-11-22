import { useAppStore } from "../store/AppStore";
import { useUpdatePreferences } from "./useAuth";

type ToggleableKey = "sectors" | "regions";

/**
 * Preference editing with the local-store + server-persist dual write centralized.
 *
 * Updating a preference always updates the local store immediately; when the user is
 * authenticated it also persists to the backend. This pattern was previously inlined
 * (and repeated) in ProfilePage.
 */
export function usePreferencesSync() {
  const { preferences, updatePreferences, isAuthenticated } = useAppStore();
  const persist = useUpdatePreferences();

  const togglePreference = (key: ToggleableKey, option: string) => {
    const current = preferences[key];
    const next = current.includes(option)
      ? current.filter((value) => value !== option)
      : [...current, option];

    updatePreferences({ [key]: next });
    if (isAuthenticated) {
      void persist.mutateAsync({ [key]: next });
    }
  };

  return { preferences, togglePreference };
}
