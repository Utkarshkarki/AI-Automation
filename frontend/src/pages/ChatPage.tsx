import { useState } from "react";
import ChatInterface from "../components/ChatInterface";
import type { MemoryEntry } from "../api/agent";

export default function ChatPage() {
  const [_, setMemories] = useState<MemoryEntry[]>([]);

  return (
    <div className="h-full flex flex-col">
      <div className="mb-4">
        <h2 className="page-title">AI Command Center</h2>
        <p className="page-subtitle">Interact with your autonomous outreach agent</p>
      </div>
      
      <div className="flex-1 glass-card overflow-hidden flex flex-col">
        <div className="flex-1 overflow-hidden relative bg-surface-900/50">
          <div className="absolute inset-0">
            <ChatInterface onMemoryUpdate={setMemories} />
          </div>
        </div>
      </div>
    </div>
  );
}
