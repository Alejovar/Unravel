"use client";

import { useEffect, useRef, useState } from "react";
import type { Core, ElementDefinition } from "cytoscape";
import { GraphEdge, GraphNode } from "@/lib/types";
import { computeLayout, phaseLabelForRatio, PositionedNode } from "@/lib/layout";
import { NODE_STYLE, RELATION_STYLE } from "@/lib/visualStyle";
import { ChevronRightIcon } from "@/components/icons";

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedId: string | null;
  onSelect: (node: GraphNode) => void;
}

const NODE_DIAMETER = 56;

export function GraphCanvas({ nodes, edges, selectedId, onSelect }: GraphCanvasProps) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const cyContainerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [width, setWidth] = useState(960);
  const [layout, setLayout] = useState<{
    positioned: PositionedNode[];
    ticks: { label: string; x: number }[];
    height: number;
  }>({ positioned: [], ticks: [], height: 320 });

  useEffect(() => {
    if (!wrapperRef.current) return;
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setWidth(Math.max(entry.contentRect.width, 320));
      }
    });
    observer.observe(wrapperRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    setLayout(computeLayout(nodes, width));
  }, [nodes, width]);

  useEffect(() => {
    if (!cyContainerRef.current || layout.positioned.length === 0) return;
    let cancelled = false;

    (async () => {
      const cytoscape = (await import("cytoscape")).default;
      if (cancelled || !cyContainerRef.current) return;

      const elements: ElementDefinition[] = [
        ...layout.positioned.map((n) => ({
          data: { id: n.id, type: n.type, icon: NODE_STYLE[n.type].icon },
          position: { x: n.x, y: n.y },
        })),
        ...edges.map((e) => ({
          data: {
            id: e.id,
            source: e.source,
            target: e.target,
            label: RELATION_STYLE[e.relation]?.label ?? e.relation,
            relation: e.relation,
          },
        })),
      ];

      if (cyRef.current) {
        cyRef.current.destroy();
      }

      const cy = cytoscape({
        container: cyContainerRef.current,
        elements,
        userZoomingEnabled: false,
        userPanningEnabled: false,
        boxSelectionEnabled: false,
        autoungrabify: true,
        style: [
          {
            selector: "node",
            style: {
              width: NODE_DIAMETER,
              height: NODE_DIAMETER,
              "background-color": (ele: any) => NODE_STYLE[ele.data("type") as GraphNode["type"]].fill,
              "border-width": 3,
              "border-color": (ele: any) => NODE_STYLE[ele.data("type") as GraphNode["type"]].border,
              "border-style": (ele: any) => NODE_STYLE[ele.data("type") as GraphNode["type"]].borderStyle,
              label: (ele: any) => {
                const icon = ele.data("icon");
                return icon === "check" ? "✓" : icon === "question" ? "?" : icon === "cross" ? "✕" : "";
              },
              color: (ele: any) => NODE_STYLE[ele.data("type") as GraphNode["type"]].iconColor,
              "font-size": 20,
              "font-weight": 700,
              "text-valign": "center",
              "text-halign": "center",
            },
          },
          {
            selector: "node:selected",
            style: {
              "border-width": 5,
              "overlay-color": "#1F6F6E",
              "overlay-opacity": 0.12,
              "overlay-padding": 6,
            },
          },
          {
            selector: "edge",
            style: {
              width: 2,
              "curve-style": "bezier",
              "target-arrow-shape": "triangle",
              "target-arrow-color": (ele: any) => RELATION_STYLE[ele.data("relation") as GraphEdge["relation"]]?.color ?? "#8A8378",
              "line-color": (ele: any) => RELATION_STYLE[ele.data("relation") as GraphEdge["relation"]]?.color ?? "#8A8378",
              "line-style": (ele: any) => (RELATION_STYLE[ele.data("relation") as GraphEdge["relation"]]?.dashed ? "dashed" : "solid"),
              "line-dash-pattern": [5, 4],
              label: "data(label)",
              "font-size": 10,
              "font-weight": 600,
              color: "#3A3530",
              "text-background-color": "#FFFFFF",
              "text-background-opacity": 1,
              "text-background-shape": "roundrectangle",
              "text-background-padding": "4px",
              "text-border-width": 1,
              "text-border-color": "#E4DFD5",
              "text-border-opacity": 1,
              "text-rotation": "autorotate",
              "arrow-scale": 1,
            },
          },
        ],
        layout: { name: "preset" },
        wheelSensitivity: 0.2,
        minZoom: 1,
        maxZoom: 1,
      });

      cy.zoom(1);
      cy.pan({ x: 0, y: 0 });

      cy.on("tap", "node", (evt) => {
        const id = evt.target.id();
        const node = nodes.find((n) => n.id === id);
        if (node) onSelect(node);
      });

      cyRef.current = cy;
    })();

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [layout.positioned, edges]);

  useEffect(() => {
    if (!cyRef.current) return;
    cyRef.current.nodes().unselect();
    if (selectedId) {
      cyRef.current.getElementById(selectedId).select();
    }
  }, [selectedId]);

  useEffect(() => {
    return () => {
      cyRef.current?.destroy();
    };
  }, []);

  return (
    <div ref={wrapperRef} className="relative w-full">
      {/* Eje de tiempo */}
      <div className="relative mb-1 h-10 select-none">
        {layout.ticks.map((tick, i) => {
          const ratio = layout.ticks.length > 1 ? i / (layout.ticks.length - 1) : 0;
          return (
            <div
              key={`${tick.label}-${i}`}
              className="absolute top-0 flex -translate-x-1/2 flex-col items-center gap-1"
              style={{ left: tick.x }}
            >
              <span className="text-[10px] font-semibold uppercase tracking-widest2 text-unravel-inkSoft/70">
                {phaseLabelForRatio(ratio)}
              </span>
              <span className="font-mono text-[11px] text-unravel-inkSoft">{tick.label}</span>
            </div>
          );
        })}
        <div className="absolute bottom-0 left-0 right-0 border-t border-dashed border-unravel-border" />
      </div>

      {/* Lienzo del grafo */}
      <div className="relative" style={{ height: layout.height }}>
        <div ref={cyContainerRef} className="absolute inset-0" />
        {layout.positioned.map((n) => (
          <div
            key={n.id}
            className="pointer-events-none absolute flex -translate-x-1/2 flex-col items-center text-center"
            style={{ left: n.x, top: n.y + NODE_DIAMETER / 2 + 6, width: 130 }}
          >
            <span className="truncate text-xs font-bold text-unravel-ink">{n.label}</span>
            {n.source && <span className="truncate text-[10px] text-unravel-inkSoft">{n.source}</span>}
            {n.is_latest && (
              <span className="mt-1 flex items-center gap-0.5 rounded-full bg-unravel-mint px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide text-unravel-teal">
                <ChevronRightIcon className="h-2.5 w-2.5" />
                Latest
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
