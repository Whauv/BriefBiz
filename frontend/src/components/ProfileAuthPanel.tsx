import { useState } from "react";

import { useLogin, useLogout, useRegister } from "../hooks/useAuth";
import { useUnreadCount } from "../hooks/useUnreadCount";
import { useAppStore } from "../store/AppStore";
import { getApiErrorMessage } from "../utils/api";
import { panelClass } from "./Panel";

export function ProfileAuthPanel() {
  const { currentUser, isAuthenticated, markNotificationsRead } = useAppStore();
  const unreadCount = useUnreadCount();
  const register = useRegister();
  const login = useLogin();
  const logout = useLogout();

  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authForm, setAuthForm] = useState({ name: "", email: "", password: "" });

  const authError = register.error ?? login.error;

  const handleSubmitAuth = async () => {
    if (authMode === "register") {
      await register.mutateAsync(authForm);
      return;
    }
    await login.mutateAsync(authForm);
  };

  return (
    <div className={`${panelClass} p-6`}>
      <div className="h-16 w-16 rounded-full bg-gradient-to-br from-emerald-300 to-sky-400" />
      <h1 className="mt-4 text-3xl font-semibold text-white">{currentUser?.name ?? "Join BriefBiz"}</h1>
      <p className="mt-2 text-sm uppercase tracking-[0.24em] text-slate-400">
        {currentUser?.email ?? "Sign in to sync preferences and notifications"}
      </p>
      {isAuthenticated ? (
        <div className="mt-6 space-y-3">
          <button
            type="button"
            onClick={markNotificationsRead}
            className="w-full rounded-full border border-white/10 bg-white/10 px-4 py-3 text-sm text-white"
          >
            Mark notifications read ({unreadCount})
          </button>
          <button
            type="button"
            onClick={logout}
            className="w-full rounded-full border border-white/10 bg-slate-950/50 px-4 py-3 text-sm text-white"
          >
            Sign out
          </button>
        </div>
      ) : (
        <div className="mt-6 space-y-4">
          <div className="flex rounded-full border border-white/10 bg-slate-950/40 p-1">
            {(["login", "register"] as const).map((mode) => (
              <button
                key={mode}
                type="button"
                onClick={() => setAuthMode(mode)}
                className={`flex-1 rounded-full px-4 py-2 text-sm ${
                  authMode === mode ? "bg-white text-slate-950" : "text-slate-300"
                }`}
              >
                {mode === "login" ? "Sign in" : "Register"}
              </button>
            ))}
          </div>
          {authMode === "register" ? (
            <input
              value={authForm.name}
              onChange={(event) => setAuthForm((current) => ({ ...current, name: event.target.value }))}
              placeholder="Your name"
              className="w-full rounded-full border border-white/10 bg-slate-950/50 px-4 py-3 text-white outline-none placeholder:text-slate-500"
            />
          ) : null}
          <input
            value={authForm.email}
            onChange={(event) => setAuthForm((current) => ({ ...current, email: event.target.value }))}
            placeholder="Email"
            className="w-full rounded-full border border-white/10 bg-slate-950/50 px-4 py-3 text-white outline-none placeholder:text-slate-500"
          />
          <input
            type="password"
            value={authForm.password}
            onChange={(event) => setAuthForm((current) => ({ ...current, password: event.target.value }))}
            placeholder="Password"
            className="w-full rounded-full border border-white/10 bg-slate-950/50 px-4 py-3 text-white outline-none placeholder:text-slate-500"
          />
          {authError ? (
            <p className="text-sm text-rose-200">{getApiErrorMessage(authError, "Authentication failed.")}</p>
          ) : null}
          <button
            type="button"
            onClick={() => void handleSubmitAuth()}
            className="w-full rounded-full bg-white px-4 py-3 text-sm font-semibold text-slate-950"
          >
            {authMode === "login" ? "Sign in" : "Create account"}
          </button>
        </div>
      )}
    </div>
  );
}
