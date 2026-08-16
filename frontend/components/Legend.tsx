import { NODE_STYLE, RELATION_STYLE, NODE_LABEL, ICON_CHAR } from "@/lib/visualStyle";

export function Legend() {
  const nodeEntries = Object.entries(NODE_STYLE) as [keyof typeof NODE_STYLE, (typeof NODE_STYLE)[keyof typeof NODE_STYLE]][];
  const edgeEntries = Object.entries(RELATION_STYLE) as [keyof typeof RELATION_STYLE, (typeof RELATION_STYLE)[keyof typeof RELATION_STYLE]][];

  return (
    <div className="flex flex-wrap items-center gap-x-6 gap-y-3 border-t border-unravel-border pt-4 text-xs text-unravel-inkSoft">
      <span className="font-semibold uppercase tracking-widest2 text-unravel-inkSoft/70">Legend</span>

      {nodeEntries.map(([type, style]) => (
        <span key={type} className="flex items-center gap-1.5">
          <span
            className="flex h-4 w-4 items-center justify-center rounded-full bg-white text-[9px] font-bold"
            style={{
              border: `2px ${style.borderStyle} ${style.border}`,
              color: style.iconColor,
            }}
          >
            {ICON_CHAR[style.icon] ?? ""}
          </span>
          {NODE_LABEL[type]}
        </span>
      ))}

      <span className="mx-1 h-4 w-px bg-unravel-border" />

      {edgeEntries.map(([relation, style]) => (
        <span key={relation} className="flex items-center gap-1.5">
          <svg width="20" height="8" className="shrink-0">
            <line
              x1="0"
              y1="4"
              x2="20"
              y2="4"
              stroke={style.color}
              strokeWidth="2"
              strokeDasharray={style.dashed ? "4 3" : undefined}
            />
          </svg>
          {style.label}
        </span>
      ))}
    </div>
  );
}
