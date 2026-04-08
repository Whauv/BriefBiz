import { useQuery } from "@tanstack/react-query";

import type { Article, CompanyProfile, NotificationItem } from "../types";
import { mockArticles, mockCompanies, mockNotifications } from "../utils/mockData";
import { apiClient } from "../utils/api";
import { isMockFallbackEnabled } from "../utils/query";
import { useAppStore } from "../store/AppStore";

async function withFallback<T>(request: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await request();
  } catch {
    if (isMockFallbackEnabled()) {
      return fallback;
    }
    throw new Error("Unable to load BriefBiz data.");
  }
}

export function useFeedData() {
  return useQuery({
    queryKey: ["feed"],
    staleTime: 60_000,
    queryFn: () =>
      withFallback(
        async () => {
          const { data } = await apiClient.get<{ items: Article[] }>("/feed");
          return data.items;
        },
        mockArticles,
      ),
  });
}

export function useFundingRadarData() {
  return useQuery({
    queryKey: ["funding-radar"],
    staleTime: 60_000,
    queryFn: () =>
      withFallback(
        async () => {
          const { data } = await apiClient.get<{ items: Article[] }>("/feed/funding-radar");
          return data.items;
        },
        mockArticles.filter((article) => article.vertical === "funding"),
      ),
  });
}

export function useCompanyData(slug: string | undefined) {
  return useQuery({
    queryKey: ["company", slug],
    enabled: Boolean(slug),
    staleTime: 60_000,
    queryFn: () =>
      withFallback(
        async () => {
          const { data } = await apiClient.get<CompanyProfile>(`/companies/${slug}`);
          return data;
        },
        mockCompanies.find((company) => company.slug === slug) ?? mockCompanies[0],
      ),
  });
}

export function useSearchData(query: string) {
  return useQuery({
    queryKey: ["search", query],
    enabled: query.trim().length > 0,
    staleTime: 15_000,
    queryFn: () =>
      withFallback(
        async () => {
          const { data } = await apiClient.get<{ articles: Article[]; companies: CompanyProfile[] }>("/search", {
            params: { q: query },
          });
          return data;
        },
        {
          articles: mockArticles.filter((article) =>
            `${article.title} ${article.summary_60w} ${article.companies.join(" ")}`
              .toLowerCase()
              .includes(query.toLowerCase()),
          ),
          companies: mockCompanies.filter((company) =>
            `${company.name} ${company.sector}`.toLowerCase().includes(query.toLowerCase()),
          ),
        },
      ),
  });
}

export function useNotificationData() {
  const { isAuthenticated, setNotifications } = useAppStore();
  return useQuery({
    queryKey: ["notifications"],
    enabled: isAuthenticated,
    staleTime: 30_000,
    queryFn: () =>
      withFallback(
        async () => {
          const { data } = await apiClient.get<NotificationItem[]>("/notifications");
          setNotifications(data);
          return data;
        },
        mockNotifications,
      ),
  });
}
