import { SearchHero } from "@/components/SearchHero";
import { Logo } from "@/components/Logo";
import { OriginIcon, DriftIcon, CheckShieldIcon } from "@/components/icons";

const STEPS = [
  {
    icon: OriginIcon,
    title: "Paste any story",
    description: "Pega una URL, un titular o una descripción breve de la noticia que quieres investigar.",
  },
  {
    icon: DriftIcon,
    title: "See the trace",
    description: "Unravel reconstruye un News Traceability Graph: quién publicó primero y cómo se propagó.",
  },
  {
    icon: CheckShieldIcon,
    title: "Judge for yourself",
    description: "Revisa fuentes, contradicciones y correcciones. Tú decides qué creer, no el algoritmo.",
  },
];

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center bg-gradient-to-b from-unravel-mint/60 to-[#FAF8F4] px-6">
      <div className="flex w-full max-w-5xl items-center justify-between py-8">
        <Logo />
      </div>

      <div className="flex flex-1 flex-col items-center justify-center gap-8 pb-24 text-center">
        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-widest2 text-unravel-teal">
            Alfabetización mediática e informacional
          </p>
          <h1 className="max-w-2xl text-4xl font-bold leading-tight text-unravel-ink sm:text-5xl">
            Unravel the story <br className="hidden sm:block" /> behind the news.
          </h1>
          <p className="mx-auto max-w-xl text-base text-unravel-inkSoft">
            Descubre cómo apareció una historia, cómo se propagó entre medios y cuentas, y qué cambió
            en el camino — con evidencia observable, no veredictos automáticos.
          </p>
        </div>

        <SearchHero />

        <div className="mt-10 grid w-full max-w-4xl grid-cols-1 gap-4 sm:grid-cols-3">
          {STEPS.map((step) => (
            <div
              key={step.title}
              className="flex flex-col items-center gap-2 rounded-2xl border border-unravel-border bg-white/70 p-5 text-center shadow-card"
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-unravel-mint text-unravel-teal">
                <step.icon className="h-4 w-4" />
              </span>
              <h3 className="text-sm font-semibold text-unravel-ink">{step.title}</h3>
              <p className="text-xs leading-relaxed text-unravel-inkSoft">{step.description}</p>
            </div>
          ))}
        </div>
      </div>

      <footer className="pb-8 text-xs text-unravel-inkSoft/70">
        Youth Hackathon 2026 · Alfabetización Mediática e Informacional (UNESCO)
      </footer>
    </main>
  );
}
