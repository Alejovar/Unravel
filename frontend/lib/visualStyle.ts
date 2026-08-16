import { NodeType, RelationType } from "./types";

export const NODE_STYLE: Record<
  NodeType,
  { fill: string; border: string; borderStyle: "solid" | "dashed"; icon: string; iconColor: string }
> = {
  origin: { fill: "#FFFFFF", border: "#9C948A", borderStyle: "solid", icon: "", iconColor: "#9C948A" },
  confirmed: { fill: "#FFFFFF", border: "#1F6F6E", borderStyle: "solid", icon: "check", iconColor: "#1F6F6E" },
  developing: { fill: "#FFFFFF", border: "#C9822E", borderStyle: "dashed", icon: "question", iconColor: "#C9822E" },
  corrected: { fill: "#FFFFFF", border: "#B93A3A", borderStyle: "solid", icon: "cross", iconColor: "#B93A3A" },
};

export const RELATION_STYLE: Record<RelationType, { color: string; dashed: boolean; label: string }> = {
  confirmation: { color: "#1F6F6E", dashed: false, label: "confirmation" },
  developing: { color: "#C9822E", dashed: true, label: "developing" },
  correction: { color: "#B93A3A", dashed: true, label: "correction" },
  reaction: { color: "#C9822E", dashed: true, label: "reaction" },
  update: { color: "#1F6F6E", dashed: true, label: "update" },
  republication: { color: "#8A8378", dashed: false, label: "republication" },
  cites: { color: "#8A8378", dashed: false, label: "cites" },
  links_to: { color: "#8A8378", dashed: false, label: "links to" },
  same_story: { color: "#8A8378", dashed: true, label: "same story" },
};

export const STATUS_LABEL: Record<string, string> = {
  unverified: "Unverified",
  confirmed: "Confirmed",
  developing: "Developing",
  corrected: "Corrected",
};
