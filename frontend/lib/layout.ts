import { GraphNode } from "./types";

export interface PositionedNode extends GraphNode {
  x: number;
  y: number;
  lane: number;
  timeValue: number;
}

export interface TimelineTick {
  label: string;
  x: number;
}

const MIN_GAP_PX = 130;
const LANE_HEIGHT = 92;
const TOP_PADDING = 46;
const SIDE_PADDING = 70;

/**
 * Ordena los nodos por fecha de publicación y les asigna una posición X
 * proporcional al tiempo transcurrido, y un "carril" (lane/Y) para evitar
 * que nodos cercanos en el tiempo se encimen — igual que un diagrama de
 * hilos de conversación.
 */
export function computeLayout(
  nodes: GraphNode[],
  containerWidth: number
): { positioned: PositionedNode[]; ticks: TimelineTick[]; height: number } {
  if (nodes.length === 0) {
    return { positioned: [], ticks: [], height: 260 };
  }

  const withTime = nodes.map((n, i) => ({
    node: n,
    time: n.published_at ? new Date(n.published_at).getTime() : NaN,
    fallbackIndex: i,
  }));

  const knownTimes = withTime.filter((n) => !Number.isNaN(n.time)).map((n) => n.time);
  const minTime = knownTimes.length ? Math.min(...knownTimes) : 0;
  const maxTime = knownTimes.length ? Math.max(...knownTimes) : 1;
  const span = Math.max(maxTime - minTime, 1);

  const sorted = [...withTime].sort((a, b) => {
    const ta = Number.isNaN(a.time) ? minTime + a.fallbackIndex * 60000 : a.time;
    const tb = Number.isNaN(b.time) ? minTime + b.fallbackIndex * 60000 : b.time;
    return ta - tb;
  });

  const innerWidth = Math.max(containerWidth - SIDE_PADDING * 2, 320);
  const laneLastX: number[] = [];

  const positioned: PositionedNode[] = sorted.map(({ node, time, fallbackIndex }) => {
    const t = Number.isNaN(time) ? minTime + fallbackIndex * 60000 : time;
    const ratio = span > 0 ? (t - minTime) / span : 0;
    const x = SIDE_PADDING + ratio * innerWidth;

    let lane = 0;
    while (laneLastX[lane] !== undefined && x - laneLastX[lane] < MIN_GAP_PX) {
      lane += 1;
    }
    laneLastX[lane] = x;

    return {
      ...node,
      x,
      y: TOP_PADDING + lane * LANE_HEIGHT,
      lane,
      timeValue: t,
    };
  });

  const tickCount = Math.min(5, positioned.length);
  const ticks: TimelineTick[] = [];
  if (tickCount > 0) {
    const step = positioned.length > 1 ? (positioned.length - 1) / (tickCount - 1 || 1) : 0;
    for (let i = 0; i < tickCount; i++) {
      const idx = Math.round(i * step);
      const p = positioned[Math.min(idx, positioned.length - 1)];
      const date = new Date(p.timeValue);
      const label = Number.isNaN(p.timeValue)
        ? "—"
        : date.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit", hour12: false });
      ticks.push({ label, x: p.x });
    }
  }

  const maxLane = Math.max(...positioned.map((p) => p.lane), 0);
  const height = TOP_PADDING * 2 + maxLane * LANE_HEIGHT + 40;

  return { positioned, ticks, height };
}

export function phaseLabelForRatio(ratio: number): string {
  if (ratio < 0.34) return "ORIGIN";
  if (ratio < 0.7) return "AMPLIFICATION";
  return "RESOLUTION";
}
