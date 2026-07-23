import { Bar, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardBody, CardHeader } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { TrendingUp } from "lucide-react";
import type { ReportTrendPoint } from "@/types/report";

export function ProgressChart({ points }: { points: ReportTrendPoint[] }) {
  return (
    <Card>
      <CardHeader>
        <h2 className="text-sm font-semibold text-slate-100">Progress over time</h2>
        <p className="mt-1 text-xs text-slate-500">Interviews completed and average score per period.</p>
      </CardHeader>
      <CardBody>
        {points.length === 0 ? (
          <EmptyState
            icon={TrendingUp}
            title="No trend data yet"
            description="Complete a few more interviews to see your progress."
          />
        ) : (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={points} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a2236" />
                <XAxis dataKey="period" tick={{ fill: "#64748b", fontSize: 11 }} stroke="#242e46" />
                <YAxis yAxisId="left" domain={[0, 10]} tick={{ fill: "#64748b", fontSize: 11 }} stroke="#242e46" />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  allowDecimals={false}
                  tick={{ fill: "#64748b", fontSize: 11 }}
                  stroke="#242e46"
                />
                <Tooltip
                  contentStyle={{ background: "#111729", border: "1px solid #242e46", borderRadius: 8 }}
                  labelStyle={{ color: "#f1f5f9" }}
                />
                <Bar yAxisId="right" dataKey="interviews" name="Interviews" fill="#242e46" radius={[4, 4, 0, 0]} />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="average_overall_score"
                  name="Avg score"
                  stroke="#5b87ff"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
