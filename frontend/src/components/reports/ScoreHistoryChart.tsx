import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, Legend } from "recharts";

import { Card, CardBody, CardHeader } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { LineChart as LineChartIcon } from "lucide-react";
import type { ScoreTrendPoint } from "@/types/report";
import { formatDate } from "@/utils/format";

interface ChartPoint {
  label: string;
  overall: number;
  technical: number;
  communication: number;
}

function toChartPoints(points: ScoreTrendPoint[]): ChartPoint[] {
  return points.map((point) => ({
    label: formatDate(point.date),
    overall: point.overall_score,
    technical: point.technical_score,
    communication: point.communication_score,
  }));
}

export function ScoreHistoryChart({ points }: { points: ScoreTrendPoint[] }) {
  return (
    <Card>
      <CardHeader>
        <h2 className="text-sm font-semibold text-slate-100">Score history</h2>
        <p className="mt-1 text-xs text-slate-500">Overall, technical and communication scores per interview.</p>
      </CardHeader>
      <CardBody>
        {points.length === 0 ? (
          <EmptyState
            icon={LineChartIcon}
            title="Not enough data yet"
            description="Complete more interviews to see your score trend."
          />
        ) : (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={toChartPoints(points)} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a2236" />
                <XAxis dataKey="label" tick={{ fill: "#64748b", fontSize: 11 }} stroke="#242e46" />
                <YAxis domain={[0, 10]} tick={{ fill: "#64748b", fontSize: 11 }} stroke="#242e46" />
                <Tooltip
                  contentStyle={{ background: "#111729", border: "1px solid #242e46", borderRadius: 8 }}
                  labelStyle={{ color: "#f1f5f9" }}
                />
                <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                <Line type="monotone" dataKey="overall" name="Overall" stroke="#5b87ff" strokeWidth={2} dot={{ r: 3 }} />
                <Line
                  type="monotone"
                  dataKey="technical"
                  name="Technical"
                  stroke="#34d399"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="communication"
                  name="Communication"
                  stroke="#fbbf24"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
