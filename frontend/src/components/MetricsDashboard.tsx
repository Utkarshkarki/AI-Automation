import { useEffect, useState } from "react";
import { fetchMetrics, type MetricsResponse } from "../api/agent";
import { Activity, TrendingUp } from "lucide-react";

export default function MetricsDashboard() {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);

  useEffect(() => {
    const load = async () => {
      try { setMetrics(await fetchMetrics()); } catch {}
    };
    load();
    const iv = setInterval(load, 5000);
    return () => clearInterval(iv);
  }, []);

  if (!metrics) return (
    <div className="text-xs text-slate-500 animate-pulse">Loading metrics…</div>
  );

  const successRate = Math.round(metrics.success_rate * 100);

  return (
    <div className="space-y-4">
      {/* Stat Cards */}
      <div className="grid grid-cols-2 gap-3">
        <div className="stat-card">
          <div className="flex items-center gap-1.5 mb-1">
            <Activity className="w-3 h-3 text-brand-400" />
            <span className="text-xs text-slate-500">Total Runs</span>
          </div>
          <div className="text-2xl font-bold text-slate-100">{metrics.total_runs}</div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-1.5 mb-1">
            <TrendingUp className="w-3 h-3 text-emerald-400" />
            <span className="text-xs text-slate-500">Success</span>
          </div>
          <div className="text-2xl font-bold text-emerald-400">{successRate}%</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div>
        <div className="flex justify-between text-xs text-slate-500 mb-1.5">
          <span>Success Rate</span>
          <span>{metrics.successful_runs}/{metrics.total_runs}</span>
        </div>
        <div className="h-1.5 bg-surface-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-brand-500 to-accent-400 rounded-full transition-all duration-700"
            style={{ width: `${successRate}%` }}
          />
        </div>
      </div>

      {/* Intents */}
      {Object.keys(metrics.intents).length > 0 && (
        <div>
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Intents</div>
          <div className="space-y-1.5">
            {Object.entries(metrics.intents).sort(([,a],[,b]) => b-a).map(([intent, count]) => (
              <div key={intent} className="flex items-center justify-between">
                <span className="text-xs text-slate-400 font-mono truncate">{intent}</span>
                <span className="text-xs text-brand-400 font-medium ml-2">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tools */}
      {Object.keys(metrics.tools).length > 0 && (
        <div>
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Tools</div>
          <div className="space-y-1.5">
            {Object.entries(metrics.tools).map(([tool, counts]) => (
              <div key={tool} className="glass-card px-3 py-2">
                <div className="text-xs text-slate-300 font-medium mb-1">{tool}</div>
                <div className="flex gap-3 text-xs">
                  <span className="text-emerald-400">✓ {counts.success ?? 0}</span>
                  <span className="text-red-400">✗ {counts.fail ?? 0}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
