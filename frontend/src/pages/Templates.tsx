import { useEffect, useState } from "react";
import { FileText, Code } from "lucide-react";

const BASE_URL = import.meta.env.PROD ? "/api" : "http://localhost:8000";

interface Template {
  id: number;
  name: string;
  subject: string;
  body: string;
}

export default function Templates() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${BASE_URL}/api/templates`);
        const data = await res.json();
        setTemplates(data.templates ?? []);
      } catch {}
      setLoading(false);
    };
    load();
  }, []);

  const highlight = (text: string) =>
    text.replace(/\{\{(\w+)\}\}/g, '<span class="text-accent-400 font-semibold">{{\$1}}</span>');

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="section-header">
        <div>
          <h1 className="page-title flex items-center gap-2"><FileText className="w-5 h-5 text-brand-400" /> Templates</h1>
          <p className="page-subtitle">Reusable email templates with variable substitution</p>
        </div>
        <div className="text-xs text-slate-500 bg-surface-800 border border-surface-600/50 px-3 py-2 rounded-lg">
          Use <code className="text-accent-400">{"{{name}}"}</code>, <code className="text-accent-400">{"{{company}}"}</code>, <code className="text-accent-400">{"{{industry}}"}</code>
        </div>
      </div>

      {loading ? (
        <div className="text-slate-500 text-sm animate-pulse">Loading templates…</div>
      ) : templates.length === 0 ? (
        <div className="empty-state glass-card">
          <FileText className="w-10 h-10 text-slate-600 mb-3" />
          <p className="text-slate-500 text-sm">No templates yet. Ask the AI to create one in the Dashboard chat.</p>
          <p className="text-xs text-slate-600 mt-2">Try: "Create a template called 'Cold Outreach' with subject 'Hi {"{{name}}"}'"</p>
        </div>
      ) : (
        <div className="space-y-3">
          {templates.map(t => (
            <div key={t.id} className="glass-card overflow-hidden">
              <button
                className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-surface-700/30 transition-colors"
                onClick={() => setExpanded(expanded === t.id ? null : t.id)}
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-brand-600/20 border border-brand-500/30 flex items-center justify-center">
                    <Code className="w-4 h-4 text-brand-400" />
                  </div>
                  <div>
                    <div className="font-medium text-slate-200">{t.name}</div>
                    <div
                      className="text-xs text-slate-400 mt-0.5"
                      dangerouslySetInnerHTML={{ __html: highlight(t.subject) }}
                    />
                  </div>
                </div>
                <span className="text-slate-500 text-xs">{expanded === t.id ? "▲ Hide" : "▼ Preview"}</span>
              </button>
              {expanded === t.id && (
                <div className="px-5 pb-5 border-t border-surface-600/40 pt-4">
                  <div
                    className="text-sm text-slate-400 whitespace-pre-wrap font-mono bg-surface-900 rounded-lg p-4 text-xs leading-relaxed"
                    dangerouslySetInnerHTML={{ __html: highlight(t.body) }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
