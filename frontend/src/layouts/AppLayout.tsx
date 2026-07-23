import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { BarChart3, FileText, LayoutDashboard, LogOut, Menu, MessagesSquare, Mic, Search, Sparkles, X } from "lucide-react";
import clsx from "clsx";

import { useAuth } from "@/contexts/AuthContext";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/resumes", label: "My Resume", icon: FileText },
  { to: "/resumes/search", label: "Resume Search", icon: Search },
  { to: "/interviews", label: "Interviews", icon: MessagesSquare },
  { to: "/voice/setup", label: "Voice Interview", icon: Mic },
  { to: "/reports", label: "Reports", icon: BarChart3 },
];

export function AppLayout() {
  const { user, logout } = useAuth();
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-surface-950">
      {/* Desktop sidebar */}
      <aside className="hidden w-64 shrink-0 flex-col border-r border-surface-800 bg-surface-900/60 lg:flex">
        <SidebarContent onNavigate={() => undefined} user={user} onLogout={logout} />
      </aside>

      {/* Mobile nav overlay */}
      {isMobileNavOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={() => setIsMobileNavOpen(false)} />
          <aside className="relative flex h-full w-64 flex-col bg-surface-900 shadow-2xl animate-fade-in">
            <button
              className="absolute right-3 top-3 rounded-lg p-1.5 text-slate-400 hover:bg-surface-800"
              onClick={() => setIsMobileNavOpen(false)}
              aria-label="Close menu"
            >
              <X className="h-5 w-5" />
            </button>
            <SidebarContent onNavigate={() => setIsMobileNavOpen(false)} user={user} onLogout={logout} />
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        {/* Mobile top bar */}
        <header className="flex items-center justify-between border-b border-surface-800 bg-surface-900/60 px-4 py-3 lg:hidden">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-brand-400" />
            <span className="font-semibold text-slate-100">AI Interview Coach</span>
          </div>
          <button
            className="rounded-lg p-2 text-slate-300 hover:bg-surface-800"
            onClick={() => setIsMobileNavOpen(true)}
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5" />
          </button>
        </header>

        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-10 lg:py-8">
          <div className="mx-auto w-full max-w-6xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

function SidebarContent({
  onNavigate,
  user,
  onLogout,
}: {
  onNavigate: () => void;
  user: { full_name: string; email: string } | null;
  onLogout: () => void;
}) {
  return (
    <>
      <div className="flex items-center gap-2 px-6 py-6">
        <Sparkles className="h-6 w-6 text-brand-400" />
        <span className="text-lg font-semibold text-slate-100">AI Interview Coach</span>
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onNavigate}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-brand-500/15 text-brand-300"
                  : "text-slate-400 hover:bg-surface-800 hover:text-slate-100",
              )
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-surface-800 px-3 py-4">
        {user && (
          <div className="mb-3 px-3">
            <p className="truncate text-sm font-medium text-slate-100">{user.full_name}</p>
            <p className="truncate text-xs text-slate-500">{user.email}</p>
          </div>
        )}
        <button
          onClick={onLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400 hover:bg-surface-800 hover:text-red-400"
        >
          <LogOut className="h-4 w-4" />
          Log out
        </button>
      </div>
    </>
  );
}
