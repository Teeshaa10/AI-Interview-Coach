import { TrendingDown, TrendingUp } from "lucide-react";

import { Card, CardBody, CardHeader } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import type { CoachingInsights } from "@/types/coaching";

export function StrengthsWeaknessesPanel({ insights }: { insights: CoachingInsights }) {
  return (
    <Card>
      <CardHeader>
        <h3 className="text-sm font-semibold text-slate-100">Strengths &amp; weak spots</h3>
      </CardHeader>
      <CardBody className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div>
          <div className="mb-2 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-emerald-400">
            <TrendingUp className="h-3.5 w-3.5" />
            Top strengths
          </div>
          {insights.top_strengths.length === 0 ? (
            <p className="text-sm text-slate-500">Not enough data yet to identify strengths.</p>
          ) : (
            <div className="flex flex-wrap gap-1.5">
              {insights.top_strengths.map((topic) => (
                <Badge key={topic} tone="success">
                  {topic}
                </Badge>
              ))}
            </div>
          )}
        </div>

        <div>
          <div className="mb-2 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-amber-400">
            <TrendingDown className="h-3.5 w-3.5" />
            Priority weaknesses
          </div>
          {insights.priority_weaknesses.length === 0 ? (
            <p className="text-sm text-slate-500">Not enough data yet to identify weak spots.</p>
          ) : (
            <div className="flex flex-wrap gap-1.5">
              {insights.priority_weaknesses.map((topic) => (
                <Badge key={topic} tone="warning">
                  {topic}
                </Badge>
              ))}
            </div>
          )}
        </div>

        {insights.recommended_topics.length > 0 && (
          <div className="sm:col-span-2">
            <div className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
              Recommended focus topics
            </div>
            <div className="flex flex-wrap gap-1.5">
              {insights.recommended_topics.map((topic) => (
                <Badge key={topic} tone="brand">
                  {topic}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
