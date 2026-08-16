"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, createAnalysis } from "@/lib/api";
import { SearchIcon } from "@/components/icons";

export function SearchHero() {
  const router = useRouter();
  const [value, setValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = value.trim();
    if (trimmed.length < 3) {
      setError("Paste a URL, a headline, or a short description.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const { analysis_id } = await createAnalysis(trimmed);
      router.push(`/trace/${analysis_id}?q=${encodeURIComponent(trimmed)}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "An unexpected error occurred.");
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl">
      <div className="flex items-center gap-2 rounded-full border border-unravel-border bg-white px-5 py-3 shadow-card focus-within:border-unravel-teal">
        <SearchIcon className="h-4 w-4 shrink-0 text-unravel-inkSoft" />
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="https://outlet.com/story — or paste a headline, or a short description"
          className="w-full bg-transparent text-sm text-unravel-ink placeholder:text-unravel-inkSoft/70 focus:outline-none"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading}
          className="shrink-0 rounded-full bg-unravel-teal px-5 py-2 text-sm font-semibold text-white transition hover:bg-unravel-tealDark disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Analysing…" : "Trace it"}
        </button>
      </div>
      {error && <p className="mt-3 text-center text-sm text-unravel-red">{error}</p>}
    </form>
  );
}
