export type NodeType = "origin" | "unverified" | "confirmed" | "developing" | "corrected";
export type ArticleStatus = "unverified" | "confirmed" | "developing" | "corrected";
export type RelationType =
  | "confirmation"
  | "developing"
  | "correction"
  | "reaction"
  | "update"
  | "republication"
  | "cites"
  | "links_to"
  | "same_story";
export type RelationKind = "observed" | "inferred";

export interface GraphNode {
  id: string;
  type: NodeType;
  label: string;
  source: string | null;
  platform: string | null;
  url: string;
  domain: string;
  published_at: string | null;
  headline: string;
  summary: string | null;
  status: ArticleStatus;
  reads: number | null;
  shares: number | null;
  is_origin: boolean;
  is_latest: boolean;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relation: RelationType;
  kind: RelationKind;
  confidence: number;
  explanation: string | null;
}

export interface GraphSummaryCard {
  key: "origin" | "story_drift" | "latest_state";
  icon: string;
  label: string;
  title: string;
  description: string;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  summary_text: string | null;
  summary_cards: GraphSummaryCard[];
  divergence_count: number;
  sources_count: number;
  edges_count: number;
}

export type AnalysisStatusValue =
  | "queued"
  | "scraping"
  | "discovering"
  | "comparing"
  | "analyzing"
  | "done"
  | "failed";

export interface AnalysisCreateResponse {
  analysis_id: string;
  status: AnalysisStatusValue;
}

export interface AnalysisResultResponse {
  analysis_id: string;
  status: AnalysisStatusValue;
  error: string | null;
  created_at: string;
  updated_at: string;
  graph: GraphResponse | null;
}
