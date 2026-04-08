import { useState } from "react";

import { useLogin, useLogout, useRegister, useUpdatePreferences } from "../hooks/useAuth";
import { useNotificationData } from "../hooks/useBriefBizData";
import { useAppStore } from "../store/AppStore";
import { getApiErrorMessage } from "../utils/api";

const sectors = ["FinTech", "SaaS", "HealthTech", "DeepTech", "Consumer", "Climate", "Emerging Markets"];
const regions = ["US", "Europe", "India", "Southeast Asia", "Africa", "LatAm", "Global"];

export function ProfilePage() {
  const {
    currentUser,
    isAuthenticated,
    preferences,
    updatePreferences,
    followCompany,
    followInvestor,
    markNotificationsRead,
    notifications,
  } = useAppStore();
  useNotificationData();
  const register = useRegister();
  const login = useLogin();
  const persistPreferences = useUpdatePreferences();
  const logout = useLogout();
  const [companyInput, setCompanyInput] = useState("");
  const [investorInput, setInvestorInput] = useState("");
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authForm, setAuthForm] = useState({ name: "", email: "", password: "" });

  const authError = register.error ?? login.error;

  const handlePreferenceToggle = (key: "sectors" | "regions", option: string) => {
    const currentValues = preferences[key];
    const nextValues = currentValues.includes(option)
      ? currentValues.filter((value) => value !== option)
      : [...currentValues, option];
    updatePreferences({ [key]: nextValues });
    if (isAuthenticated) {
      void persistPreferences.mutateAsync({ [key]: nextValues });
    }
  };

  const handleSubmitAuth = async () => {
    if (authMode === "register") {
      await register.mutateAsync(authForm);
      return;
    }
    await login.mutateAsync(authForm);
  };

  return (
    <div className="space-y-6">
      <section className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="rounded-[2rem] border border-white/10 bg-white/5 p-6">
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
                Mark notifications read ({notifications.filter((item) => !item.read).length})
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
                <p className="text-sm text-rose-200">
                  {getApiErrorMessage(authError, "Authentication failed.")}
                </p>
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

        <div className="rounded-[2rem] border border-white/10 bg-white/5 p-6">
          <PreferenceGroup
            title="Sectors"
            options={sectors}
            selected={preferences.sectors}
            onToggle={(option) => handlePreferenceToggle("sectors", option)}
          />
          <PreferenceGroup
            title="Regions"
            options={regions}
            selected={preferences.regions}
            onToggle={(option) => handlePreferenceToggle("regions", option)}
          />
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <FollowBox
          title="Follow companies"
          value={companyInput}
          onChange={setCompanyInput}
          items={preferences.followed_companies}
          placeholder="Add a company"
          onSubmit={() => {
            followCompany(companyInput);
            if (isAuthenticated) {
              void persistPreferences.mutateAsync({
                followed_companies: [...preferences.followed_companies, companyInput.trim()].filter(Boolean),
              });
            }
            setCompanyInput("");
          }}
        />
        <FollowBox
          title="Follow investors"
          value={investorInput}
          onChange={setInvestorInput}
          items={preferences.followed_investors}
          placeholder="Add an investor"
          onSubmit={() => {
            followInvestor(investorInput);
            if (isAuthenticated) {
              void persistPreferences.mutateAsync({
                followed_investors: [...preferences.followed_investors, investorInput.trim()].filter(Boolean),
              });
            }
            setInvestorInput("");
          }}
        />
      </section>
    </div>
  );
}

interface PreferenceGroupProps {
  title: string;
  options: string[];
  selected: string[];
  onToggle: (option: string) => void;
}

function PreferenceGroup({ title, options, selected, onToggle }: PreferenceGroupProps) {
  return (
    <section className="mb-6 last:mb-0">
      <div className="text-xs uppercase tracking-[0.3em] text-slate-400">{title}</div>
      <div className="mt-4 flex flex-wrap gap-3">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => onToggle(option)}
            className={`rounded-full border px-4 py-2 text-sm transition ${
              selected.includes(option)
                ? "border-emerald-300/30 bg-emerald-300/15 text-emerald-100"
                : "border-white/10 bg-white/5 text-slate-300"
            }`}
          >
            {option}
          </button>
        ))}
      </div>
    </section>
  );
}

interface FollowBoxProps {
  title: string;
  value: string;
  onChange: (value: string) => void;
  items: string[];
  placeholder: string;
  onSubmit: () => void;
}

function FollowBox({ title, value, onChange, items, placeholder, onSubmit }: FollowBoxProps) {
  return (
    <section className="rounded-[2rem] border border-white/10 bg-white/5 p-6">
      <div className="text-xs uppercase tracking-[0.3em] text-slate-400">{title}</div>
      <div className="mt-4 flex gap-3">
        <input
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          className="flex-1 rounded-full border border-white/10 bg-slate-950/50 px-4 py-3 text-white outline-none placeholder:text-slate-500"
        />
        <button
          type="button"
          onClick={onSubmit}
          className="rounded-full bg-white px-4 py-3 text-sm font-semibold text-slate-950"
        >
          Add
        </button>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {items.map((item) => (
          <span key={item} className="rounded-full border border-white/10 bg-white/10 px-3 py-2 text-sm text-white">
            {item}
          </span>
        ))}
      </div>
    </section>
  );
}
