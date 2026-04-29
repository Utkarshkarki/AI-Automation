import { useState } from "react";
import MetricsDashboard from "../components/MetricsDashboard";
import type { MemoryEntry } from "../api/agent";
import { Brain } from "lucide-react";

export default function Dashboard() {
  const [memories, setMemories] = useState<MemoryEntry[]>([]);

  return (
    <div className="h-full flex gap-6">
      {/* Left: Metrics */}
      <div className="w-64 shrink-0 space-y-4">
        <div>
          <h2 className="page-title">Dashboard</h2>
          <p className="page-subtitle">Real-time agent performance</p>
        </div>
        <div className="glass-card p-4">
          <MetricsDashboard />
        </div>

        {/* Memory Context */}
        {memories.length > 0 && (
          <div className="glass-card p-4">
            <div className="flex items-center gap-2 mb-3">
              <Brain className="w-3.5 h-3.5 text-brand-400" />
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Memory Context</span>
            </div>
            <div className="space-y-2">
              {memories.slice(0, 3).map((m, i) => (
                <div key={i} className="text-xs text-slate-500 truncate">{m.intent}</div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Right: Activity/Overview */}
      <div className="flex-1 overflow-auto flex flex-col gap-6">
        <div className="glass-card p-6 flex flex-col items-center justify-center h-64 text-center">
          <h3 className="text-xl font-semibold text-slate-200 mb-2">Welcome to PersonaFlow</h3>
          <p className="text-slate-400 max-w-md mx-auto mb-6">
            Your autonomous AI outreach agent is ready. Use the floating chat button in the bottom right to start drafting emails and managing campaigns.
          </p>
        </div>
      </div>
    </div>
  );
}
