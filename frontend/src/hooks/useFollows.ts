import { useAppStore } from "../store/AppStore";
import { useUpdatePreferences } from "./useAuth";

/**
 * Follow/unfollow companies and investors with the local-store + server-persist dual
 * write centralized (previously inlined twice in ProfilePage).
 */
export function useFollows() {
  const { preferences, followCompany, followInvestor, isAuthenticated } = useAppStore();
  const persist = useUpdatePreferences();

  const addCompany = (name: string) => {
    const trimmed = name.trim();
    if (!trimmed) return;
    followCompany(trimmed);
    if (isAuthenticated) {
      void persist.mutateAsync({
        followed_companies: [...preferences.followed_companies, trimmed].filter(Boolean),
      });
    }
  };

  const addInvestor = (name: string) => {
    const trimmed = name.trim();
    if (!trimmed) return;
    followInvestor(trimmed);
    if (isAuthenticated) {
      void persist.mutateAsync({
        followed_investors: [...preferences.followed_investors, trimmed].filter(Boolean),
      });
    }
  };

  return {
    companies: preferences.followed_companies,
    investors: preferences.followed_investors,
    addCompany,
    addInvestor,
  };
}
