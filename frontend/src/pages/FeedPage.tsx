import { AnimatePresence, motion } from "framer-motion";
import { BookmarkCheck, RotateCcw, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";

import { DeepDiveModal } from "../components/DeepDiveModal";
import { Panel } from "../components/Panel";
import { StatCard } from "../components/StatCard";
import { StoryCard } from "../components/StoryCard";
import { useFeedData, useFundingRadarData } from "../hooks/useBriefBizData";
import { useAppStore } from "../store/AppStore";
import type { Article } from "../types";

export function FeedPage() {
  const { data: articles = [], isLoading } = useFeedData();
  const { data: fundingArticles = [] } = useFundingRadarData();
  const { bookmarks, dismissed, dismissArticle, restoreDismissed, toggleBookmark } = useAppStore();
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);

  const visibleArticles = useMemo(
    () => articles.filter((article) => !dismissed.includes(article.id)),
    [articles, dismissed],
  );

  const activeStack = visibleArticles.slice(0, 3);

  return (
    <div className="space-y-6">
      <section className="grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="max-w-3xl">
          <p className="text-sm uppercase tracking-[0.35em] text-emerald-200/70">Global startup pulse</p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight text-white md:text-5xl">
            Swipe through the business stories that actually move markets.
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-8 text-slate-300">
            BriefBiz turns heavyweight startup and business reporting into fast, high-signal cards with a founder lens.
            Swipe right to save, left to dismiss, and tap any card to open the deep dive.
          </p>
        </div>

        <div className="grid gap-3 md:grid-cols-3 lg:grid-cols-1">
          <StatCard label="Saved stories" value={bookmarks.length.toString()} icon={<BookmarkCheck className="h-5 w-5" />} />
          <StatCard label="Dismissed today" value={dismissed.length.toString()} icon={<Sparkles className="h-5 w-5" />} />
          <button
            type="button"
            onClick={restoreDismissed}
            className="rounded-[1.75rem] border border-white/10 bg-white/5 p-5 text-left transition hover:bg-white/10"
          >
            <div className="mb-3 inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-white/10">
              <RotateCcw className="h-5 w-5" />
            </div>
            <div className="text-sm uppercase tracking-[0.24em] text-slate-400">Reset deck</div>
            <div className="mt-2 text-lg font-semibold text-white">Bring skipped stories back</div>
          </button>
        </div>
      </section>

      {isLoading ? (
        <section className="rounded-[2rem] border border-white/10 bg-white/5 p-10 text-center text-slate-300">
          Loading your briefing deck...
        </section>
      ) : (
        <section className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="relative min-h-[38rem]">
            <AnimatePresence>
              {activeStack.map((article, index) => (
                <motion.div
                  key={article.id}
                  className="absolute inset-0"
                  initial={{ opacity: 0, y: 22, scale: 0.97 }}
                  animate={{ opacity: 1, y: index * 14, scale: 1 - index * 0.03 }}
                  exit={{ opacity: 0, x: -220, rotate: -8 }}
                  transition={{ duration: 0.24 }}
                  style={{ zIndex: activeStack.length - index }}
                >
                  <StoryCard
                    article={article}
                    onOpen={() => setSelectedArticle(article)}
                    onBookmark={() => toggleBookmark(article.id)}
                    onDismiss={() => dismissArticle(article.id)}
                  />
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          <aside className="space-y-4">
            <Panel className="p-6">
              <div className="text-xs uppercase tracking-[0.3em] text-slate-400">Funding Radar</div>
              <div className="mt-3 space-y-4">
                {fundingArticles.slice(0, 3).map((article) => (
                  <button
                    type="button"
                    key={article.id}
                    onClick={() => setSelectedArticle(article)}
                    className="w-full rounded-3xl border border-white/10 bg-slate-950/50 p-4 text-left"
                  >
                    <div className="text-sm text-emerald-200">{article.companies[0]}</div>
                    <div className="mt-1 text-lg font-semibold text-white">{article.amount ?? "New round"}</div>
                    <p className="mt-2 text-sm leading-6 text-slate-300">{article.summary_60w.slice(0, 120)}...</p>
                  </button>
                ))}
              </div>
            </Panel>

            <Panel className="p-6">
              <div className="text-xs uppercase tracking-[0.3em] text-slate-400">How to use</div>
              <div className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
                <p>Swipe right to bookmark an article for later.</p>
                <p>Swipe left to clear it from the current deck.</p>
                <p>Tap any story to open the deep-dive view with key players and market impact.</p>
              </div>
            </Panel>
          </aside>
        </section>
      )}

      <DeepDiveModal article={selectedArticle} onClose={() => setSelectedArticle(null)} />
    </div>
  );
}
