import { useState } from "react";
import { MessageSquare, X } from "lucide-react";
import ChatInterface from "./ChatInterface";

export default function ChatButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-brand-600 hover:bg-brand-500 text-white shadow-glow-brand flex items-center justify-center transition-all z-50 hover:scale-105 active:scale-95"
      >
        {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
      </button>

      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[600px] max-h-[80vh] flex flex-col z-50 animate-slide-up origin-bottom-right">
          <div className="glass-card shadow-card flex-1 flex flex-col overflow-hidden">
            <div className="p-4 border-b border-surface-700/60 bg-surface-800 flex items-center justify-between">
              <h3 className="font-semibold text-slate-100 flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-brand-400" />
                AI Assistant
              </h3>
            </div>
            <div className="flex-1 overflow-hidden relative bg-surface-900/50">
              <div className="absolute inset-0">
                <ChatInterface />
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
