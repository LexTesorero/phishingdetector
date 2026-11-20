import { useState } from "react";
import { checkUrl } from "./api";
import UrlForm from "./components/UrlForm";
import ResultCard from "./components/ResultCard";

const STREAMLIT_URL = "http://localhost:8501";
// Change this in VS Code between "baseline" and "enhanced"
const MODEL = "enhanced";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleCheck(url) {
    if (!url.trim()) {
      setError("Please enter a link to check.");
      return;
    }

    setError("");
    setResult(null);
    setLoading(true);

    try {
      const probability = await checkUrl(url.trim(), MODEL);
      setResult({ url: url.trim(), probability, model: MODEL });
    } catch (err) {
      setError(err.message);
    }

    setLoading(false);
  }

  return (
    <div className="min-h-screen">
      <header className="border-b-4 border-brand">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
          <h1 className="text-xl font-bold text-brand">URL PHISHING DETECTOR</h1>
          <a
            href={STREAMLIT_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-muted hover:text-brand"
          >
            Dashboard
          </a>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-16">
        <h2 className="text-4xl font-bold">Check a link before you click it.</h2>
        <p className="mt-3 text-lg text-muted">
          Paste a web address to see how likely it is to be phishing.
        </p>

        <UrlForm onCheck={handleCheck} loading={loading} />

        {error && <p className="mt-3 font-medium text-brand">{error}</p>}
        {result && (
          <>
            <ResultCard url={result.url} probability={result.probability} />
          </>
        )}
      </main>
    </div>
  );
}