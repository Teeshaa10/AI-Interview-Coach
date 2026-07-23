import { Mic, Play, RotateCcw, Send, Square, TriangleAlert } from "lucide-react";
import clsx from "clsx";

import { Button } from "@/components/common/Button";
import { Card, CardBody } from "@/components/common/Card";
import { useAudioRecorder } from "@/hooks/useAudioRecorder";

interface VoiceAnswerRecorderProps {
  onSubmit: (audioBlob: Blob, mimeType: string) => void;
  isSubmitting?: boolean;
}

function formatElapsed(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

export function VoiceAnswerRecorder({ onSubmit, isSubmitting }: VoiceAnswerRecorderProps) {
  const {
    isSupported,
    permissionStatus,
    recordingState,
    elapsedSeconds,
    audioUrl,
    audioBlob,
    mimeType,
    error,
    requestPermission,
    startRecording,
    stopRecording,
    resetRecording,
  } = useAudioRecorder();

  if (!isSupported) {
    return (
      <Card>
        <CardBody className="flex items-start gap-3 pt-5">
          <TriangleAlert className="mt-0.5 h-5 w-5 shrink-0 text-amber-400" />
          <div>
            <p className="text-sm font-medium text-slate-100">Recording isn't supported here</p>
            <p className="mt-1 text-sm text-slate-400">
              This browser doesn't support in-browser audio recording. Try a recent version of Chrome, Edge,
              or Firefox.
            </p>
          </div>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardBody className="space-y-4 pt-5" aria-live="polite">
        {permissionStatus === "idle" && (
          <div className="flex flex-col items-center gap-3 py-6 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-800">
              <Mic className="h-6 w-6 text-slate-400" />
            </div>
            <p className="text-sm text-slate-400">Allow microphone access to record your spoken answer.</p>
            <Button onClick={() => void requestPermission()}>
              <Mic className="h-4 w-4" />
              Allow microphone
            </Button>
          </div>
        )}

        {permissionStatus === "requesting" && (
          <p className="py-6 text-center text-sm text-slate-400">Requesting microphone access...</p>
        )}

        {permissionStatus === "denied" && (
          <div className="flex flex-col items-center gap-3 py-6 text-center">
            <TriangleAlert className="h-6 w-6 text-red-400" />
            <p className="text-sm text-red-400">{error ?? "Microphone access was denied."}</p>
            <Button variant="secondary" onClick={() => void requestPermission()}>
              Try again
            </Button>
          </div>
        )}

        {permissionStatus === "granted" && recordingState === "idle" && (
          <div className="flex flex-col items-center gap-3 py-6 text-center">
            <button
              type="button"
              onClick={() => void startRecording()}
              aria-label="Start recording"
              className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-500 text-white shadow-glow transition-colors hover:bg-brand-400"
            >
              <Mic className="h-7 w-7" />
            </button>
            <p className="text-sm text-slate-400">Tap to start recording your answer.</p>
          </div>
        )}

        {recordingState === "recording" && (
          <div className="flex flex-col items-center gap-3 py-6 text-center">
            <button
              type="button"
              onClick={stopRecording}
              aria-label="Stop recording"
              className="relative flex h-16 w-16 items-center justify-center rounded-full bg-red-500 text-white shadow-glow transition-colors hover:bg-red-400"
            >
              <span className="absolute inset-0 animate-ping rounded-full bg-red-500/60" aria-hidden="true" />
              <Square className="relative h-6 w-6" />
            </button>
            <p className="font-mono text-lg text-slate-100" aria-label="Recording elapsed time">
              {formatElapsed(elapsedSeconds)}
            </p>
            <p className="text-sm text-slate-400">Recording... tap to stop.</p>
          </div>
        )}

        {recordingState === "stopped" && audioUrl && audioBlob && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 rounded-lg bg-surface-800 px-3 py-2">
              <Play className="h-4 w-4 shrink-0 text-slate-400" />
              {/* Spoken interview answer playback - no captions available for a user recording. */}
              <audio controls src={audioUrl} className="h-9 w-full" />
            </div>
            <p className="text-center text-xs text-slate-500">
              Recorded {formatElapsed(elapsedSeconds)} of audio.
            </p>
            <div className="flex gap-3">
              <Button
                variant="secondary"
                className="flex-1"
                onClick={resetRecording}
                disabled={isSubmitting}
              >
                <RotateCcw className="h-4 w-4" />
                Retake
              </Button>
              <Button
                className="flex-1"
                isLoading={isSubmitting}
                onClick={() => mimeType && onSubmit(audioBlob, mimeType)}
              >
                <Send className="h-4 w-4" />
                Submit answer
              </Button>
            </div>
          </div>
        )}

        {error && permissionStatus !== "denied" && (
          <p className={clsx("text-center text-sm text-red-400")}>{error}</p>
        )}
      </CardBody>
    </Card>
  );
}
