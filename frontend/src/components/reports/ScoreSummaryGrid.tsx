import type { LucideIcon } from "lucide-react";
import { Award, Brain, MessageCircle, ListChecks } from "lucide-react";
import clsx from "clsx";

import { Card, CardBody } from "@/components/common/Card";
import { scoreTone } from "@/utils/score";

interface ScoreStat {
  label: string;
  value: number;
  icon: LucideIcon;
}

const toneTextClasses: Record<string, string> = {
  success: "text-emerald-400",
  warning: "text-amber-400",
  danger: "text-red-400",
};

export function ScoreSummaryGrid({
  overallScore,
  technicalScore,
  communicationScore,
  completenessScore,
}: {
  overallScore: number;
  technicalScore: number;
  communicationScore: number;
  completenessScore: number;
}) {
  const stats: ScoreStat[] = [
    { label: "Overall score", value: overallScore, icon: Award },
    { label: "Technical", value: technicalScore, icon: Brain },
    { label: "Communication", value: communicationScore, icon: MessageCircle },
    { label: "Completeness", value: completenessScore, icon: ListChecks },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {stats.map(({ label, value, icon: Icon }) => (
        <Card key={label}>
          <CardBody className="pt-5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</span>
              <Icon className="h-4 w-4 text-slate-500" />
            </div>
            <p className={clsx("mt-2 text-2xl font-semibold", toneTextClasses[scoreTone(value)])}>
              {value.toFixed(1)}
              <span className="ml-1 text-sm font-normal text-slate-500">/10</span>
            </p>
          </CardBody>
        </Card>
      ))}
    </div>
  );
}
