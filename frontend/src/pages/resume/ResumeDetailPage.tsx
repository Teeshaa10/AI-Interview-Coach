import { useParams, Link } from "react-router-dom";
import { AlertTriangle, ArrowLeft } from "lucide-react";

import { useMyResume } from "@/hooks/useMyResume";
import { ResumeDetails } from "@/components/resume/ResumeDetails";
import { Spinner } from "@/components/common/Spinner";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/common/Button";

/**
 * The backend has no GET /resume/{resume_id} endpoint - only DELETE. This
 * page therefore reuses GET /resume/me (the only resume the user has) and
 * checks the id in the URL against it, rather than fetching by id.
 */
export function ResumeDetailPage() {
  const { resumeId } = useParams<{ resumeId: string }>();
  const { data: resume, isLoading, hasNoResume } = useMyResume();

  if (isLoading) {
    return <Spinner label="Loading resume..." />;
  }

  if (hasNoResume || !resume || resume.id !== resumeId) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Resume not found"
        description="This resume no longer exists, or the backend does not expose a lookup for it by id."
        action={
          <Link to="/resumes">
            <Button variant="secondary">
              <ArrowLeft className="h-4 w-4" />
              Back to my resume
            </Button>
          </Link>
        }
      />
    );
  }

  return (
    <div className="space-y-6">
      <Link to="/resumes" className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-200">
        <ArrowLeft className="h-4 w-4" />
        Back to my resume
      </Link>
      <ResumeDetails resume={resume} />
    </div>
  );
}
