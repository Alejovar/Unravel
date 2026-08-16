import { GraphSummaryCard } from "@/lib/types";
import { OriginIcon, DriftIcon, CheckShieldIcon } from "@/components/icons";

const ICONS: Record<string, typeof OriginIcon> = {
  origin: OriginIcon,
  drift: DriftIcon,
  latest: CheckShieldIcon,
};

export function SummaryCards({ cards }: { cards: GraphSummaryCard[] }) {
  if (!cards.length) return null;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      {cards.map((card) => {
        const Icon = ICONS[card.icon] ?? OriginIcon;
        return (
          <div key={card.key} className="rounded-2xl border border-unravel-border bg-white p-4 shadow-card">
            <div className="mb-2 flex items-center gap-1.5 text-unravel-teal">
              <Icon className="h-3.5 w-3.5" />
              <span className="text-[10px] font-bold uppercase tracking-widest2 text-unravel-inkSoft/70">
                {card.label}
              </span>
            </div>
            <h3 className="text-sm font-bold text-unravel-ink">{card.title}</h3>
            <p className="mt-1 text-xs leading-relaxed text-unravel-inkSoft">{card.description}</p>
          </div>
        );
      })}
    </div>
  );
}
