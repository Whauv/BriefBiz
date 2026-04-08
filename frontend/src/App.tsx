import { Outlet } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { useSessionSync } from "./hooks/useAuth";

export function App() {
  useSessionSync();
  return (
    <AppShell>
      <Outlet />
    </AppShell>
  );
}
