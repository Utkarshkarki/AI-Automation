import type { FC } from "react";
import type { MemoryEntry } from "../api/agent";

interface Props {
  memories: MemoryEntry[];
}

const MemoryPanel: FC<Props> = ({ memories }) => {
  if (!memories.length) {
    return (
      <div style={{ color: "var(--text-muted)", fontSize: 12, textAlign: "center", padding: "16px 0" }}>
        No memory context used
      </div>
    );
  }

  return (
    <div>
      {memories.map((m, i) => (
        <div key={i} className="memory-entry">
          <div className="memory-input">"{m.user_input}"</div>
          <div className="memory-meta">
            <span style={{ color: "var(--accent-indigo)" }}>{m.intent}</span>
            {" · "}
            {new Date(m.timestamp).toLocaleTimeString()}
          </div>
        </div>
      ))}
    </div>
  );
};

export default MemoryPanel;
