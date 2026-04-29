import { Link } from "react-router-dom";
import { ArrowRight, Mail, Zap, Bot } from "lucide-react";

export default function Landing() {
  return (
    <div className="min-h-screen bg-surface-950 text-slate-100 flex flex-col items-center">
      <nav className="w-full max-w-6xl px-6 py-4 flex justify-between items-center border-b border-surface-800">
        <div className="flex items-center gap-2">
          <Bot className="w-8 h-8 text-brand-500" />
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-brand">
            PersonaFlow
          </span>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/login" className="text-sm font-medium hover:text-brand-400 transition-colors">
            Sign In
          </Link>
          <Link to="/register" className="btn-primary">
            Get Started
          </Link>
        </div>
      </nav>

      <main className="w-full max-w-6xl px-6 flex-1 flex flex-col items-center justify-center text-center py-20">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-400 text-sm mb-8 animate-fade-in">
          <Zap className="w-4 h-4" />
          <span>v5.0 Now Available with Llama 3.2</span>
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 animate-slide-up">
          Automate Outreach. <br />
          <span className="bg-clip-text text-transparent bg-gradient-brand">
            Scale Your Pipeline.
          </span>
        </h1>
        
        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mb-10 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          Deploy an autonomous AI agent to research leads, write hyper-personalized emails, 
          and manage drip campaigns seamlessly.
        </p>

        <div className="flex items-center gap-4 animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <Link to="/register" className="btn-primary text-base px-6 py-3 shadow-glow-brand">
            Start Free Trial <ArrowRight className="w-4 h-4 ml-2" />
          </Link>
          <a href="#features" className="btn-secondary text-base px-6 py-3">
            Learn More
          </a>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-6 mt-24 text-left w-full">
          {[
            {
              title: "Autonomous Agents",
              desc: "Give the agent an objective, and it researches, drafts, and schedules automatically.",
              icon: <Bot className="w-6 h-6 text-brand-400" />
            },
            {
              title: "Smart Sequences",
              desc: "Create multi-day follow-up campaigns that pause intelligently on reply.",
              icon: <Zap className="w-6 h-6 text-accent-400" />
            },
            {
              title: "Deliverability Protection",
              desc: "Automated rate limiting and natural delays keep your domain out of spam.",
              icon: <Mail className="w-6 h-6 text-brand-400" />
            }
          ].map((f, i) => (
            <div key={i} className="glass-card p-6 flex flex-col gap-4">
              <div className="w-12 h-12 rounded-lg bg-surface-800 flex items-center justify-center border border-surface-700">
                {f.icon}
              </div>
              <h3 className="text-xl font-semibold">{f.title}</h3>
              <p className="text-slate-400">{f.desc}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
