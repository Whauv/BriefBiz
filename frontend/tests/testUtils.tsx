import type { ReactElement, ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, renderHook } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import { AppStoreProvider } from "../src/store/AppStore";

/** Build a providers wrapper (react-query + app store + router) for tests. */
export function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });

  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <AppStoreProvider>
          <MemoryRouter>{children}</MemoryRouter>
        </AppStoreProvider>
      </QueryClientProvider>
    );
  };
}

export function renderWithProviders(ui: ReactElement) {
  return render(ui, { wrapper: createWrapper() });
}

export function renderHookWithProviders<T>(callback: () => T) {
  return renderHook(callback, { wrapper: createWrapper() });
}
