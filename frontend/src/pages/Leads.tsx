import { useEffect, useState } from "react";
import { Users, Search, UploadCloud } from "lucide-react";

const BASE_URL = import.meta.env.PROD ? "/api" : "http://localhost:8000";

interface Contact {
  email: string;
  name?: string;
  company?: string;
  status?: string;
}

export default function Leads() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<string | null>(null);

  const load = async () => {
    try {
      const res = await fetch(`${BASE_URL}/api/contacts`);
      const data = await res.json();
      setContacts(data.contacts ?? []);
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
      load();
    } catch { setUploadMsg("Upload failed."); }
    setUploading(false);
    e.target.value = "";
  };

  const filtered = contacts.filter(c =>
    [c.email, c.name, c.company].some(v => v?.toLowerCase().includes(search.toLowerCase()))
  );

  const statusBadge = (status?: string) => {
    const map: Record<string, string> = {
      lead: "badge-blue", contacted: "badge-yellow", converted: "badge-green", bounced: "badge-red",
    };
    return <span className={map[status ?? "lead"] ?? "badge-gray"}>{status ?? "lead"}</span>;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="section-header">
        <div>
          <h1 className="page-title flex items-center gap-2"><Users className="w-5 h-5 text-brand-400" /> Leads</h1>
          <p className="page-subtitle">{contacts.length} contacts in your CRM</p>
        </div>
        <div className="flex gap-3">
          <label className={`btn-secondary cursor-pointer ${uploading ? "opacity-50 pointer-events-none" : ""}`}>
            <UploadCloud className="w-4 h-4" />
            {uploading ? "Uploading…" : "Upload CSV"}
            <input type="file" accept=".csv" className="hidden" onChange={handleCSVUpload} />
          </label>
        </div>
      </div>

      {uploadMsg && (
        <div className="px-4 py-3 rounded-lg bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 text-sm">
          ✓ {uploadMsg}
        </div>
      )}

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
        <input
          className="input pl-9"
          placeholder="Search by name, email, or company…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm animate-pulse">Loading leads…</div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <Users className="w-10 h-10 text-slate-600 mb-3" />
            <p className="text-slate-500 text-sm">No contacts yet. Upload a CSV or add one via the chat.</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Company</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(c => (
                <tr key={c.email}>
                  <td className="font-medium text-slate-200">{c.name ?? <span className="text-slate-600 italic">—</span>}</td>
                  <td className="font-mono text-xs">{c.email}</td>
                  <td>{c.company ?? <span className="text-slate-600 italic">—</span>}</td>
                  <td>{statusBadge(c.status)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
