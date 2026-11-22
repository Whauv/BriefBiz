import { panelClass } from "./Panel";

interface FollowBoxProps {
  title: string;
  value: string;
  onChange: (value: string) => void;
  items: string[];
  placeholder: string;
  onSubmit: () => void;
}

export function FollowBox({ title, value, onChange, items, placeholder, onSubmit }: FollowBoxProps) {
  return (
    <section className={`${panelClass} p-6`}>
      <div className="text-xs uppercase tracking-[0.3em] text-slate-400">{title}</div>
      <div className="mt-4 flex gap-3">
        <input
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          className="flex-1 rounded-full border border-white/10 bg-slate-950/50 px-4 py-3 text-white outline-none placeholder:text-slate-500"
        />
        <button
          type="button"
          onClick={onSubmit}
          className="rounded-full bg-white px-4 py-3 text-sm font-semibold text-slate-950"
        >
          Add
        </button>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {items.map((item) => (
          <span key={item} className="rounded-full border border-white/10 bg-white/10 px-3 py-2 text-sm text-white">
            {item}
          </span>
        ))}
      </div>
    </section>
  );
}
