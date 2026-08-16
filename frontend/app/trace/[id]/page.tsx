"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import Link from "next/link";
import { ApiError, getAnalysis } from "@/lib/api";
import { AnalysisResultResponse, GraphNode } from "@/lib/types";
import { Logo } from "@/components/Logo";
import { SearchIcon } from "@/components/icons";
import { AnalysisProgress } from "@/components/AnalysisProgress";
import { GraphCanvas } from "@/components/GraphCanvas";
import { Legend } from "@/components/Legend";
import { SummaryCards } from "@/components/SummaryCards";
import { SourceDetailPanel } from "@/components/SourceDetailPanel";
import { HelpButton } from "@/components/HelpButton";

const POLL_INTERVAL_MS = 2500;

export default function TracePage() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const queryInput = searchParams.get("q") || "";

  const [result, setResult] = useState<AnalysisResultResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const data = await getAnalysis(params.id);
        if (cancelled) return;
        setResult(data);
        if (data.status === "done" || data.status === "failed") {
          if (timerRef.current) clearInterval(timerRef.current);
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof ApiError ? err.message : "Could not fetch the analysis.");
        if (timerRef.current) clearInterval(timerRef.current);
      }
    }

    poll();
    timerRef.current = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [params.id]);

  useEffect(() => {
    if (result?.graph?.nodes?.length && !selectedNode) {
      const origin = result.graph.nodes.find((n) => n.is_origin) ?? result.graph.nodes[0];
      setSelectedNode(origin);
    }
  }, [result, selectedNode]);

  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center">
        <Logo />
        <p className="text-sm text-unravel-red">{error}</p>
        <Link href="/" className="text-sm font-semibold text-unravel-teal hover:underline">
          Back to home
        </Link>
      </div>
    );
  }

  if (!result || (result.status !== "done" && result.status !== "failed")) {
    return (
      <div className="flex min-h-screen flex-col bg-[#FAF8F4]">
        <TopBar queryInput={queryInput} stats={null} />
        <AnalysisProgress status={result?.status ?? "queued"} queryInput={queryInput || params.id} />
      </div>
    );
  }

  if (result.status === "failed") {
    return (
      <div className="flex min-h-screen flex-col bg-[#FAF8F4]">
        <TopBar queryInput={queryInput} stats={null} />
        <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-6 text-center">
          <p className="max-w-md text-sm text-unravel-red">
            {result.error || "This story could not be analysed."}
          </p>
          <Link href="/" className="text-sm font-semibold text-unravel-teal hover:underline">
            Try another story
          </Link>
        </div>
      </div>
    );
  }

  const graph = result.graph!;

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[#FAF8F4]">
      <TopBar
        queryInput={queryInput}
        stats={{ sources: graph.sources_count, edges: graph.edges_count }}
      />

      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 overflow-y-auto p-6 scrollbar-thin">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm text-unravel-inkSoft">
              Tracing: <span className="font-bold text-unravel-ink">{queryInput || "story"}</span>
              <span className="mx-2 text-unravel-border">·</span>
              Click any node to inspect
            </p>
            {graph.divergence_count > 0 && (
              <span className="flex items-center gap-1.5 rounded-full bg-unravel-amberSoft px-3 py-1 text-xs font-semibold text-unravel-amber">
                <span className="h-1.5 w-1.5 rounded-full bg-unravel-amber" />
                {graph.divergence_count} divergence{graph.divergence_count !== 1 ? "s" : ""} detected
              </span>
            )}
          </div>

          <div className="rounded-2xl border border-unravel-border bg-unravel-mint/60 p-6">
            <GraphCanvas
              nodes={graph.nodes}
              edges={graph.edges}
              selectedId={selectedNode?.id ?? null}
              onSelect={setSelectedNode}
            />
          </div>

          <div className="mt-4">
            <Legend />
          </div>

          {graph.summary_text && (
            <div className="mt-6 rounded-2xl border border-unravel-border bg-white p-5 shadow-card">
              <p className="mb-2 text-[10px] font-bold uppercase tracking-widest2 text-unravel-inkSoft/70">
                Summary
              </p>
              <p className="text-sm leading-relaxed text-unravel-ink">{graph.summary_text}</p>
            </div>
          )}

          <div className="mt-6">
            <SummaryCards cards={graph.summary_cards} />
          </div>
        </div>

        {selectedNode && <SourceDetailPanel node={selectedNode} onClose={() => setSelectedNode(null)} />}
      </div>
      <HelpButton />
    </div>
  );
}

function TopBar({
  queryInput,
  stats,
}: {
  queryInput: string;
  stats: { sources: number; edges: number } | null;
}) {
  return (
    <header className="flex items-center justify-between gap-4 border-b border-unravel-border bg-white px-6 py-4">
      <Link href="/" className="shrink-0">
        <Logo compact />
      </Link>
      <div className="flex min-w-0 flex-1 items-center gap-2 rounded-full border border-unravel-border bg-unravel-cream px-4 py-2 text-sm text-unravel-inkSoft">
        <SearchIcon className="h-3.5 w-3.5 shrink-0" />
        <span className="truncate">{queryInput}</span>
      </div>
      <div className="hidden shrink-0 items-center gap-1.5 text-xs text-unravel-inkSoft sm:flex">
        {stats ? (
          <>
            <span className="h-1.5 w-1.5 rounded-full bg-unravel-teal" />
            {stats.sources} sources · {stats.edges} edges traced
          </>
        ) : (
          "Analysing…"
        )}
      </div>
    </header>
  );
}
