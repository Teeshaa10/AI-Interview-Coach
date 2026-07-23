import { Link } from "react-router-dom";
import { FileUp, MessagesSquare, Search } from "lucide-react";

import { Card, CardBody, CardHeader } from "@/components/common/Card";

const actions = [
  { to: "/resumes/upload", label: "Upload resume", icon: FileUp },
  { to: "/interviews/setup", label: "Start an interview", icon: MessagesSquare },
  { to: "/resumes/search", label: "Search your resume", icon: Search },
];

export function QuickActions() {
  return (
    <Card>
      <CardHeader>
        <h3 className="text-sm font-semibold text-slate-100">Quick actions</h3>
      </CardHeader>
      <CardBody className="space-y-2">
        {actions.map(({ to, label, icon: Icon }) => (
          <Link
            key={to}
            to={to}
            className="flex items-center gap-3 rounded-lg border border-surface-700 px-3.5 py-3 text-sm font-medium text-slate-200 transition-colors hover:border-brand-500/40 hover:bg-brand-500/5"
          >
            <Icon className="h-4 w-4 text-brand-400" />
            {label}
          </Link>
        ))}
      </CardBody>
    </Card>
  );
}
