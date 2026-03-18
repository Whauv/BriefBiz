import { useParams } from "react-router-dom";

import { StatusPill } from "../components/StatusPill";
import { useCompanyData } from "../hooks/useBriefBizData";

export function CompanyProfilePage() {
  const { slug } = useParams();
  const { data: company, isLoading } = useCompanyData(slug);

  if (isLoading || !company) {
    return (
      <section className="rounded-[2rem] border border-white/10 bg-white/5 p-8 text-slate-300">
        Loading company profile...
      </section>
    );
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[2rem] border border-white/10 bg-white/5 p-6">
        <div className="flex flex-wrap items-center gap-2">
          <StatusPill tone="tag">{company.sector}</StatusPill>
          <StatusPill tone="tag">{company.funding_stage}</StatusPill>
          <StatusPill tone="tag">{company.hq_country}</StatusPill>
        </div>
        <h1 className="mt-4 text-4xl font-semibold text-white">{company.name}</h1>
        <p className="mt-3 max-w-2xl text-base leading-8 text-slate-300">
          {company.name} appears in {company.article_count} recent BriefBiz stories. Investors following this company
          should watch how its category narrative evolves across funding, regulatory, and platform shifts.
        </p>

        <div className="mt-6 flex flex-wrap gap-2">
          {company.investors.map((investor) => (
            <span key={investor} className="rounded-full border border-white/10 bg-white/10 px-3 py-2 text-sm text-white">
              {investor}
            </span>
          ))}
        </div>
      </section>

      <section className="space-y-4">
        {company.articles.map((article) => (
          <article key={article.id} className="rounded-[2rem] border border-white/10 bg-white/5 p-6">
            <div className="text-xs uppercase tracking-[0.24em] text-slate-400">
              {new Date(article.published_at).toLocaleDateString()}
            </div>
            <h2 className="mt-3 text-2xl font-semibold text-white">{article.title}</h2>
            <p className="mt-3 text-sm leading-7 text-slate-300">{article.summary_60w}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
