import { useState } from "react";
import MetricsDashboard from "../components/MetricsDashboard";
import ChatInterface from "../components/ChatInterface";
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

      {/* Right: Chat */}
      <div className="flex-1 glass-card overflow-hidden flex flex-col">
        <div className="px-5 py-4 border-b border-surface-600/50">
          <h3 className="text-sm font-semibold text-slate-200">AI Outreach Assistant</h3>
          <p className="text-xs text-slate-500 mt-0.5">Chat to manage leads, draft emails, and run campaigns</p>
        </div>
        <div className="flex-1 overflow-hidden">
          <ChatInterface onMemoryUpdate={setMemories} />
        </div>
      </div>
    </div>
  );
}
