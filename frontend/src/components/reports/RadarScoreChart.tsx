import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer } from "recharts";

import { Card, CardBody, CardHeader } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { Activity } from "lucide-react";

interface RadarDatum {
  axis: string;
  score: number;
}

export function RadarScoreChart({ data, title = "Score breakdown" }: { data: RadarDatum[]; title?: string }) {
  return (
    <Card>
      <CardHeader>
        <h2 className="text-sm font-semibold text-slate-100">{title}</h2>
        <p className="mt-1 text-xs text-slate-500">How scores are distributed across categories.</p>
      </CardHeader>
      <CardBody>
        {data.length === 0 ? (
          <EmptyState icon={Activity} title="No category data" description="This report has no category breakdown." />
        ) : (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={data} outerRadius="75%">
                <PolarGrid stroke="#242e46" />
                <PolarAngleAxis dataKey="axis" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, 10]} tick={{ fill: "#64748b", fontSize: 10 }} stroke="#242e46" />
                <Radar name="Score" dataKey="score" stroke="#5b87ff" fill="#5b87ff" fillOpacity={0.35} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
