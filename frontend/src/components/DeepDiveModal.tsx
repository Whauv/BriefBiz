import { AnimatePresence, motion } from "framer-motion";
import { ArrowUpRight, Share2, X } from "lucide-react";
import { Link } from "react-router-dom";

import type { Article } from "../types";
import { StatusPill } from "./StatusPill";

interface DeepDiveModalProps {
  article: Article | null;
  onClose: () => void;
}

export function DeepDiveModal({ article, onClose }: DeepDiveModalProps) {
  const disagreementPerspectives = article?.conflict_context?.perspectives ?? [];

  return (
    <AnimatePresence>
      {article ? (
        <>
          <motion.button
            type="button"
            className="fixed inset-0 z-30 bg-slate-950/70 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.section
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={{ type: "spring", damping: 22, stiffness: 220 }}
            className="fixed inset-x-0 bottom-0 z-40 mx-auto max-h-[88vh] max-w-4xl overflow-y-auto rounded-t-[2rem] border border-white/10 bg-slate-950/95 p-6 shadow-2xl"
          >
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <div className="mb-3 flex flex-wrap gap-2">
                  <StatusPill tone="tag">{article.source_name}</StatusPill>
                  <StatusPill tone={article.sentiment}>{article.sentiment}</StatusPill>
                  {article.sources_disagree ? <StatusPill tone="risk">Sources Disagree</StatusPill> : null}
                </div>
                <h2 className="max-w-3xl text-2xl font-semibold text-white">{article.title}</h2>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-white/5"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <Section title="What Happened" body={article.deep_dive.what_happened} />
              <Section title="Market Impact" body={article.deep_dive.market_impact} />
            </div>

            <section className="mt-4 rounded-3xl border border-white/10 bg-white/5 p-5">
              <div className="text-xs uppercase tracking-[0.3em] text-slate-400">Key Players</div>
              <div className="mt-3 flex flex-wrap gap-2">
                {article.deep_dive.key_players.map((player) => {
                  const companySlug = article.companies
                    .find((company) => company === player)
                    ?.toLowerCase()
                    .replace(/\s+/g, "-");
                  return companySlug ? (
                    <Link
                      key={player}
                      to={`/companies/${companySlug}`}
                      className="rounded-full border border-white/10 bg-white/10 px-3 py-2 text-sm text-white"
                    >
                      {player}
                    </Link>
                  ) : (
                    <span
                      key={player}
                      className="rounded-full border border-white/10 bg-white/10 px-3 py-2 text-sm text-white"
                    >
                      {player}
                    </span>
                  );
                })}
              </div>
            </section>

            {article.sources_disagree ? (
              <section className="mt-4 grid gap-4 rounded-3xl border border-amber-300/20 bg-amber-200/5 p-5 md:grid-cols-2">
                <Section
                  title={
                    disagreementPerspectives[0]
                      ? `${disagreementPerspectives[0].source_name} view`
                      : "Bull Case"
                  }
                  body={
                    disagreementPerspectives[0]?.summary ??
                    "Bundled AI products can accelerate enterprise adoption and strengthen the platform position of category leaders."
                  }
                />
                <Section
                  title={
                    disagreementPerspectives[1]
                      ? `${disagreementPerspectives[1].source_name} view`
                      : "Bear Case"
                  }
                  body={
                    disagreementPerspectives[1]?.summary ??
                    "Horizontal SaaS vendors may lose pricing power before buyers fully trust the bundled AI stack."
                  }
                />
              </section>
            ) : null}

            <Section title="What's Next" body={article.deep_dive.whats_next} className="mt-4" />

            <div className="mt-6 flex flex-wrap gap-3">
              <a
                href={article.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-3 text-sm font-semibold text-slate-950"
              >
                Read Full Story
                <ArrowUpRight className="h-4 w-4" />
              </a>
              <button
                type="button"
                onClick={() => {
                  window.open(
                    `${import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"}/articles/${article.id}/share-card/image`,
                    "_blank",
                  );
                }}
                className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-3 text-sm text-white"
              >
                <Share2 className="h-4 w-4" />
                Share
              </button>
            </div>
          </motion.section>
        </>
      ) : null}
    </AnimatePresence>
  );
}

interface SectionProps {
  title: string;
  body: string;
  className?: string;
}

function Section({ title, body, className }: SectionProps) {
  return (
    <section className={`rounded-3xl border border-white/10 bg-white/5 p-5 ${className ?? ""}`}>
      <div className="text-xs uppercase tracking-[0.3em] text-slate-400">{title}</div>
      <p className="mt-3 text-sm leading-7 text-slate-200">{body}</p>
    </section>
  );
}
