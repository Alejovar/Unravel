import { GraphNode } from "@/lib/types";
import { STATUS_LABEL } from "@/lib/visualStyle";
import { hasKnownTime } from "@/lib/time";
import { CloseIcon, ExternalLinkIcon, EyeIcon, ShareIcon, GlobeIcon, OriginIcon } from "@/components/icons";

const BADGE_STYLE: Record<string, { bg: string; fg: string }> = {
  origin: { bg: "#3A3530", fg: "#FFFFFF" },
  confirmed: { bg: "#1F6F6E", fg: "#FFFFFF" },
  developing: { bg: "#C9822E", fg: "#FFFFFF" },
  corrected: { bg: "#B93A3A", fg: "#FFFFFF" },
};

function formatDate(iso: string | null): { date: string; time: string } {
  if (!iso) return { date: "—", time: "—" };
  const d = new Date(iso);
  return {
    date: d.toLocaleDateString("es-MX", { day: "2-digit", month: "short", year: "numeric" }),
    time: hasKnownTime(iso) ? d.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit", hour12: false }) : "—",
  };
}

function formatCount(n: number | null): string {
  if (n === null || n === undefined) return "—";
  if (n >= 1000) return `${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}K`;
  return String(n);
}

const PROVENANCE_TEXT: Record<string, string> = {
  origin: "Primer origen — contenido publicado directamente sin revisión editorial previa detectada.",
  confirmed: "Esta fuente respalda o reproduce la información de una publicación anterior.",
  developing: "La información de esta fuente aún no ha sido confirmada por otras fuentes.",
  corrected: "Esta publicación corrige formalmente una versión anterior de la historia.",
};

export function SourceDetailPanel({ node, onClose }: { node: GraphNode; onClose: () => void }) {
  const { date, time } = formatDate(node.published_at);
  const badge = BADGE_STYLE[node.type] ?? BADGE_STYLE.origin;
  const badgeLabel = node.is_origin ? "Origin" : STATUS_LABEL[node.status] ?? node.status;

  return (
    <aside className="flex h-full w-[340px] shrink-0 flex-col overflow-y-auto border-l border-unravel-border bg-white p-6 shadow-panel scrollbar-thin">
      <div className="mb-5 flex items-center justify-between">
        <span className="text-[10px] font-bold uppercase tracking-widest2 text-unravel-inkSoft/70">
          Source detail
        </span>
        <button
          onClick={onClose}
          className="rounded-full p-1 text-unravel-inkSoft transition hover:bg-unravel-mint hover:text-unravel-teal"
          aria-label="Cerrar"
        >
          <CloseIcon className="h-4 w-4" />
        </button>
      </div>

      <span
        className="mb-5 inline-flex w-fit items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold"
        style={{ backgroundColor: badge.bg, color: badge.fg }}
      >
        <OriginIcon className="h-3 w-3" />
        {badgeLabel}
      </span>

      <div className="mb-5 grid grid-cols-2 gap-3">
        <div className="rounded-xl bg-unravel-cream p-3">
          <p className="text-[10px] font-bold uppercase tracking-widest2 text-unravel-inkSoft/70">Date</p>
          <p className="mt-0.5 text-sm font-semibold text-unravel-ink">{date}</p>
        </div>
        <div className="rounded-xl bg-unravel-cream p-3">
          <p className="text-[10px] font-bold uppercase tracking-widest2 text-unravel-inkSoft/70">Time</p>
          <p className="mt-0.5 text-sm font-semibold text-unravel-ink">{time}</p>
        </div>
      </div>

      <div className="mb-5 space-y-2">
        <p className="text-[10px] font-bold uppercase tracking-widest2 text-unravel-inkSoft/70">Source</p>
        {node.url ? (
          <a
            href={node.url}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 text-sm font-semibold text-unravel-teal hover:underline"
          >
            <GlobeIcon className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">{node.source || node.domain}</span>
            <ExternalLinkIcon className="h-3 w-3 shrink-0" />
          </a>
        ) : (
          <span className="text-sm text-unravel-inkSoft">{node.source || node.domain || "—"}</span>
        )}
        {node.platform && (
          <p className="flex items-center gap-1.5 text-xs text-unravel-inkSoft">
            <GlobeIcon className="h-3 w-3" />
            {node.platform}
          </p>
        )}
      </div>

      {(node.reads !== null || node.shares !== null) && (
      <div className="mb-5 grid grid-cols-2 gap-3">
        {node.reads !== null && (
        <div className="rounded-xl bg-unravel-cream p-3">
          <p className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-widest2 text-unravel-inkSoft/70">
            <EyeIcon className="h-3 w-3" /> Reads
          </p>
          <p className="mt-0.5 text-sm font-semibold text-unravel-ink">{formatCount(node.reads)}</p>
        </div>
        )}
        {node.shares !== null && (
        <div className="rounded-xl bg-unravel-cream p-3">
          <p className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-widest2 text-unravel-inkSoft/70">
            <ShareIcon className="h-3 w-3" /> Shares
          </p>
          <p className="mt-0.5 text-sm font-semibold text-unravel-ink">{formatCount(node.shares)}</p>
        </div>
        )}
      </div>
      )}

      <div className="mb-4">
        <p className="mb-1 text-[10px] font-bold uppercase tracking-widest2 text-unravel-inkSoft/70">Headline</p>
        <p className="text-sm font-bold leading-snug text-unravel-ink">&ldquo;{node.headline}&rdquo;</p>
      </div>

      {node.summary && (
        <div className="mb-5">
          <p className="mb-1 text-[10px] font-bold uppercase tracking-widest2 text-unravel-inkSoft/70">Summary</p>
          <p className="text-xs leading-relaxed text-unravel-inkSoft">{node.summary}</p>
        </div>
      )}

      <div className="mb-5 rounded-xl bg-unravel-cream p-3">
        <p className="mb-1 text-[10px] font-bold uppercase tracking-widest2 text-unravel-inkSoft/70">Provenance</p>
        <p className="text-xs leading-relaxed text-unravel-inkSoft">
          {PROVENANCE_TEXT[node.is_origin ? "origin" : node.type] ?? PROVENANCE_TEXT.developing}
        </p>
      </div>

      {node.url && (
        <a
          href={node.url}
          target="_blank"
          rel="noreferrer"
          className="mt-auto flex items-center gap-1.5 text-sm font-semibold text-unravel-teal hover:underline"
        >
          <ExternalLinkIcon className="h-3.5 w-3.5" />
          View original source
        </a>
      )}
    </aside>
  );
}
