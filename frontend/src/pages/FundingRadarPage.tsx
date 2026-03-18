import { useMemo, useState } from "react";

import { StatusPill } from "../components/StatusPill";
import { useFundingRadarData } from "../hooks/useBriefBizData";

const regions = ["All", "US", "Europe", "India", "Africa", "Global"];
const sectors = ["All", "FinTech", "SaaS", "DeepTech", "Consumer"];
const stages = ["All", "Series A", "Series B", "Series C", "IPO", "Acquisition", "Secondary", "Series D"];

export function FundingRadarPage() {
  const { data: articles = [] } = useFundingRadarData();
  const [region, setRegion] = useState("All");
  const [sector, setSector] = useState("All");
  const [stage, setStage] = useState("All");

  const filtered = useMemo(
    () =>
      articles.filter((article) => {
        const matchesRegion = region === "All" || article.region === region;
        const matchesSector = sector === "All" || article.sector === sector;
        const matchesStage = stage === "All" || article.funding_stage === stage;
        return matchesRegion && matchesSector && matchesStage;
      }),
    [articles, region, sector, stage],
  );

  return (
    <div className="space-y-6">
      <section>
        <p className="text-sm uppercase tracking-[0.35em] text-amber-200/80">Funding Radar</p>
        <h1 className="mt-3 text-4xl font-semibold text-white">Where capital is moving this week</h1>
      </section>

      <section className="rounded-[2rem] border border-white/10 bg-white/5 p-5">
        <div className="grid gap-3 md:grid-cols-3">
          <FilterSelect label="Region" options={regions} value={region} onChange={setRegion} />
          <FilterSelect label="Sector" options={sectors} value={sector} onChange={setSector} />
          <FilterSelect label="Stage" options={stages} value={stage} onChange={setStage} />
        </div>
      </section>

      <section className="space-y-4">
        {filtered.map((article) => (
          <article key={article.id} className="rounded-[2rem] border border-white/10 bg-white/5 p-6">
            <div className="flex flex-wrap items-center gap-2">
              <StatusPill tone="tag">{article.region}</StatusPill>
              <StatusPill tone="tag">{article.sector ?? "General"}</StatusPill>
              <StatusPill tone="bullish">{article.funding_stage ?? "Funding"}</StatusPill>
            </div>
            <div className="mt-4 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div>
                <h2 className="text-2xl font-semibold text-white">{article.companies[0]}</h2>
                <p className="mt-2 text-sm uppercase tracking-[0.22em] text-emerald-200">
                  {article.amount ?? "Undisclosed"} • {(article.investor_names ?? []).join(", ")}
                </p>
              </div>
              <div className="text-sm text-slate-400">{new Date(article.published_at).toLocaleDateString()}</div>
            </div>
            <p className="mt-4 max-w-4xl text-base leading-8 text-slate-200">{article.summary_60w}</p>
          </article>
        ))}
      </section>
    </div>
  );
}

interface FilterSelectProps {
  label: string;
  options: string[];
  value: string;
  onChange: (value: string) => void;
}

function FilterSelect({ label, options, value, onChange }: FilterSelectProps) {
  return (
    <label className="rounded-3xl border border-white/10 bg-slate-950/50 p-4">
      <div className="text-xs uppercase tracking-[0.25em] text-slate-400">{label}</div>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-3 w-full bg-transparent text-base text-white outline-none"
      >
        {options.map((option) => (
          <option key={option} value={option} className="bg-slate-950">
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}
