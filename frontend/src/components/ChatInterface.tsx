import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { runAgent } from "../api/agent";
import MessageBubble, { type Message } from "./MessageBubble";
import type { MemoryEntry } from "../api/agent";
import { Send, Bot } from "lucide-react";

const EXAMPLES = [
  "Add Alice from TechCorp (alice@techcorp.com). Industry: SaaS. Pain point: churn is too high.",
  "Draft an email to alice@techcorp.com pitching our retention analytics tool.",
  "Create a template called 'Cold Outreach' with subject 'Hi {{name}}' and a body about {{company}}.",
  "Show me the last 5 emails I sent",
];

interface Props {
  onMemoryUpdate: (memories: MemoryEntry[]) => void;
}

export default function ChatInterface({ onMemoryUpdate }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`;
  }, [input]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", text: text.trim(), timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError(null);
    try {
      const res = await runAgent(text.trim());
      const intent = res.output?.intent ?? "unknown";
      const actionCount = res.results?.length ?? 0;
      let agentText = "";
      if (res.status === "review") {
        agentText = `I understand you want to: **${intent}**, but my confidence is too low to act automatically. Please clarify.`;
      } else if (actionCount === 0) {
        agentText = `Understood. Intent detected: **${intent}**. No tools required.`;
      } else {
        const success = res.results.filter(r => r.status === "success").length;
        agentText = `Completed **${success}/${actionCount}** action${actionCount !== 1 ? "s" : ""} for intent: **${intent}**.`;
      }
      const agentMsg: Message = { id: crypto.randomUUID(), role: "agent", text: agentText, timestamp: new Date().toISOString(), response: res };
      setMessages(prev => [...prev, agentMsg]);
      onMemoryUpdate(res.memory_context ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: FormEvent) => { e.preventDefault(); sendMessage(input); };
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(input); }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-2 py-4 space-y-4">
        {messages.length === 0 && !loading && (
          <div className="empty-state animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-gradient-brand flex items-center justify-center shadow-glow-brand mx-auto mb-4">
              <Bot className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-lg font-semibold text-slate-200 mb-1">AI Outreach Assistant</h2>
            <p className="text-sm text-slate-500 max-w-sm mb-6">
              Add leads, draft hyper-personalized emails, and manage campaigns — all by just describing what you need.
            </p>
            <div className="grid grid-cols-1 gap-2 w-full max-w-md">
              {EXAMPLES.map(ex => (
                <button
                  key={ex}
                  onClick={() => sendMessage(ex)}
                  className="text-left px-4 py-3 rounded-lg border border-surface-600/60 bg-surface-800/50 
                             hover:bg-surface-700/60 hover:border-brand-500/40 text-sm text-slate-400 
                             hover:text-slate-200 transition-all duration-200"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map(m => <MessageBubble key={m.id} message={m} />)}

        {loading && (
          <div className="flex items-center gap-3 px-4 animate-fade-in">
            <div className="w-8 h-8 rounded-full bg-brand-600/30 border border-brand-500/30 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 text-brand-400" />
            </div>
            <div className="flex gap-1.5">
              {[0, 1, 2].map(i => (
                <div key={i} className="w-2 h-2 rounded-full bg-brand-400 animate-bounce"
                  style={{ animationDelay: `${i * 0.15}s` }} />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="mx-4 mb-3 px-4 py-2.5 rounded-lg bg-red-500/10 border border-red-500/25 text-red-400 text-sm">
          ⚠ {error}
        </div>
      )}

      {/* Input */}
      <div className="border-t border-surface-700/60 p-4">
        <form onSubmit={handleSubmit} className="flex gap-3 items-end">
          <textarea
            ref={textareaRef}
            className="flex-1 input min-h-[44px] max-h-[120px] resize-none py-2.5"
            placeholder="Describe a task… (Enter to send, Shift+Enter for newline)"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            rows={1}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="w-11 h-11 rounded-lg bg-brand-600 hover:bg-brand-500 disabled:opacity-40 
                       disabled:cursor-not-allowed flex items-center justify-center
                       transition-all duration-200 shadow-glow-brand shrink-0"
          >
            <Send className="w-4 h-4 text-white" />
          </button>
        </form>
        <p className="text-xs text-slate-600 mt-2 text-center">
          add_contact · generate_email_draft · send_email · create_template · start_campaign · powered by Ollama
        </p>
      </div>
    </div>
  );
}
