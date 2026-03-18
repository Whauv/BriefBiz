import type { ReactNode } from "react";

import { cn } from "../utils/cn";

interface StatusPillProps {
  tone: "bullish" | "bearish" | "risk" | "neutral" | "tag";
  children: ReactNode;
}

const toneClasses: Record<StatusPillProps["tone"], string> = {
  bullish: "border-emerald-300/20 bg-emerald-400/15 text-emerald-200",
  bearish: "border-rose-300/20 bg-rose-400/15 text-rose-200",
  risk: "border-amber-200/20 bg-amber-300/15 text-amber-100",
  neutral: "border-slate-300/20 bg-slate-400/15 text-slate-200",
  tag: "border-sky-200/20 bg-sky-300/10 text-sky-100",
};

export function StatusPill({ tone, children }: StatusPillProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-3 py-1 text-[11px] font-medium uppercase tracking-[0.22em]",
        toneClasses[tone],
      )}
    >
      {children}
    </span>
  );
}
