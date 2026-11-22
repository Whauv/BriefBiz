interface PreferenceGroupProps {
  title: string;
  options: string[];
  selected: string[];
  onToggle: (option: string) => void;
}

export function PreferenceGroup({ title, options, selected, onToggle }: PreferenceGroupProps) {
  return (
    <section className="mb-6 last:mb-0">
      <div className="text-xs uppercase tracking-[0.3em] text-slate-400">{title}</div>
      <div className="mt-4 flex flex-wrap gap-3">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => onToggle(option)}
            className={`rounded-full border px-4 py-2 text-sm transition ${
              selected.includes(option)
                ? "border-emerald-300/30 bg-emerald-300/15 text-emerald-100"
                : "border-white/10 bg-white/5 text-slate-300"
            }`}
          >
            {option}
          </button>
        ))}
      </div>
    </section>
  );
}
