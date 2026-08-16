import { AnalysisStatusValue } from "@/lib/types";

const STEPS: { key: AnalysisStatusValue; label: string }[] = [
  { key: "queued", label: "Queued" },
  { key: "scraping", label: "Extracting the article" },
  { key: "discovering", label: "Searching for related sources" },
  { key: "comparing", label: "Comparing without an LLM (TF-IDF, BM25, entities)" },
  { key: "analyzing", label: "Analysing claims with AI" },
  { key: "done", label: "Done" },
];

export function AnalysisProgress({ status, queryInput }: { status: AnalysisStatusValue; queryInput: string }) {
  const currentIndex = STEPS.findIndex((s) => s.key === status);

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-8 px-6 text-center">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-unravel-mint border-t-unravel-teal" />
      <div className="max-w-md space-y-1">
        <p className="text-sm font-semibold text-unravel-ink">Tracing the story…</p>
        <p className="truncate text-xs text-unravel-inkSoft">&ldquo;{queryInput}&rdquo;</p>
      </div>
      <ol className="space-y-2 text-left">
        {STEPS.slice(0, 5).map((step, i) => {
          const active = i === currentIndex;
          const done = currentIndex > i;
          return (
            <li
              key={step.key}
              className={`flex items-center gap-2 text-sm ${
                active ? "font-semibold text-unravel-teal" : done ? "text-unravel-inkSoft" : "text-unravel-inkSoft/40"
              }`}
            >
              <span
                className={`h-2 w-2 rounded-full ${
                  active ? "bg-unravel-teal" : done ? "bg-unravel-teal/50" : "bg-unravel-border"
                }`}
              />
              {step.label}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
