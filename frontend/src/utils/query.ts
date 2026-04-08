export const AUTH_TOKEN_KEY = "briefbiz-auth-token";

export function isMockFallbackEnabled() {
  return import.meta.env.DEV && import.meta.env.VITE_ENABLE_MOCK_FALLBACK === "true";
}
