import { CheckCircle2, XCircle } from "lucide-react";
import clsx from "clsx";

import { Card, CardBody, CardHeader } from "@/components/common/Card";

interface StrengthWeaknessListProps {
  title: string;
  items: string[];
  tone: "success" | "danger";
  emptyLabel: string;
}

export function StrengthWeaknessList({ title, items, tone, emptyLabel }: StrengthWeaknessListProps) {
  const Icon = tone === "success" ? CheckCircle2 : XCircle;
  const iconClasses = tone === "success" ? "text-emerald-400" : "text-red-400";

  return (
    <Card>
      <CardHeader>
        <h2 className="text-sm font-semibold text-slate-100">{title}</h2>
      </CardHeader>
      <CardBody>
        {items.length === 0 ? (
          <p className="text-sm text-slate-500">{emptyLabel}</p>
        ) : (
          <ul className="space-y-2.5">
            {items.map((item, index) => (
              <li key={`${index}-${item}`} className="flex items-start gap-2.5 text-sm text-slate-300">
                <Icon className={clsx("mt-0.5 h-4 w-4 shrink-0", iconClasses)} />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        )}
      </CardBody>
    </Card>
  );
}
