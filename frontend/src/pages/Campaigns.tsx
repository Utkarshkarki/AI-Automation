import { useEffect, useState } from "react";
import { Megaphone, UploadCloud, Calendar } from "lucide-react";

const BASE_URL = import.meta.env.PROD ? "/api" : "http://localhost:8000";

interface Campaign {
  id: number;
  name: string;
  description?: string;
  created_at?: string;
}

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<string | null>(null);

  const load = async () => {
    try {
      const res = await fetch(`${BASE_URL}/api/campaigns`);
      const data = await res.json();
      setCampaigns(data.campaigns ?? []);
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const handleCSVUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadMsg(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(`${BASE_URL}/api/leads/upload`, { method: "POST", body: formData });
      const data = await res.json();
      setUploadMsg(data.message);
    } catch { setUploadMsg("Upload failed."); }
    setUploading(false);
    e.target.value = "";
  };

  const formatDate = (iso?: string) => {
    if (!iso) return "—";
    return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="section-header">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Megaphone className="w-5 h-5 text-brand-400" /> Campaigns
          </h1>
          <p className="page-subtitle">Manage and track your outreach campaigns</p>
        </div>
        <label className={`btn-secondary cursor-pointer ${uploading ? "opacity-50 pointer-events-none" : ""}`}>
          <UploadCloud className="w-4 h-4" />
          {uploading ? "Uploading…" : "Bulk Upload Leads (CSV)"}
          <input type="file" accept=".csv" className="hidden" onChange={handleCSVUpload} />
        </label>
      </div>

      {uploadMsg && (
        <div className="px-4 py-3 rounded-lg bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 text-sm">
          ✓ {uploadMsg} — Go to Leads to view them.
        </div>
      )}

      {/* CSV format hint */}
      <div className="glass-card p-4 text-xs text-slate-500 space-y-1">
        <p className="font-semibold text-slate-400 mb-2">📋 CSV Format (columns):</p>
        <code className="text-accent-400">email, name, company, industry, pain_points, recent_news, website, linkedin</code>
        <p className="mt-2">After uploading, go to the Dashboard chat and say: "Start the [campaign name] campaign using Template #1 for all leads."</p>
      </div>

      {/* Campaign Cards */}
      {loading ? (
        <div className="text-slate-500 text-sm animate-pulse">Loading campaigns…</div>
      ) : campaigns.length === 0 ? (
        <div className="empty-state glass-card">
          <Megaphone className="w-10 h-10 text-slate-600 mb-3" />
          <p className="text-slate-500 text-sm">No campaigns yet.</p>
          <p className="text-xs text-slate-600 mt-2">Ask the AI: "Create a campaign called 'Q3 SaaS Outreach'"</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {campaigns.map(c => (
            <div key={c.id} className="glass-card p-5 flex flex-col gap-3 hover:border-brand-500/30 transition-colors">
              <div className="flex items-start justify-between">
                <div className="w-10 h-10 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center">
                  <Megaphone className="w-5 h-5 text-brand-400" />
                </div>
                <span className="badge-blue">Active</span>
              </div>
              <div>
                <h3 className="font-semibold text-slate-200">{c.name}</h3>
                {c.description && <p className="text-xs text-slate-500 mt-1">{c.description}</p>}
              </div>
              <div className="flex items-center gap-1.5 text-xs text-slate-600 mt-auto pt-2 border-t border-surface-600/40">
                <Calendar className="w-3 h-3" />
                Created {formatDate(c.created_at)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
