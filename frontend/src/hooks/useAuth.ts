import { useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { AuthResponse, AuthUser, Preferences } from "../types";
import { apiClient } from "../utils/api";
import { useAppStore } from "../store/AppStore";

interface AuthPayload {
  email: string;
  password: string;
  name?: string;
}

export function useBootstrapSession() {
  const { authToken } = useAppStore();

  return useQuery({
    queryKey: ["auth", "me"],
    enabled: Boolean(authToken),
    staleTime: 60_000,
    retry: false,
    queryFn: async () => {
      const { data } = await apiClient.get<AuthUser>("/auth/me");
      return data;
    },
    select: (data) => data,
  });
}

export function useSessionSync() {
  const { data, error } = useBootstrapSession();
  const { setCurrentUser, clearSession } = useAppStore();

  useEffect(() => {
    if (data) {
      setCurrentUser(data);
    }
  }, [data, setCurrentUser]);

  useEffect(() => {
    if (error) {
      clearSession();
    }
  }, [clearSession, error]);
}

export function useRegister() {
  const { setSession } = useAppStore();
  return useMutation({
    mutationFn: async (payload: AuthPayload) => {
      const { data } = await apiClient.post<AuthResponse>("/auth/register", payload);
      return data;
    },
    onSuccess: (data) => setSession(data.access_token, data.user),
  });
}

export function useLogin() {
  const { setSession } = useAppStore();
  return useMutation({
    mutationFn: async (payload: AuthPayload) => {
      const { data } = await apiClient.post<AuthResponse>("/auth/login", payload);
      return data;
    },
    onSuccess: (data) => setSession(data.access_token, data.user),
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  const { clearSession } = useAppStore();
  return () => {
    clearSession();
    queryClient.removeQueries({ queryKey: ["auth"] });
    queryClient.removeQueries({ queryKey: ["notifications"] });
  };
}

export function useUpdatePreferences() {
  const { setCurrentUser } = useAppStore();
  return useMutation({
    mutationFn: async (payload: Partial<Preferences>) => {
      const { data } = await apiClient.patch<AuthUser>("/auth/preferences", payload);
      return data;
    },
    onSuccess: (user) => setCurrentUser(user),
  });
}
