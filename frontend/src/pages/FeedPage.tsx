import { motion } from "framer-motion";

import { useHealth } from "../hooks/useHealth";

export function FeedPage() {
  const health = useHealth();

  return (
    <div className="space-y-6">
      <section className="max-w-2xl">
        <p className="text-sm uppercase tracking-[0.35em] text-emerald-200/70">Global startup pulse</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight text-white">
          Swipe through the business stories that actually move markets.
        </h1>
        <p className="mt-3 text-base text-slate-300">
          Phase 1 scaffold is live with FastAPI, Redis, Celery, Elasticsearch, React Query, and routing
          wired together.
        </p>
      </section>

      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="grid gap-6 lg:grid-cols-[1.5fr_1fr]"
      >
        <article className="rounded-[2rem] border border-white/10 bg-white/8 p-6 shadow-glow backdrop-blur">
          <div className="mb-4 flex items-center justify-between text-sm text-slate-300">
            <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-emerald-200">Infrastructure ready</span>
            <span>Backend status: {health.data?.status ?? "checking..."}</span>
          </div>
          <h2 className="text-2xl font-semibold">BriefBiz monorepo initialized</h2>
          <p className="mt-3 leading-7 text-slate-300">
            The app now has a backend service layer, async database/session setup, Redis cache client,
            Celery worker bootstrap, Elasticsearch client, and a frontend shell ready for the product
            pages we will build next.
          </p>
        </article>

        <aside className="rounded-[2rem] border border-white/10 bg-slate-950/50 p-6">
          <div className="text-sm text-slate-400">Tracked services</div>
          <div className="mt-4 space-y-3 text-sm">
            {Object.entries(health.data?.services ?? {}).map(([service, status]) => (
              <div key={service} className="flex items-center justify-between rounded-2xl bg-white/5 px-4 py-3">
                <span className="capitalize">{service}</span>
                <span className="text-slate-300">{status}</span>
              </div>
            ))}
          </div>
        </aside>
      </motion.section>
    </div>
  );
}

