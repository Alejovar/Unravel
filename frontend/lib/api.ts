import { AnalysisCreateResponse, AnalysisResultResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {}

export async function createAnalysis(queryInput: string): Promise<AnalysisCreateResponse> {
  const res = await fetch(`${API_BASE_URL}/analyses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query_input: queryInput }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new ApiError(detail?.detail || `Could not start the analysis (${res.status})`);
  }
  return res.json();
}

export async function getAnalysis(analysisId: string): Promise<AnalysisResultResponse> {
  const res = await fetch(`${API_BASE_URL}/analyses/${analysisId}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new ApiError(detail?.detail || `Could not fetch the analysis (${res.status})`);
  }
  return res.json();
}
