import { Link } from "react-router-dom";
import { Compass } from "lucide-react";

import { Button } from "@/components/common/Button";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-surface-950 px-4 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-surface-800">
        <Compass className="h-7 w-7 text-slate-400" />
      </div>
      <h1 className="text-3xl font-semibold text-slate-100">Page not found</h1>
      <p className="max-w-sm text-sm text-slate-400">
        The page you&apos;re looking for doesn&apos;t exist or may have moved.
      </p>
      <Link to="/dashboard">
        <Button>Back to dashboard</Button>
      </Link>
    </div>
  );
}
