import { useState } from "react";

export default function UrlForm({ onCheck, loading }) {
  const [url, setUrl] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    onCheck(url);
  }

  return (
    <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-3 sm:flex-row">
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://example.com/login"
        className="flex-1 rounded-md border border-line px-4 py-3 focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand"
      />
      <button
        type="submit"
        disabled={loading}
        className="rounded-md bg-brand px-6 py-3 font-semibold text-white hover:bg-brand-dark disabled:opacity-60"
      >
        {loading ? "Checking..." : "Check link"}
      </button>
    </form>
  );
}