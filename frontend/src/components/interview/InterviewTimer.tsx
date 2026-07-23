import { useEffect, useState } from "react";
import { Clock } from "lucide-react";

/**
 * A purely client-side elapsed-time display. The backend does not enforce
 * any time limit on answering a question, so this never auto-submits or
 * blocks anything - it's informational only, per the "only if it does not
 * conflict with backend behavior" requirement.
 */
export function InterviewTimer({ resetKey }: { resetKey: string | number }) {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    setSeconds(0);
    const interval = setInterval(() => setSeconds((value) => value + 1), 1000);
    return () => clearInterval(interval);
  }, [resetKey]);

  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;

  return (
    <div className="flex items-center gap-1.5 text-xs text-slate-500">
      <Clock className="h-3.5 w-3.5" />
      {minutes}:{remainder.toString().padStart(2, "0")}
    </div>
  );
}
