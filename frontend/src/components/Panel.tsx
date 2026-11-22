import type { ReactNode } from "react";

import { cn } from "../utils/cn";

/** Shared glassmorphism surface: `rounded-[2rem] border border-white/10 bg-white/5`. */
export const panelClass = "rounded-[2rem] border border-white/10 bg-white/5";

interface PanelProps {
  children: ReactNode;
  className?: string;
}

export function Panel({ children, className }: PanelProps) {
  return <div className={cn(panelClass, className)}>{children}</div>;
}
