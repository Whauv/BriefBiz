import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { readStorage, usePersistentState } from "../../src/hooks/usePersistentState";

describe("usePersistentState", () => {
  it("uses the fallback when storage is empty", () => {
    const { result } = renderHook(() => usePersistentState("missing-key", 7));
    expect(result.current[0]).toBe(7);
  });

  it("writes updates to localStorage", () => {
    const { result } = renderHook(() => usePersistentState<number[]>("nums", []));
    act(() => result.current[1]([1, 2, 3]));
    expect(result.current[0]).toEqual([1, 2, 3]);
    expect(JSON.parse(window.localStorage.getItem("nums") ?? "null")).toEqual([1, 2, 3]);
  });

  it("reads a previously persisted value on init", () => {
    window.localStorage.setItem("seeded", JSON.stringify({ a: 1 }));
    const { result } = renderHook(() => usePersistentState("seeded", { a: 0 }));
    expect(result.current[0]).toEqual({ a: 1 });
  });
});

describe("readStorage", () => {
  it("returns the fallback on corrupt JSON", () => {
    window.localStorage.setItem("broken", "{not json");
    expect(readStorage("broken", "fallback")).toBe("fallback");
  });
});
