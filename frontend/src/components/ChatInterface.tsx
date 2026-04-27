import { useEffect, useRef, useState, type FC, type FormEvent, type KeyboardEvent } from "react";
import { runAgent } from "../api/agent";
import MessageBubble, { type Message } from "./MessageBubble";
import type { MemoryEntry } from "../api/agent";

const EXAMPLES = [
  "Draft and send a cold outreach email to ceo@startup.com about my SaaS product",
  "Write a follow-up email to john@company.com after our meeting yesterday",
  "Send a partnership proposal to partner@brand.com from Utkarsh",
  "Show me the last 5 emails I sent",
];

interface Props {
  onMemoryUpdate: (memories: MemoryEntry[]) => void;
}

const ChatInterface: FC<Props> = ({ onMemoryUpdate }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`;
  }, [input]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      text: text.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const res = await runAgent(text.trim());

      // Build agent response text
      const intent = res.output?.intent ?? "unknown";
      const actionCount = res.results?.length ?? 0;
      let agentText = "";

      if (res.status === "review") {
        agentText = `I understand you want to: **${intent}**, but my confidence is too low to act automatically. Please clarify your request.`;
      } else if (actionCount === 0) {
        agentText = `Understood. Intent detected: **${intent}**. No tools were required for this request.`;
      } else {
        const success = res.results.filter((r) => r.status === "success").length;
        agentText = `Completed **${success}/${actionCount}** action${actionCount !== 1 ? "s" : ""} for intent: **${intent}**.`;
      }

      const agentMsg: Message = {
        id: crypto.randomUUID(),
        role: "agent",
        text: agentText,
        timestamp: new Date().toISOString(),
        response: res,
      };

      setMessages((prev) => [...prev, agentMsg]);
      onMemoryUpdate(res.memory_context ?? []);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="chat-area">
      {/* Messages */}
      <div className="messages-list">
        {messages.length === 0 && !loading && (
          <div className="empty-state">
            <div className="empty-state-icon">✉️</div>
            <div className="empty-state-title">Email Outreach Agent</div>
            <div className="empty-state-sub">
              Describe who you want to reach and why — the agent will draft and send the perfect email.
            </div>
            <div className="example-prompts">
              {EXAMPLES.map((ex) => (
                <button key={ex} className="example-prompt-btn" onClick={() => sendMessage(ex)}>
                  {ex}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}

        {loading && (
          <div className="message-row">
            <div className="message-avatar agent">🤖</div>
            <div className="typing-indicator">
              <div className="typing-dot" />
              <div className="typing-dot" />
              <div className="typing-dot" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="error-banner">
          ⚠ {error}
        </div>
      )}

      {/* Input */}
      <div className="input-area">
        <form className="input-form" onSubmit={handleSubmit}>
          <textarea
            ref={textareaRef}
            className="chat-input"
            placeholder="Describe a task… (Enter to send, Shift+Enter for newline)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            rows={1}
          />
          <button className="send-btn" type="submit" disabled={loading || !input.trim()}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </form>
        <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 8, textAlign: "center" }}>
          Tools: generate_email_draft · send_email · list_sent_emails &nbsp;·&nbsp; powered by Ollama
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
