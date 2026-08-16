export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-baseline gap-2.5 whitespace-nowrap">
      <span className={`font-bold tracking-tight text-unravel-ink ${compact ? "text-xl" : "text-3xl"}`}>
        Unravel
      </span>
      <span className="hidden text-[10px] font-semibold uppercase tracking-widest2 text-unravel-inkSoft sm:inline">
        News Traceability Graph
      </span>
    </div>
  );
}
