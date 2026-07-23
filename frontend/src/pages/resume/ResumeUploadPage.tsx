import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { FileText, X } from "lucide-react";

import { ResumeUploadDropzone } from "@/components/resume/ResumeUploadDropzone";
import { Button } from "@/components/common/Button";
import { Card, CardBody } from "@/components/common/Card";
import { resumeApi } from "@/api/resumeApi";
import { getApiErrorMessage } from "@/api/client";
import { formatFileSize } from "@/utils/format";

export function ResumeUploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setProgress(0);
    try {
      await resumeApi.upload(selectedFile, setProgress);
      toast.success("Resume uploaded and parsed successfully");
      await queryClient.invalidateQueries({ queryKey: ["resume", "me"] });
      navigate("/resumes");
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Upload failed. Please try again."));
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Upload resume</h1>
        <p className="mt-1 text-sm text-slate-400">
          Uploading a new resume replaces your previously stored one.
        </p>
      </div>

      <Card>
        <CardBody className="pt-5">
          {!selectedFile ? (
            <ResumeUploadDropzone onFileSelected={setSelectedFile} disabled={isUploading} />
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between rounded-xl border border-surface-600 bg-surface-800 px-4 py-3">
                <div className="flex min-w-0 items-center gap-3">
                  <FileText className="h-5 w-5 shrink-0 text-brand-400" />
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-slate-100">{selectedFile.name}</p>
                    <p className="text-xs text-slate-500">{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>
                {!isUploading && (
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="rounded-lg p-1.5 text-slate-400 hover:bg-surface-700 hover:text-white"
                    aria-label="Remove file"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>

              {isUploading && (
                <div className="space-y-1.5">
                  <div className="h-2 w-full overflow-hidden rounded-full bg-surface-700">
                    <div
                      className="h-full bg-brand-500 transition-all duration-200"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <p className="text-right text-xs text-slate-500">{progress}%</p>
                </div>
              )}

              <Button className="w-full" onClick={handleUpload} isLoading={isUploading}>
                {isUploading ? "Uploading..." : "Upload and parse"}
              </Button>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
