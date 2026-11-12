function getStatus(probability) {
  if (probability < 0.4) {
    return {
      label: "Safe",
      text: "text-green-700",
      bar: "bg-green-700",
      message: "No strong phishing signals found.",
    };
  }
  if (probability <= 0.8) {
    return {
      label: "Suspicious",
      text: "text-amber-600",
      bar: "bg-amber-600",
      message: "Some signals look risky. Avoid entering personal data.",
    };
  }
  return {
    label: "Potentially harmful",
    text: "text-brand",
    bar: "bg-brand",
    message: "This link looks like phishing. Do not open it.",
  };
}

export default function ResultCard({ url, probability }) {
  const status = getStatus(probability);
  const percent = Math.round(probability * 100);

  return (
    <div className="mt-8 rounded-lg border border-line p-6">
      <p className="break-all text-sm text-muted">{url}</p>

      <p className={`mt-4 text-7xl font-bold ${status.text}`}>{percent}%</p>
      <p className="text-muted">chance of phishing</p>

      <p className={`mt-4 text-xl font-semibold ${status.text}`}>{status.label}</p>
      <p className="text-muted">{status.message}</p>

      <div className="mt-6 h-3 overflow-hidden rounded-full bg-brand-light">
        <div
          className={`h-full transition-all duration-500 ${status.bar}`}
          style={{ width: `${percent}%` }}
        />
      </div>
      <div className="mt-1 flex justify-between text-xs text-muted">
        <span>0%</span>
        <span>Safe below 40%</span>
        <span>Harmful above 80%</span>
        <span>100%</span>
      </div>
    </div>
  );
}