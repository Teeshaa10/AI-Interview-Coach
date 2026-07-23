import type { LucideIcon } from "lucide-react";
import { Card, CardBody } from "@/components/common/Card";

interface StatItem {
  label: string;
  value: string | number;
  icon: LucideIcon;
}

export function DashboardStats({ stats }: { stats: StatItem[] }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {stats.map(({ label, value, icon: Icon }) => (
        <Card key={label}>
          <CardBody className="flex items-center gap-4 pt-5">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-500/10">
              <Icon className="h-5 w-5 text-brand-400" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-slate-100">{value}</p>
              <p className="text-xs text-slate-500">{label}</p>
            </div>
          </CardBody>
        </Card>
      ))}
    </div>
  );
}
