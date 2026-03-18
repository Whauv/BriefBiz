import { Link } from "react-router-dom";

import { useFeedData } from "../hooks/useBriefBizData";
import { useAppStore } from "../store/AppStore";

export function BookmarksPage() {
  const { data: articles = [] } = useFeedData();
  const { bookmarks } = useAppStore();
  const savedArticles = articles.filter((article) => bookmarks.includes(article.id));

  return (
    <div className="space-y-6">
      <section>
        <p className="text-sm uppercase tracking-[0.35em] text-emerald-200/80">Bookmarks</p>
        <h1 className="mt-3 text-4xl font-semibold text-white">Your saved strategic stories</h1>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {savedArticles.map((article) => (
          <article key={article.id} className="rounded-[2rem] border border-white/10 bg-white/5 p-5">
            <div className="text-xs uppercase tracking-[0.24em] text-slate-400">{article.source_name}</div>
            <h2 className="mt-3 text-2xl font-semibold text-white">{article.title}</h2>
            <p className="mt-3 text-sm leading-7 text-slate-300">{article.summary_60w}</p>
            <div className="mt-4 flex flex-wrap gap-2">
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
          </article>
        ))}
      </section>
    </div>
  );
}
