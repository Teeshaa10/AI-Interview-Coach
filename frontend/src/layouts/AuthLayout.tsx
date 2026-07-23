import type { ReactNode } from "react";
import { Sparkles } from "lucide-react";

export function AuthLayout({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-950 px-4 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-500/15">
            <Sparkles className="h-6 w-6 text-brand-400" />
          </div>
          <h1 className="text-2xl font-semibold text-slate-50">{title}</h1>
          <p className="mt-1.5 text-sm text-slate-400">{subtitle}</p>
        </div>
        <div className="rounded-2xl border border-surface-700 bg-surface-900/60 p-6 shadow-xl backdrop-blur-sm sm:p-8">
          {children}
        </div>
      </div>
    </div>
  );
}
