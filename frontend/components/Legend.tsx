const NODE_LEGEND = [
  { label: "Origin", border: "#9C948A", dashed: false, icon: "" },
  { label: "Confirmed", border: "#1F6F6E", dashed: false, icon: "✓" },
  { label: "Developing", border: "#C9822E", dashed: true, icon: "?" },
  { label: "Corrected", border: "#B93A3A", dashed: false, icon: "✕" },
];

const EDGE_LEGEND = [
  { label: "confirmation", color: "#1F6F6E", dashed: false },
  { label: "developing", color: "#C9822E", dashed: true },
  { label: "correction", color: "#B93A3A", dashed: true },
];

export function Legend() {
  return (
    <div className="flex flex-wrap items-center gap-x-6 gap-y-3 border-t border-unravel-border pt-4 text-xs text-unravel-inkSoft">
      <span className="font-semibold uppercase tracking-widest2 text-unravel-inkSoft/70">Legend</span>

      {NODE_LEGEND.map((item) => (
        <span key={item.label} className="flex items-center gap-1.5">
          <span
            className="flex h-4 w-4 items-center justify-center rounded-full bg-white text-[9px] font-bold"
            style={{
              border: `2px ${item.dashed ? "dashed" : "solid"} ${item.border}`,
              color: item.border,
            }}
          >
            {item.icon}
          </span>
          {item.label}
        </span>
      ))}

      <span className="mx-1 h-4 w-px bg-unravel-border" />

      {EDGE_LEGEND.map((item) => (
        <span key={item.label} className="flex items-center gap-1.5">
          <svg width="20" height="8" className="shrink-0">
            <line
              x1="0"
              y1="4"
              x2="20"
              y2="4"
              stroke={item.color}
              strokeWidth="2"
              strokeDasharray={item.dashed ? "4 3" : undefined}
            />
          </svg>
          {item.label}
        </span>
      ))}
    </div>
  );
}
