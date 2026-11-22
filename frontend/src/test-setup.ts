import "@testing-library/jest-dom/vitest";
import { afterEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";

// Unmount React trees and reset per-test global state after every test so DOM,
// localStorage, and stubbed env vars never leak between cases.
afterEach(() => {
  cleanup();
  try {
    window.localStorage.clear();
  } catch {
    // ignore
  }
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});
