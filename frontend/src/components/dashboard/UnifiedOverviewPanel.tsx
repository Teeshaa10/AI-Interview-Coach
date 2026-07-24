import { useQuery } from "@tanstack/react-query";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { Code2, Flame, MessagesSquare, Mic, Sparkles, Trophy } from "lucide-react";

import { sessionsApi } from "@/api/sessionsApi";
import { Card, CardBody, CardHeader } from "@/components/common/Card";
import { Spinner } from "@/components/common/Spinner";
import type { SessionType } from "@/types/sessions";

const TYPE_LABEL: Record<SessionType, string> = {
  text: "Text interviews",
  voice: "Voice interviews",
  coding: "Coding interviews",
};

const TYPE_COLOR: Record<SessionType, string> = {
  text: "#6366f1",
  voice: "#f59e0b",
  coding: "#22c55e",
};

const TYPE_ICON: Record<SessionType, typeof MessagesSquare> = {
  text: MessagesSquare,
  voice: Mic,
  coding: Code2,
};

export function UnifiedOverviewPanel() {
  const { data: overview, isLoading: isOverviewLoading } = useQuery({
    queryKey: ["sessions", "analytics", "overview"],
    queryFn: sessionsApi.analyticsOverview,
  });

  const { data: insights, isLoading: isInsightsLoading } = useQuery({
    queryKey: ["sessions", "analytics", "insights"],
    queryFn: sessionsApi.analyticsInsights,
  });

  if (isOverviewLoading) {
    return <Spinner label="Loading your unified analytics..." />;
  }

  if (!overview || overview.total_sessions === 0) {
    return null;
  }

  const pieData = overview.by_type
    .filter((t) => t.total > 0)
    .map((t) => ({ name: TYPE_LABEL[t.type], value: t.total, color: TYPE_COLOR[t.type] }));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-slate-100">All-up practice overview</h2>
        <p className="mt-1 text-sm text-slate-400">
          Text, voice, and coding interviews combined into one picture.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardBody className="pt-5">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Total sessions</p>
            <p className="mt-2 text-2xl font-semibold text-slate-100">{overview.total_sessions}</p>
            <p className="mt-1 text-xs text-slate-500">
              {overview.completed_sessions} completed &middot; {overview.in_progress_sessions} in progress
            </p>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="pt-5">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Average score</p>
            <p className="mt-2 text-2xl font-semibold text-slate-100">{overview.average_score_overall.toFixed(1)}</p>
            <p className="mt-1 text-xs text-slate-500">
              Best {overview.best_score_overall.toFixed(1)} &middot; Lowest {overview.lowest_score_overall.toFixed(1)}
            </p>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="flex items-center gap-3 pt-5">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-amber-500/10">
              <Flame className="h-5 w-5 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-slate-100">{overview.current_streak_days}d</p>
              <p className="text-xs text-slate-500">Current streak &middot; best {overview.longest_streak_days}d</p>
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="flex items-center gap-3 pt-5">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-500/10">
              <Trophy className="h-5 w-5 text-brand-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-100">
                Tech {overview.average_technical_score.toFixed(1)} &middot; Comm{" "}
                {overview.average_communication_score.toFixed(1)}
              </p>
              <p className="text-xs text-slate-500">From reported interviews</p>
            </div>
          </CardBody>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <h3 className="text-sm font-semibold text-slate-100">Sessions by type</h3>
          </CardHeader>
          <CardBody>
            {pieData.length === 0 ? (
              <p className="py-8 text-center text-sm text-slate-500">No sessions yet.</p>
            ) : (
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80} paddingAngle={2}>
                      {pieData.map((entry) => (
                        <Cell key={entry.name} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 8 }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
            <div className="mt-3 flex flex-wrap gap-3">
              {overview.by_type.map((t) => {
                const Icon = TYPE_ICON[t.type];
                return (
                  <div key={t.type} className="flex items-center gap-1.5 text-xs text-slate-400">
                    <Icon className="h-3.5 w-3.5" style={{ color: TYPE_COLOR[t.type] }} />
                    {TYPE_LABEL[t.type]}: {t.total} ({t.average_score.toFixed(1)} avg)
                  </div>
                );
              })}
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="flex items-center gap-2 text-sm font-semibold text-slate-100">
              <Sparkles className="h-4 w-4 text-brand-400" />
              Personalized insights
              {insights?.generated_by_ai && (
                <span className="rounded-full bg-brand-500/10 px-2 py-0.5 text-[10px] font-medium text-brand-300">
                  AI generated
                </span>
              )}
            </h3>
          </CardHeader>
          <CardBody>
            {isInsightsLoading && <Spinner label="Generating insights..." />}
            {!isInsightsLoading && insights && (
              <ul className="space-y-2.5 text-sm text-slate-300">
                {insights.insights.map((line, index) => (
                  <li key={index} className="flex gap-2">
                    <span className="text-brand-400">&bull;</span>
                    <span>{line}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
