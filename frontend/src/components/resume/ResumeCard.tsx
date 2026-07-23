import { FileText, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";

import { Card, CardBody } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { formatDate } from "@/utils/format";
import type { Resume } from "@/types/resume";

interface ResumeCardProps {
  resume: Resume;
  onDelete?: (resumeId: string) => void;
  isDeleting?: boolean;
}

export function ResumeCard({ resume, onDelete, isDeleting }: ResumeCardProps) {
  return (
    <Card>
      <CardBody className="pt-5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-500/10">
              <FileText className="h-5 w-5 text-brand-400" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-slate-100">{resume.original_filename}</p>
              <p className="mt-0.5 text-xs text-slate-500">Uploaded {formatDate(resume.created_at)}</p>
            </div>
          </div>
          <Badge tone="brand">{resume.file_type.toUpperCase()}</Badge>
        </div>

        <div className="mt-4 flex gap-2">
          <Link to={`/resumes/${resume.id}`} className="flex-1">
            <Button variant="secondary" size="sm" className="w-full">
              View details
            </Button>
          </Link>
          {onDelete && (
            <Button
              variant="danger"
              size="sm"
              isLoading={isDeleting}
              onClick={() => onDelete(resume.id)}
              aria-label="Delete resume"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardBody>
    </Card>
  );
}
