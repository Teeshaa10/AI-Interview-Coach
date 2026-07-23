import { useCallback, useEffect, useRef, useState } from "react";

export type MicrophonePermissionStatus = "idle" | "requesting" | "granted" | "denied" | "unsupported";

export type RecordingState = "idle" | "recording" | "stopped";

interface UseAudioRecorderResult {
  isSupported: boolean;
  permissionStatus: MicrophonePermissionStatus;
  recordingState: RecordingState;
  elapsedSeconds: number;
  audioBlob: Blob | null;
  audioUrl: string | null;
  mimeType: string | null;
  error: string | null;
  requestPermission: () => Promise<boolean>;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  resetRecording: () => void;
}

const CANDIDATE_MIME_TYPES = [
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/ogg;codecs=opus",
  "audio/ogg",
  "audio/mp4",
];

function detectSupportedMimeType(): string | null {
  if (typeof MediaRecorder === "undefined" || typeof MediaRecorder.isTypeSupported !== "function") {
    return null;
  }
  for (const candidate of CANDIDATE_MIME_TYPES) {
    if (MediaRecorder.isTypeSupported(candidate)) {
      return candidate;
    }
  }
  return null;
}

function isBrowserRecordingSupported(): boolean {
  return (
    typeof window !== "undefined" &&
    typeof MediaRecorder !== "undefined" &&
    Boolean(navigator.mediaDevices) &&
    typeof navigator.mediaDevices.getUserMedia === "function"
  );
}

function describeGetUserMediaError(err: unknown): string {
  if (err instanceof DOMException) {
    switch (err.name) {
      case "NotAllowedError":
      case "PermissionDeniedError":
        return "Microphone access was denied. Allow microphone access in your browser settings and try again.";
      case "NotFoundError":
      case "DevicesNotFoundError":
        return "No microphone was found on this device.";
      case "NotReadableError":
      case "TrackStartError":
        return "Your microphone is already in use by another application.";
      case "SecurityError":
        return "Microphone access is blocked in this context. Try using a secure (https) connection.";
      default:
        return "Could not access the microphone. Please try again.";
    }
  }
  return "Could not access the microphone. Please try again.";
}

/**
 * Reusable, strongly typed audio-recording hook built directly on the
 * browser MediaRecorder API (no third-party recorder libraries, no
 * browser speech-to-text - transcription happens server-side via
 * POST /voice/interview/{id}/answer).
 */
export function useAudioRecorder(): UseAudioRecorderResult {
  const isSupported = isBrowserRecordingSupported();

  const [permissionStatus, setPermissionStatus] = useState<MicrophonePermissionStatus>(
    isSupported ? "idle" : "unsupported",
  );
  const [recordingState, setRecordingState] = useState<RecordingState>("idle");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [mimeType, setMimeType] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const streamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const audioUrlRef = useRef<string | null>(null);

  const clearTimer = useCallback(() => {
    if (timerRef.current !== null) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const stopStreamTracks = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }, []);

  const detachRecorderHandlers = useCallback(() => {
    const recorder = mediaRecorderRef.current;
    if (recorder) {
      recorder.ondataavailable = null;
      recorder.onstop = null;
      recorder.onerror = null;
    }
  }, []);

  const revokeAudioUrl = useCallback(() => {
    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current);
      audioUrlRef.current = null;
    }
  }, []);

  // Full teardown on unmount: stop tracks, clear timers, detach handlers,
  // revoke any outstanding object URL.
  useEffect(() => {
    return () => {
      clearTimer();
      detachRecorderHandlers();
      stopStreamTracks();
      revokeAudioUrl();
    };
  }, [clearTimer, detachRecorderHandlers, stopStreamTracks, revokeAudioUrl]);

  const requestPermission = useCallback(async (): Promise<boolean> => {
    if (!isSupported) {
      setPermissionStatus("unsupported");
      setError("Audio recording isn't supported in this browser.");
      return false;
    }

    setPermissionStatus("requesting");
    setError(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      setPermissionStatus("granted");
      return true;
    } catch (err) {
      setPermissionStatus("denied");
      setError(describeGetUserMediaError(err));
      return false;
    }
  }, [isSupported]);

  const startRecording = useCallback(async (): Promise<void> => {
    if (recordingState === "recording") {
      // Prevent starting a second, simultaneous recording.
      return;
    }

    setError(null);

    let stream = streamRef.current;
    if (!stream || stream.getAudioTracks().every((track) => track.readyState === "ended")) {
      const granted = await requestPermission();
      if (!granted) return;
      stream = streamRef.current;
    }
    if (!stream) return;

    const supportedMimeType = detectSupportedMimeType();
    if (!supportedMimeType) {
      setError("No supported audio recording format was found in this browser.");
      return;
    }

    revokeAudioUrl();
    setAudioUrl(null);
    setAudioBlob(null);
    chunksRef.current = [];

    let recorder: MediaRecorder;
    try {
      recorder = new MediaRecorder(stream, { mimeType: supportedMimeType });
    } catch {
      setError("Could not start recording with this browser's audio format.");
      return;
    }

    recorder.ondataavailable = (event: BlobEvent) => {
      if (event.data.size > 0) {
        chunksRef.current.push(event.data);
      }
    };

    recorder.onerror = () => {
      setError("Recording failed unexpectedly. Please try again.");
      clearTimer();
      setRecordingState("idle");
    };

    recorder.onstop = () => {
      clearTimer();
      stopStreamTracks();

      const chunks = chunksRef.current;
      chunksRef.current = [];

      if (chunks.length === 0 || chunks.reduce((total, chunk) => total + chunk.size, 0) === 0) {
        setError("The recording was empty. Please try again.");
        setRecordingState("idle");
        return;
      }

      const blob = new Blob(chunks, { type: supportedMimeType });
      const url = URL.createObjectURL(blob);
      audioUrlRef.current = url;

      setAudioBlob(blob);
      setAudioUrl(url);
      setMimeType(supportedMimeType);
      setRecordingState("stopped");
    };

    mediaRecorderRef.current = recorder;
    setElapsedSeconds(0);
    recorder.start();
    setRecordingState("recording");

    timerRef.current = setInterval(() => {
      setElapsedSeconds((value) => value + 1);
    }, 1000);
  }, [recordingState, requestPermission, revokeAudioUrl, stopStreamTracks, clearTimer]);

  const stopRecording = useCallback(() => {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
  }, []);

  const resetRecording = useCallback(() => {
    clearTimer();
    revokeAudioUrl();
    chunksRef.current = [];
    setAudioBlob(null);
    setAudioUrl(null);
    setElapsedSeconds(0);
    setRecordingState("idle");
    setError(null);
  }, [clearTimer, revokeAudioUrl]);

  return {
    isSupported,
    permissionStatus,
    recordingState,
    elapsedSeconds,
    audioBlob,
    audioUrl,
    mimeType,
    error,
    requestPermission,
    startRecording,
    stopRecording,
    resetRecording,
  };
}
