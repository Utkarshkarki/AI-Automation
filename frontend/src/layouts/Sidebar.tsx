import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  Megaphone,
  FileText,
  Mail,
  Zap,
  Bot
} from "lucide-react";

const navItems = [
  { to: "/app", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/app/chat", icon: Bot, label: "Command Center" },
  { to: "/app/leads", icon: Users, label: "Leads" },
  { to: "/app/campaigns", icon: Megaphone, label: "Campaigns" },
  { to: "/app/templates", icon: FileText, label: "Templates" },
];

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-full w-56 bg-surface-900 border-r border-surface-700/60 flex flex-col z-50">
      {/* Brand */}
      <div className="px-4 py-5 border-b border-surface-700/60">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-brand flex items-center justify-center shadow-glow-brand">
            <Mail className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="text-sm font-semibold text-slate-100">PersonaFlow</div>
            <div className="text-xs text-slate-500 font-mono">SaaS Platform</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <div className="text-xs font-semibold text-slate-600 uppercase tracking-widest px-3 mb-3">
          Main Menu
        </div>
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/app"}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
          >
            <Icon className="w-4 h-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-surface-700/60">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Zap className="w-3 h-3 text-brand-400" />
          Powered by Ollama
        </div>
      </div>
    </aside>
  );
}
