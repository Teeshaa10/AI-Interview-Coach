import { FileText } from "lucide-react";

import { Card, CardBody, CardHeader } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { formatDate } from "@/utils/format";
import type { Resume } from "@/types/resume";

export function ResumeDetails({ resume }: { resume: Resume }) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-500/10">
            <FileText className="h-5 w-5 text-brand-400" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-100">{resume.original_filename}</h2>
            <p className="text-xs text-slate-500">Uploaded {formatDate(resume.created_at)}</p>
          </div>
          <div className="ml-auto">
            <Badge tone="brand">{resume.file_type.toUpperCase()}</Badge>
          </div>
        </CardHeader>
        <CardBody>
          <dl className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-500">Stored filename</dt>
              <dd className="mt-1 truncate text-slate-200">{resume.filename}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-500">Last updated</dt>
              <dd className="mt-1 text-slate-200">{formatDate(resume.updated_at)}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-500">Resume ID</dt>
              <dd className="mt-1 truncate text-slate-200">{resume.id}</dd>
            </div>
          </dl>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="text-sm font-semibold text-slate-100">Parsed content</h3>
          <p className="mt-1 text-xs text-slate-500">Text extracted from your resume by the backend parser.</p>
        </CardHeader>
        <CardBody>
          <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-lg bg-surface-950 p-4 text-xs leading-relaxed text-slate-300 scrollbar-thin">
            {resume.extracted_text || "No text was extracted from this file."}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}
