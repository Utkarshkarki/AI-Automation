import { useState, type FC } from "react";
import type { ToolResult } from "../api/agent";

interface Props {
  results: ToolResult[];
}

const ToolResultCard: FC<Props> = ({ results }) => {
  const [open, setOpen] = useState<Record<number, boolean>>({});

  if (!results.length) return null;

  const toggle = (i: number) =>
    setOpen((prev) => ({ ...prev, [i]: !prev[i] }));

  return (
    <div style={{ marginTop: 10 }}>
      {results.map((r, i) => (
        <div key={i} className="tool-card">
          <div className="tool-card-header" onClick={() => toggle(i)}>
            <span className="tool-name">⚙ {r.tool}</span>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span className={r.status === "success" ? "tool-status-success" : "tool-status-fail"}>
                {r.status === "success" ? "✓ success" : "✗ failed"}
              </span>
              <span style={{ color: "var(--text-muted)", fontSize: 10 }}>
                {open[i] ? "▲" : "▼"}
              </span>
            </div>
          </div>
          {open[i] && (
            <div className="tool-card-body">
              {r.result
                ? JSON.stringify(r.result, null, 2)
                : r.error ?? "No output"}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ToolResultCard;
