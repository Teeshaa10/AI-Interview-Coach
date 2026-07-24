import type { LucideIcon } from "lucide-react";
import { Award, CheckCircle2, Flame, Target } from "lucide-react";

import { Card, CardBody, CardHeader } from "@/components/common/Card";
import type { CoachingProfile } from "@/types/coaching";

function StatBlock({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string | number }) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-surface-700 px-4 py-3">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-surface-800">
        <Icon className="h-4 w-4 text-brand-400" />
      </div>
      <div className="min-w-0">
        <p className="text-base font-semibold text-slate-100">{value}</p>
        <p className="truncate text-xs text-slate-500">{label}</p>
      </div>
    </div>
  );
}

export function ProgressSummary({ profile }: { profile: CoachingProfile }) {
  return (
    <Card>
      <CardHeader>
        <h3 className="text-sm font-semibold text-slate-100">Progress summary</h3>
      </CardHeader>
      <CardBody className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatBlock icon={CheckCircle2} label="Sessions completed" value={profile.completed_sessions} />
        <StatBlock icon={Target} label="Average score" value={profile.average_score_overall.toFixed(1)} />
        <StatBlock icon={Flame} label="Current streak (days)" value={profile.current_streak_days} />
        <StatBlock icon={Award} label="Longest streak (days)" value={profile.longest_streak_days} />
      </CardBody>
      {profile.by_type.length > 0 && (
        <CardBody className="pt-0">
          <div className="border-t border-surface-700 pt-4">
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">By interview type</p>
            <ul className="space-y-2">
              {profile.by_type.map((breakdown) => (
                <li key={breakdown.type} className="flex items-center justify-between text-sm">
                  <span className="capitalize text-slate-300">{breakdown.type}</span>
                  <span className="text-slate-500">
                    {breakdown.completed}/{breakdown.total} completed &middot; avg {breakdown.average_score.toFixed(1)}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </CardBody>
      )}
    </Card>
  );
}
