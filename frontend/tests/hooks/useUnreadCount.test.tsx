import { act } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useAppStore } from "../../src/store/AppStore";
import { useUnreadCount } from "../../src/hooks/useUnreadCount";
import { renderHookWithProviders } from "../testUtils";

describe("useUnreadCount", () => {
  it("counts only unread notifications", () => {
    const { result } = renderHookWithProviders(() => ({
      store: useAppStore(),
      unread: useUnreadCount(),
    }));

    act(() =>
      result.current.store.setNotifications([
        { id: 1, user_id: 1, article_id: 1, type: "x", read: false, created_at: "" },
        { id: 2, user_id: 1, article_id: 2, type: "x", read: true, created_at: "" },
        { id: 3, user_id: 1, article_id: 3, type: "x", read: false, created_at: "" },
      ]),
    );

    expect(result.current.unread).toBe(2);
  });
});
