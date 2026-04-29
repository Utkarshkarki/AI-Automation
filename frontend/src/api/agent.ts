// API client for the AI Automation Agent backend
// In development: connects directly to FastAPI at localhost:8000
// In production (Docker): Nginx proxies /api/* → backend:8000
const BASE_URL = import.meta.env.PROD ? "/api" : "http://localhost:8000";

export interface Action {
  tool: string;
  params: Record<string, string>;
}

export interface AgentOutput {
  intent: string;
  confidence: number;
  actions: Action[];
  reasoning: string;
}

export interface ToolResult {
  tool: string;
  status: "success" | "fail";
  result?: Record<string, unknown>;
  error?: string;
}

export interface MemoryEntry {
  timestamp: string;
  user_input: string;
  intent: string;
  confidence: number;
  actions: Action[];
  results: { tool: string; status: string }[];
}

export interface RunResponse {
  status: "ok" | "review";
  output: AgentOutput;
  results: ToolResult[];
  memory_context: MemoryEntry[];
}

export interface ToolCounts {
  success?: number;
  fail?: number;
}

export interface MetricsResponse {
  intents: Record<string, number>;
  tools: Record<string, ToolCounts>;
  total_runs: number;
  successful_runs: number;
  success_rate: number;
}

export interface HealthResponse {
  api: string;
  ollama_running: boolean;
  model: string;
  model_available: boolean;
  memory_entries: number;
  available_models?: string[];
  error?: string;
}

export function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem("token");
  if (!token) return { "Content-Type": "application/json" };
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`,
  };
}

export async function runAgent(input: string): Promise<RunResponse> {
  const res = await fetch(`${BASE_URL}/run`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ input }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Agent request failed");
  }
  return res.json();
}

export async function fetchMetrics(): Promise<MetricsResponse> {
  const res = await fetch(`${BASE_URL}/metrics`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error("Failed to fetch metrics");
  return res.json();
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${BASE_URL}/health`); // Health is usually public
  if (!res.ok) throw new Error("Failed to fetch health");
  return res.json();
}

export async function fetchMemory(): Promise<{ count: number; entries: MemoryEntry[] }> {
  const res = await fetch(`${BASE_URL}/memory`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error("Failed to fetch memory");
  return res.json();
}
