import { BookmarkPlus, Clock3, MoveHorizontal } from "lucide-react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";

import type { Article } from "../types";
import { AudioButton } from "./AudioButton";
import { StatusPill } from "./StatusPill";

interface StoryCardProps {
  article: Article;
  onOpen: () => void;
  onBookmark: () => void;
  onDismiss: () => void;
}

export function StoryCard({ article, onOpen, onBookmark, onDismiss }: StoryCardProps) {
  return (
    <motion.article
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={(_, info) => {
        if (info.offset.x > 130) {
          onBookmark();
        } else if (info.offset.x < -130) {
          onDismiss();
        }
      }}
      className="relative overflow-hidden rounded-[2.25rem] border border-white/10 bg-[radial-gradient(circle_at_top_left,rgba(110,231,183,0.14),transparent_35%),linear-gradient(180deg,rgba(15,23,42,0.92),rgba(2,6,23,0.98))] p-6 shadow-glow"
    >
      {article.image_url ? (
        <div
          className="absolute inset-x-0 top-0 h-40 bg-cover bg-center opacity-25"
          style={{ backgroundImage: `url(${article.image_url})` }}
        />
      ) : null}
      <div className="relative z-10">
        <div className="flex flex-wrap items-center gap-2">
          <StatusPill tone="tag">{article.source_name}</StatusPill>
          <StatusPill tone={article.sentiment}>{article.sentiment}</StatusPill>
          <StatusPill tone="tag">{article.vertical.replace("_", " ")}</StatusPill>
          <StatusPill tone="tag">{article.region}</StatusPill>
        </div>

        <div className="mt-5 flex items-center justify-between text-xs uppercase tracking-[0.26em] text-slate-400">
          <span>Source quality {article.source_quality_score.toFixed(2)}</span>
          <span className="inline-flex items-center gap-2">
            <Clock3 className="h-4 w-4" />
            {new Date(article.published_at).toLocaleDateString()}
          </span>
        </div>

        <button type="button" onClick={onOpen} className="mt-4 text-left">
          <h2 className="text-3xl font-semibold leading-tight text-white">{article.title}</h2>
        </button>
        <p className="mt-4 text-base leading-8 text-slate-200">{article.summary_60w}</p>
        <p className="mt-4 border-l border-emerald-300/30 pl-4 text-sm italic text-emerald-100/90">
          {article.why_it_matters}
        </p>

        <div className="mt-5 flex flex-wrap gap-2">
          {article.companies.map((company) => (
            <Link
              key={company}
              to={`/companies/${company.toLowerCase().replace(/\s+/g, "-")}`}
              className="rounded-full border border-white/10 bg-white/10 px-3 py-2 text-sm text-white"
            >
              {company}
            </Link>
          ))}
        </div>

        <div className="mt-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AudioButton text={article.summary_60w} />
            <button
              type="button"
              onClick={onBookmark}
              className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition hover:bg-white/10"
            >
              <BookmarkPlus className="h-4 w-4" />
              Bookmark
            </button>
          </div>
          <div className="hidden items-center gap-2 text-xs uppercase tracking-[0.26em] text-slate-500 md:flex">
            <MoveHorizontal className="h-4 w-4" />
            Swipe to sort
          </div>
        </div>
      </div>
    </motion.article>
  );
}
