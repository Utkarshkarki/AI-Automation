import type { FC } from "react";
import type { RunResponse } from "../api/agent";
import ConfidenceBadge from "./ConfidenceBadge";
import ToolResultCard from "./ToolResultCard";

export interface Message {
  id: string;
  role: "user" | "agent";
  text: string;
  timestamp: string;
  response?: RunResponse;
}

interface Props {
  message: Message;
}

const MessageBubble: FC<Props> = ({ message }) => {
  const isUser = message.role === "user";
  const res = message.response;
  const output = res?.output;

  const timeStr = new Date(message.timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className={`message-row ${isUser ? "user" : ""}`}>
      {/* Avatar */}
      <div className={`message-avatar ${isUser ? "user" : "agent"}`}>
        {isUser ? "👤" : "🤖"}
      </div>

      {/* Content */}
      <div className="message-content">
        <div className={`message-bubble ${isUser ? "user" : "agent"}`}>
          {message.text}

          {/* Agent reasoning */}
          {!isUser && output?.reasoning && (
            <div className="reasoning-block">{output.reasoning}</div>
          )}

          {/* Review warning */}
          {!isUser && res?.status === "review" && (
            <div className="review-banner">
              ⚠ Low confidence — human review recommended
            </div>
          )}

          {/* Tool results */}
          {!isUser && res?.results && res.results.length > 0 && (
            <ToolResultCard results={res.results} />
          )}
        </div>

        {/* Meta row */}
        <div className="message-meta">
          <span>{timeStr}</span>
          {!isUser && output && (
            <>
              <span className="intent-tag">{output.intent}</span>
              <ConfidenceBadge score={output.confidence} />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
