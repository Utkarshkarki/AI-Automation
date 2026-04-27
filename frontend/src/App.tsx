import { useEffect, useState } from "react";
import "./index.css";
import ChatInterface from "./components/ChatInterface";
import MetricsDashboard from "./components/MetricsDashboard";
import MemoryPanel from "./components/MemoryPanel";
import { fetchHealth, type HealthResponse, type MemoryEntry } from "./api/agent";

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [currentMemory, setCurrentMemory] = useState<MemoryEntry[]>([]);

  useEffect(() => {
    const check = async () => {
      try {
        const h = await fetchHealth();
        setHealth(h);
      } catch {
        setHealth(null);
      }
    };
    check();
    const iv = setInterval(check, 15000);
    return () => clearInterval(iv);
  }, []);

  const isOnline = !!health?.ollama_running;

  return (
    <div className="app-shell">
      {/* Header */}
      <header className="header">
        <div className="header-brand">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="url(#grad)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <defs>
              <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#38bdf8" />
                <stop offset="100%" stopColor="#818cf8" />
              </linearGradient>
            </defs>
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
            <polyline points="22,6 12,13 2,6" />
          </svg>
          Email Outreach Agent &nbsp;
          <span style={{ fontWeight: 300, color: "var(--text-muted)", fontSize: 12 }}>v5.0</span>
        </div>

        <div className="header-status">
          <div className={`status-dot ${isOnline ? "" : "offline"}`} />
          {health
            ? isOnline
              ? `Ollama · ${health.model} · ${health.memory_entries ?? 0} memories`
              : "Ollama offline — run: ollama serve"
            : "Connecting…"}
        </div>
      </header>

      {/* Left sidebar — Metrics */}
      <aside className="sidebar">
        <div className="section-title">📊 Metrics</div>
        <MetricsDashboard />
      </aside>

      {/* Center — Chat */}
      <ChatInterface onMemoryUpdate={setCurrentMemory} />

      {/* Right panel — Memory */}
      <aside className="right-panel">
        <div className="section-title">🧠 Memory Context</div>
        <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 12 }}>
          Memories used in the last response
        </div>
        <MemoryPanel memories={currentMemory} />
      </aside>
    </div>
  );
}
