"use client";

import { useEffect, useRef, useState } from "react";
import type { Core, ElementDefinition } from "cytoscape";
import { GraphEdge, GraphNode } from "@/lib/types";
import { NODE_STYLE, RELATION_STYLE } from "@/lib/visualStyle";
import { ChevronRightIcon } from "@/components/icons";

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedId: string | null;
  onSelect: (node: GraphNode) => void;
}

const NODE_DIAMETER = 56;
const CANVAS_PADDING = 60;
const LABEL_WIDTH = 130;

interface LaidOutNode {
  node: GraphNode;
  x: number;
  y: number;
}

let dagreRegistered = false;

function formatTime(publishedAt: string | null): string {
  if (!publishedAt) return "";
  const date = new Date(publishedAt);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit", hour12: false });
}

export function GraphCanvas({ nodes, edges, selectedId, onSelect }: GraphCanvasProps) {
  const cyContainerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [canvas, setCanvas] = useState<{ nodes: LaidOutNode[]; width: number; height: number }>({
    nodes: [],
    width: 960,
    height: 320,
  });

  useEffect(() => {
    if (!cyContainerRef.current || nodes.length === 0) {
      setCanvas({ nodes: [], width: 960, height: 320 });
      return;
    }
    let cancelled = false;

    (async () => {
      const cytoscape = (await import("cytoscape")).default;
      const dagre = (await import("cytoscape-dagre")).default;
      if (!dagreRegistered) {
        cytoscape.use(dagre as any);
        dagreRegistered = true;
      }
      if (cancelled || !cyContainerRef.current) return;

      const elements: ElementDefinition[] = [
        ...nodes.map((n) => ({
          data: { id: n.id, type: n.type, icon: NODE_STYLE[n.type].icon },
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
        layout: {
          name: "dagre",
          rankDir: "LR",
          nodeSep: 70,
          rankSep: 110,
          edgeSep: 20,
          ranker: "network-simplex",
          padding: CANVAS_PADDING,
          fit: false,
        } as any,
        wheelSensitivity: 0.2,
        minZoom: 1,
        maxZoom: 1,
      });

      cy.on("tap", "node", (evt) => {
        const id = evt.target.id();
        const node = nodes.find((n) => n.id === id);
        if (node) onSelect(node);
      });

      cy.one("layoutstop", () => {
        if (cancelled) return;
        const bb = cy.elements().boundingBox();
        const offsetX = CANVAS_PADDING - bb.x1;
        const offsetY = CANVAS_PADDING - bb.y1;
        cy.nodes().positions((n) => {
          const p = n.position();
          return { x: p.x + offsetX, y: p.y + offsetY };
        });
        cy.pan({ x: 0, y: 0 });
        cy.zoom(1);

        const laidOut: LaidOutNode[] = cy.nodes().map((n) => {
          const node = nodes.find((original) => original.id === n.id())!;
          const p = n.position();
          return { node, x: p.x, y: p.y };
        });
        setCanvas({
          nodes: laidOut,
          width: bb.w + CANVAS_PADDING * 2,
          height: bb.h + CANVAS_PADDING * 2 + 50,
        });
      });

      cyRef.current = cy;
    })();

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodes, edges]);

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
    <div className="relative w-full">
      <div className="overflow-auto pb-2" style={{ maxHeight: 640 }}>
        <div style={{ width: canvas.width, height: canvas.height, position: "relative" }}>
          <div ref={cyContainerRef} className="absolute inset-0" />
          {canvas.nodes.map(({ node: n, x, y }) => (
            <div
              key={n.id}
              className="pointer-events-none absolute flex -translate-x-1/2 flex-col items-center text-center"
              style={{ left: x, top: y - NODE_DIAMETER / 2 - 22, width: LABEL_WIDTH }}
            >
              {formatTime(n.published_at) && (
                <span className="font-mono text-[10px] text-unravel-inkSoft/70">{formatTime(n.published_at)}</span>
              )}
            </div>
          ))}
          {canvas.nodes.map(({ node: n, x, y }) => (
            <div
              key={`${n.id}-label`}
              className="pointer-events-none absolute flex -translate-x-1/2 flex-col items-center text-center"
              style={{ left: x, top: y + NODE_DIAMETER / 2 + 6, width: LABEL_WIDTH }}
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
    </div>
  );
}
