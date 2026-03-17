import { useQuery } from "@tanstack/react-query";

import { apiClient } from "../utils/api";

interface HealthResponse {
  status: string;
  services: Record<string, string>;
}

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const { data } = await apiClient.get<HealthResponse>("/health");
      return data;
    },
  });
}

