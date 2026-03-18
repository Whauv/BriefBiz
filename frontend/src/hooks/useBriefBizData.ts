import { useQuery } from "@tanstack/react-query";

import type { Article, CompanyProfile, NotificationItem } from "../types";
import { mockArticles, mockCompanies, mockNotifications } from "../utils/mockData";
import { apiClient } from "../utils/api";

async function withFallback<T>(request: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await request();
  } catch {
    return fallback;
  }
}

export function useFeedData() {
  return useQuery({
    queryKey: ["feed"],
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
  return useQuery({
    queryKey: ["notifications"],
    queryFn: () =>
      withFallback(
        async () => {
          const { data } = await apiClient.get<NotificationItem[]>("/notifications");
          return data;
        },
        mockNotifications,
      ),
  });
}
