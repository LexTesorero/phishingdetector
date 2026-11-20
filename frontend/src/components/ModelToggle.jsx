const OPTIONS = [
  { key: "baseline", label: "Baseline (XGBoost)" },
  { key: "enhanced", label: "Enhanced (Full Stack)" },
];

export default function ModelToggle({ value, onChange }) {
  return (
    <div className="mt-6 inline-flex rounded-md border border-line p-1 text-sm">
      {OPTIONS.map((o) => (
        <button
          key={o.key}
          type="button"
          onClick={() => onChange(o.key)}
          className={`rounded px-3 py-1.5 font-medium ${
            value === o.key ? "bg-brand text-white" : "text-muted hover:text-brand"
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}