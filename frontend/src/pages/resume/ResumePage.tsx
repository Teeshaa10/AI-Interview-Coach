import { Link } from "react-router-dom";
import { Plus, Trash2 } from "lucide-react";
import toast from "react-hot-toast";
import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { useMyResume } from "@/hooks/useMyResume";
import { resumeApi } from "@/api/resumeApi";
import { getApiErrorMessage } from "@/api/client";
import { Button } from "@/components/common/Button";
import { EmptyState } from "@/components/common/EmptyState";
import { Spinner } from "@/components/common/Spinner";
import { ResumeDetails } from "@/components/resume/ResumeDetails";
import { FileText } from "lucide-react";
import { Modal } from "@/components/common/Modal";

export function ResumePage() {
  const { data: resume, isLoading, hasNoResume } = useMyResume();
  const queryClient = useQueryClient();
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!resume) return;
    setIsDeleting(true);
    try {
      await resumeApi.delete(resume.id);
      toast.success("Resume deleted");
      await queryClient.invalidateQueries({ queryKey: ["resume", "me"] });
      setIsDeleteModalOpen(false);
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Could not delete this resume."));
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">My Resume</h1>
          <p className="mt-1 text-sm text-slate-400">
            The backend keeps only your most recently uploaded resume.
          </p>
        </div>
        <Link to="/resumes/upload">
          <Button>
            <Plus className="h-4 w-4" />
            {resume ? "Replace resume" : "Upload resume"}
          </Button>
        </Link>
      </div>

      {isLoading && <Spinner label="Loading your resume..." />}

      {!isLoading && hasNoResume && (
        <EmptyState
          icon={FileText}
          title="No resume uploaded yet"
          description="Upload a PDF or DOCX resume to unlock AI interviews and resume search."
          action={
            <Link to="/resumes/upload">
              <Button>
                <Plus className="h-4 w-4" />
                Upload your resume
              </Button>
            </Link>
          }
        />
      )}

      {resume && (
        <>
          <ResumeDetails resume={resume} />
          <div className="flex justify-end">
            <Button variant="danger" size="sm" onClick={() => setIsDeleteModalOpen(true)}>
              <Trash2 className="h-4 w-4" />
              Delete resume
            </Button>
          </div>
        </>
      )}

      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Delete resume"
        footer={
          <>
            <Button variant="secondary" onClick={() => setIsDeleteModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" isLoading={isDeleting} onClick={handleDelete}>
              Delete
            </Button>
          </>
        }
      >
        This will permanently delete your uploaded resume. You&apos;ll need to upload a new one before
        starting another AI interview.
      </Modal>
    </div>
  );
}
