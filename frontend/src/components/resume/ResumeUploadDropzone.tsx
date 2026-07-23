import { useCallback, useRef, useState, type DragEvent } from "react";
import { FileUp, UploadCloud } from "lucide-react";
import clsx from "clsx";

const ALLOWED_EXTENSIONS = [".pdf", ".docx"];
const MAX_SIZE_BYTES = 10 * 1024 * 1024; // Matches ResumeService.MAX_FILE_SIZE_BYTES on the backend.

interface ResumeUploadDropzoneProps {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

export function ResumeUploadDropzone({ onFileSelected, disabled }: ResumeUploadDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndEmit = useCallback(
    (file: File) => {
      const extension = `.${file.name.split(".").pop()?.toLowerCase()}`;
      if (!ALLOWED_EXTENSIONS.includes(extension)) {
        setValidationError("Only PDF and DOCX files are supported.");
        return;
      }
      if (file.size > MAX_SIZE_BYTES) {
        setValidationError("File is too large. Maximum size is 10 MB.");
        return;
      }
      setValidationError(null);
      onFileSelected(file);
    },
    [onFileSelected],
  );

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    if (disabled) return;
    const file = event.dataTransfer.files?.[0];
    if (file) validateAndEmit(file);
  };

  return (
    <div className="space-y-2">
      <div
        onDragOver={(event) => {
          event.preventDefault();
          if (!disabled) setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !disabled && inputRef.current?.click()}
        className={clsx(
          "flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 text-center transition-colors",
          isDragging ? "border-brand-400 bg-brand-500/5" : "border-surface-600 hover:border-surface-500",
          disabled && "cursor-not-allowed opacity-60",
        )}
      >
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-surface-800">
          <UploadCloud className="h-6 w-6 text-brand-400" />
        </div>
        <p className="text-sm font-medium text-slate-100">
          Drag and drop your resume here, or <span className="text-brand-400">browse</span>
        </p>
        <p className="mt-1 text-xs text-slate-500">PDF or DOCX, up to 10 MB</p>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          disabled={disabled}
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) validateAndEmit(file);
            event.target.value = "";
          }}
        />
      </div>
      {validationError && (
        <p className="flex items-center gap-1.5 text-xs text-red-400">
          <FileUp className="h-3.5 w-3.5" />
          {validationError}
        </p>
      )}
    </div>
  );
}
