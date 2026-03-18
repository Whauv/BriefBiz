import { Search } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { useSearchData } from "../hooks/useBriefBizData";

export function SearchPage() {
  const [params, setParams] = useSearchParams();
  const [query, setQuery] = useState(params.get("q") ?? "");
  const { data, isFetching } = useSearchData(query);

  useEffect(() => {
    setParams(query ? { q: query } : {}, { replace: true });
  }, [query, setParams]);

  return (
    <div className="space-y-6">
      <section>
        <p className="text-sm uppercase tracking-[0.35em] text-sky-200/80">Search</p>
        <h1 className="mt-3 text-4xl font-semibold text-white">Explore articles and companies in real time</h1>
      </section>

      <section className="rounded-[2rem] border border-white/10 bg-white/5 p-4">
        <div className="flex items-center gap-3">
          <Search className="h-5 w-5 text-slate-400" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search companies, themes, investors..."
            className="w-full bg-transparent text-lg text-white outline-none placeholder:text-slate-400"
          />
        </div>
      </section>

      {isFetching ? <div className="text-slate-300">Searching...</div> : null}

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-[2rem] border border-white/10 bg-white/5 p-6">
          <div className="text-xs uppercase tracking-[0.3em] text-slate-400">Articles</div>
          <div className="mt-4 space-y-4">
            {data?.articles.map((article) => (
              <article key={article.id} className="rounded-3xl border border-white/10 bg-slate-950/50 p-4">
                <div className="text-sm text-slate-400">{article.source_name}</div>
                <div className="mt-1 text-xl font-semibold text-white">{article.title}</div>
                <p className="mt-2 text-sm leading-7 text-slate-300">{article.summary_60w}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-white/5 p-6">
          <div className="text-xs uppercase tracking-[0.3em] text-slate-400">Companies</div>
          <div className="mt-4 space-y-4">
            {data?.companies.map((company) => (
              <Link
                key={company.slug}
                to={`/companies/${company.slug}`}
                className="block rounded-3xl border border-white/10 bg-slate-950/50 p-4"
              >
                <div className="text-xl font-semibold text-white">{company.name}</div>
                <p className="mt-2 text-sm text-slate-300">{company.sector ?? "General business"}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
