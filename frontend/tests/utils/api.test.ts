import { AxiosError } from "axios";
import { describe, expect, it } from "vitest";

import { getApiErrorMessage } from "../../src/utils/api";

describe("getApiErrorMessage", () => {
  it("returns the backend detail string from an axios error", () => {
    const error = new AxiosError("Request failed");
    error.response = {
      data: { detail: "Email already registered" },
      status: 409,
      statusText: "Conflict",
      headers: {},
      config: {} as never,
    };
    expect(getApiErrorMessage(error)).toBe("Email already registered");
  });

  it("returns the fallback for non-axios errors", () => {
    expect(getApiErrorMessage(new Error("boom"), "Default message")).toBe("Default message");
  });

  it("returns the fallback when there is no detail string", () => {
    const error = new AxiosError("Request failed");
    error.response = {
      data: {},
      status: 500,
      statusText: "Server Error",
      headers: {},
      config: {} as never,
    };
    expect(getApiErrorMessage(error, "Fallback")).toBe("Fallback");
  });
});
