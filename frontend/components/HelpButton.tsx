"use client";

import { useState } from "react";
import { HelpIcon, CloseIcon } from "@/components/icons";

export function HelpButton() {
  const [open, setOpen] = useState(false);

  return (
    <div className="fixed bottom-6 right-6 z-20">
      {open && (
        <div className="mb-3 w-72 rounded-2xl border border-unravel-border bg-white p-4 text-xs leading-relaxed text-unravel-inkSoft shadow-panel">
          <p className="mb-2 font-bold text-unravel-ink">How do I read this graph?</p>
          <p>
            Each node is a publication. Its horizontal position shows when it appeared. Solid lines are
            observed relations (citations, direct links); dashed lines are inferred from similarity.
            Unravel does not decide what is true — it gives you the context so you can decide.
          </p>
        </div>
      )}
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex h-11 w-11 items-center justify-center rounded-full bg-unravel-ink text-white shadow-panel transition hover:bg-unravel-teal"
        aria-label="Help"
      >
        {open ? <CloseIcon className="h-4 w-4" /> : <HelpIcon className="h-4 w-4" />}
      </button>
    </div>
  );
}
