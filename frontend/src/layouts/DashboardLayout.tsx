import { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import { fetchHealth, type HealthResponse } from "../api/agent";
import { Wifi, WifiOff, Database } from "lucide-react";

export default function DashboardLayout() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    const check = async () => {
      try { setHealth(await fetchHealth()); }
      catch { setHealth(null); }
    };
    check();
    const iv = setInterval(check, 15000);
    return () => clearInterval(iv);
  }, []);

  const isOnline = !!health?.ollama_running;

  return (
    <div className="flex h-screen bg-surface-950 overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-56 overflow-hidden">
        {/* Top Bar */}
        <header className="h-14 bg-surface-900/80 backdrop-blur-sm border-b border-surface-700/60 flex items-center justify-between px-6 shrink-0">
          <div className="text-sm text-slate-500">
            AI-powered email outreach platform
          </div>
          <div className="flex items-center gap-4">
            {health && (
              <div className="flex items-center gap-1.5 text-xs text-slate-400">
                <Database className="w-3 h-3" />
                {health.memory_entries ?? 0} memories
              </div>
            )}
            <div className={`flex items-center gap-1.5 text-xs font-medium ${isOnline ? "text-emerald-400" : "text-red-400"}`}>
              {isOnline
                ? <><Wifi className="w-3 h-3" /> {health?.model}</>
                : <><WifiOff className="w-3 h-3" /> Ollama offline</>
              }
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
