import type { ReactNode } from "react";
import { useState } from "react";
import { Bell, Bookmark, Home, Radar, Search, User } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";

import { useAppStore } from "../store/AppStore";
import { cn } from "../utils/cn";

interface AppShellProps {
  children: ReactNode;
}

const tabs = [
  { to: "/", label: "Home", icon: Home },
  { to: "/funding-radar", label: "Funding", icon: Radar },
  { to: "/search", label: "Search", icon: Search },
  { to: "/bookmarks", label: "Bookmarks", icon: Bookmark },
  { to: "/profile", label: "Profile", icon: User },
];

export function AppShell({ children }: AppShellProps) {
  const navigate = useNavigate();
  const { notifications } = useAppStore();
  const [search, setSearch] = useState("");
  const unreadCount = notifications.filter((item) => !item.read).length;

  return (
    <div className="min-h-screen bg-hero-grid text-slate-50">
      <header className="sticky top-0 z-20 border-b border-white/10 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-4">
          <button type="button" onClick={() => navigate("/")} className="text-left">
            <div className="text-xs uppercase tracking-[0.35em] text-sky-200/70">BriefBiz</div>
            <div className="text-lg font-semibold">Business news, distilled</div>
          </button>
          <form
            className="hidden flex-1 items-center rounded-full border border-white/10 bg-white/5 px-4 py-2 md:flex"
            onSubmit={(event) => {
              event.preventDefault();
              navigate(`/search?q=${encodeURIComponent(search)}`);
            }}
          >
            <Search className="mr-2 h-4 w-4 text-slate-400" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search companies, investors, headlines..."
              className="w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-400"
            />
          </form>
          <button
            type="button"
            onClick={() => navigate("/profile")}
            className="relative ml-auto inline-flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-white/5"
          >
            <Bell className="h-5 w-5" />
            {unreadCount > 0 ? (
              <span className="absolute -right-1 -top-1 inline-flex min-h-5 min-w-5 items-center justify-center rounded-full bg-amber-300 px-1 text-[10px] font-bold text-slate-950">
                {unreadCount}
              </span>
            ) : null}
          </button>
          <div className="hidden h-10 w-10 rounded-full bg-gradient-to-br from-emerald-300 to-sky-400 md:block" />
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 pb-28 pt-6 md:pb-8">{children}</main>

      <nav className="fixed bottom-0 left-0 right-0 z-20 border-t border-white/10 bg-slate-950/90 px-2 py-3 backdrop-blur md:hidden">
        <div className="mx-auto flex max-w-xl items-center justify-between">
          {tabs.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  "flex min-w-14 flex-col items-center gap-1 rounded-xl px-2 py-1 text-xs text-slate-400 transition",
                  isActive && "bg-white/10 text-white",
                )
              }
            >
              <Icon className="h-4 w-4" />
              <span>{label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}
