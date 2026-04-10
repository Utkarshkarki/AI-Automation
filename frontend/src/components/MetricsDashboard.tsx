import { useEffect, useState, type FC } from "react";
import { fetchMetrics, type MetricsResponse } from "../api/agent";

const MetricsDashboard: FC = () => {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);

  const load = async () => {
    try {
      const m = await fetchMetrics();
      setMetrics(m);
    } catch {
      /* ignore if backend not ready */
    }
  };

  useEffect(() => {
    load();
    const iv = setInterval(load, 5000);
    return () => clearInterval(iv);
  }, []);

  if (!metrics) {
    return <div style={{ color: "var(--text-muted)", fontSize: 12 }}>Loading metrics…</div>;
  }

  const successRate = Math.round(metrics.success_rate * 100);

  return (
    <div>
      {/* Big stats */}
      <div className="stats-grid">
        <div className="stat-box">
          <span className="stat-number">{metrics.total_runs}</span>
          <span className="stat-label">Total Runs</span>
        </div>
        <div className="stat-box">
          <span className="stat-number">{successRate}%</span>
          <span className="stat-label">Success Rate</span>
        </div>
      </div>

      {/* Success rate bar */}
      <div className="progress-bar-wrap">
        <div className="progress-bar-fill" style={{ width: `${successRate}%` }} />
      </div>
      <div style={{ fontSize: 10, color: "var(--text-muted)", marginBottom: 14 }}>
        {metrics.successful_runs} / {metrics.total_runs} successful
      </div>

      {/* Intents */}
      <div className="section-title">Intents Detected</div>
      {Object.keys(metrics.intents).length === 0 ? (
        <div style={{ color: "var(--text-muted)", fontSize: 12 }}>No data yet</div>
      ) : (
        Object.entries(metrics.intents)
          .sort(([, a], [, b]) => b - a)
          .map(([intent, count]) => (
            <div key={intent} className="metric-item">
              <span className="metric-label" style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 11 }}>
                {intent}
              </span>
              <span className="metric-value">{count}</span>
            </div>
          ))
      )}

      {/* Tools */}
      {Object.keys(metrics.tools).length > 0 && (
        <>
          <div className="section-title" style={{ marginTop: 16 }}>Tool Usage</div>
          {Object.entries(metrics.tools).map(([tool, counts]) => (
            <div key={tool} className="metric-item" style={{ flexDirection: "column", alignItems: "flex-start", gap: 4 }}>
              <span className="tool-name">{tool}</span>
              <div style={{ display: "flex", gap: 10 }}>
                <span style={{ fontSize: 11, color: "var(--accent-emerald)" }}>
                  ✓ {counts.success ?? 0}
                </span>
                <span style={{ fontSize: 11, color: "var(--accent-rose)" }}>
                  ✗ {counts.fail ?? 0}
                </span>
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
};

export default MetricsDashboard;
