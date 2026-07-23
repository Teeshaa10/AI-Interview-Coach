import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";
import { Link } from "react-router-dom";

import { useMyResume } from "@/hooks/useMyResume";
import { Card, CardBody } from "@/components/common/Card";
import { Button } from "@/components/common/Button";
import { Spinner } from "@/components/common/Spinner";

/**
 * Since the backend only ever has one resume per user (GET /resume/me),
 * "selecting" a resume just means confirming it's the one you'll use -
 * there is no list to pick from.
 */
export function ResumeSelector({ onResumeId }: { onResumeId: (resumeId: string | null) => void }) {
  const { data: resume, isLoading, hasNoResume } = useMyResume();

  useEffect(() => {
    onResumeId(resume?.id ?? null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resume?.id]);

  if (isLoading) return <Spinner label="Loading your resume..." />;

  if (hasNoResume || !resume) {
    return (
      <Card>
        <CardBody className="flex items-start gap-3 pt-5">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-400" />
          <div>
            <p className="text-sm font-medium text-slate-100">No resume on file</p>
            <p className="mt-1 text-sm text-slate-400">
              You need to upload a resume before starting an AI interview.
            </p>
            <Link to="/resumes/upload" className="mt-3 inline-block">
              <Button size="sm">Upload resume</Button>
            </Link>
          </div>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardBody className="pt-5">
        <p className="text-sm text-slate-400">Interview questions will be based on:</p>
        <p className="mt-1 text-sm font-medium text-slate-100">{resume.original_filename}</p>
      </CardBody>
    </Card>
  );
}
