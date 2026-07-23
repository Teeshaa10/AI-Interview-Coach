import { Loader2 } from "lucide-react";
import clsx from "clsx";

export function Spinner({ className, label }: { className?: string; label?: string }) {
  return (
    <div className={clsx("flex items-center gap-2 text-slate-400", className)}>
      <Loader2 className="h-5 w-5 animate-spin" />
      {label && <span className="text-sm">{label}</span>}
    </div>
  );
}

export function FullScreenSpinner({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex h-screen w-full flex-col items-center justify-center gap-3 bg-surface-950">
      <Loader2 className="h-8 w-8 animate-spin text-brand-400" />
      <p className="text-sm text-slate-400">{label}</p>
    </div>
  );
}
