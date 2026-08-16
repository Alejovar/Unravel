"use client";

import { useState } from "react";
import { HelpIcon, CloseIcon } from "@/components/icons";

export function HelpButton() {
  const [open, setOpen] = useState(false);

  return (
    <div className="fixed bottom-6 right-6 z-20">
      {open && (
        <div className="mb-3 w-72 rounded-2xl border border-unravel-border bg-white p-4 text-xs leading-relaxed text-unravel-inkSoft shadow-panel">
          <p className="mb-2 font-bold text-unravel-ink">¿Cómo leer este grafo?</p>
          <p>
            Cada nodo es una publicación. La posición horizontal indica cuándo apareció. Las líneas
            sólidas son relaciones observadas (citas, enlaces directos); las punteadas son inferidas por
            similitud. Unravel no decide qué es verdadero — te da el contexto para que tú lo hagas.
          </p>
        </div>
      )}
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex h-11 w-11 items-center justify-center rounded-full bg-unravel-ink text-white shadow-panel transition hover:bg-unravel-teal"
        aria-label="Ayuda"
      >
        {open ? <CloseIcon className="h-4 w-4" /> : <HelpIcon className="h-4 w-4" />}
      </button>
    </div>
  );
}
