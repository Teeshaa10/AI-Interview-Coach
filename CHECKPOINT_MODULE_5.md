# Checkpoint — Module 5: Voice Interview (checkpoint B — UI complete, build not yet run)

Status: All Module 5 pages, components, hooks, API layer, routing and
navigation are implemented. `npm install` / `npm run build` / `npm run
lint` have **not** been run yet (final stage only, per instructions).

## Backend voice endpoints verified (app/api/v1/voice.py)

- `POST /voice/transcribe` — multipart `audio` file -> `TranscriptionResponse {transcription, language, duration_seconds}`. Standalone transcription, not tied to an interview. **Not used** by this UI — not needed for the required flow.
- `POST /voice/interview/{interview_id}/answer` — multipart form: `question_number` (Form, int, `ge=1`) + `audio` (File) -> `VoiceAnswerResponse {interview_id, transcription, question: InterviewQuestion}`. **This is the only endpoint the UI calls.** It transcribes AND evaluates the answer server-side in one request (`VoiceService.submit_voice_answer`: looks up the interview, transcribes with faster-whisper, evaluates with the same `EvaluationService` Module 3 uses, persists the updated question, and returns it).
- `POST /voice/text-to-speech`, `GET /voice/audio/{audio_id}` — TTS playback of arbitrary text via edge-tts. Out of scope for this module (the brief describes recording spoken *answers*, not reading questions aloud) — verified but intentionally unused.
- Allowed upload extensions (`VoiceService.ALLOWED_AUDIO_EXTENSIONS`): `.wav .mp3 .m4a .ogg .webm .flac .aac`. The frontend only ever produces webm/ogg/mp4 via `MediaRecorder`, mapped to `webm`/`ogg`/`m4a` filenames by `utils/audio.ts::getAudioFileExtension`.

There is **no** `POST /voice/interview/start` and **no** `GET` voice-session endpoint anywhere in `app/api/v1/voice.py`. A voice interview is the same session as a text interview — created with the existing `POST /interview/start` (`InterviewSessionCreate {resume_id, job_role, experience_level, number_of_questions}` → `InterviewSessionResponse {interview_id, questions}`) — because `submit_voice_answer` resolves the interview through the same `InterviewRepository` text answers use. Session recovery therefore reuses the **existing** `sessionStorage` pattern in `utils/interviewSession.ts` unchanged; no recovery endpoint was invented.

## Pages completed

| Page | Route | Notes |
|---|---|---|
| `VoiceInterviewSetupPage` | `/voice/setup` | Reuses `InterviewSetupForm` verbatim (same `/interview/start` contract as text interviews) — no duplicated form logic. On success, saves session state via the existing `saveInterviewState` and navigates to `/voice/:interviewId`. |
| `VoiceInterviewSessionPage` | `/voice/:sessionId` | Question display, progress, timer, exit dialog all reuse Module 3 components unchanged. Recording UI (`VoiceAnswerRecorder`) replaces `AnswerEditor` for the unanswered state. Once a question has `feedback` (i.e. has been graded), shows the transcript (`currentQuestion.answer`) + reused `AnswerFeedback` + Next/Finish — identical control flow to `InterviewSessionPage`. |
| `VoiceInterviewCompletePage` | `/voice/:sessionId/complete` | Same `GET /interview/history` lookup-by-id strategy as `InterviewCompletePage` (no per-session GET exists). Reuses `InterviewCompletionCard` with `setupHref="/voice/setup"` and `reportHref="/reports/interview/:sessionId"` (Module 4's report generation works for any `interview_id`, voice or text, so no new report behavior was invented). |

## Components completed

- `src/components/voice/VoiceAnswerRecorder.tsx` — mic-permission / record / stop / preview / retake / submit UI built on `useAudioRecorder`. Handles: unsupported browser, permission idle/requesting/denied/granted, recording, stopped-with-preview. All interactive elements have `aria-label`s; the state region is `aria-live="polite"`.
- **Reused unchanged**: `QuestionCard`, `AnswerFeedback`, `InterviewProgress`, `InterviewTimer`, `ExitInterviewDialog` (all from Module 3, zero modifications).
- **Reused with additive change**: `InterviewCompletionCard` — added two optional props (`setupHref` defaulting to `/interviews/setup`, `reportHref` defaulting to unset) so Module 3's existing call site renders byte-for-byte the same as before, while the voice completion page can point "Start another interview" at `/voice/setup` and add a "View report" link.

## Hooks completed

- `src/hooks/useAudioRecorder.ts` — see checkpoint-1 notes (support/permission detection, MIME-type negotiation via `MediaRecorder.isTypeSupported`, start/stop/reset, elapsed-time timer, object-URL lifecycle, full cleanup on unmount, empty-recording rejection, duplicate-recording guard). Unchanged since checkpoint 1.

## API services completed

- `src/api/voiceApi.ts` — `voiceApi.submitAnswer(interviewId, questionNumber, audioBlob, filename)` → `POST /voice/interview/{id}/answer`. No `Content-Type` header is set manually (axios drops the instance's default `application/json` header for `FormData` bodies and lets the browser set the multipart boundary) — this satisfies the "do not manually set a multipart boundary" requirement.
- `src/types/voice.ts` — `VoiceAnswerResponse`, reusing `InterviewQuestion` from `types/interview.ts` rather than redefining it.
- `src/utils/audio.ts` — `getAudioFileExtension(mimeType)`.

## Routes added (`src/App.tsx`)

```
/voice/setup                -> VoiceInterviewSetupPage
/voice/:sessionId           -> VoiceInterviewSessionPage
/voice/:sessionId/complete  -> VoiceInterviewCompletePage
```

All three are nested inside the existing `ProtectedRoute` + `AppLayout` tree, alongside Modules 1–4's routes (untouched). Param name `sessionId` matches the existing `/interviews/:sessionId` convention exactly.

## Navigation

`src/layouts/AppLayout.tsx` — added one `Voice Interview` entry (icon: `Mic`, links to `/voice/setup`) to the existing sidebar `navItems` array, alongside the existing Dashboard/Resume/Search/Interviews/Reports items. Nothing else in the layout changed.

## Files added

```
frontend/src/types/voice.ts
frontend/src/api/voiceApi.ts
frontend/src/utils/audio.ts
frontend/src/hooks/useAudioRecorder.ts
frontend/src/components/voice/VoiceAnswerRecorder.tsx
frontend/src/pages/voice/VoiceInterviewSetupPage.tsx
frontend/src/pages/voice/VoiceInterviewSessionPage.tsx
frontend/src/pages/voice/VoiceInterviewCompletePage.tsx
CHECKPOINT_MODULE_5.md
BUILD_REPORT_MODULE_5.md
```

## Files modified

```
frontend/src/components/interview/InterviewCompletionCard.tsx — added optional setupHref/reportHref props (default-backward-compatible)
frontend/src/App.tsx                — registered the 3 new voice routes
frontend/src/layouts/AppLayout.tsx  — added "Voice Interview" nav item
```

No backend files, no Module 1–4 pages, and no other Module 3 component were touched.

## Session-recovery strategy

Identical to Module 3: `utils/interviewSession.ts` (unmodified) persists `{interviewId, questions, currentIndex}` to `sessionStorage` keyed by `aic_interview_${interviewId}` after every state change (setup start, each graded answer, each "next question"). On mount, `VoiceInterviewSessionPage` reads that key:
- **Missing/expired/invalid session id** → `stored` is `null` → `questions` is set to `[]` → renders the "can't be recovered" `EmptyState` with a "Start a new voice interview" CTA to `/voice/setup`.
- **Completed session** → completing the interview calls `clearInterviewState(sessionId)` before navigating to the complete page, so revisiting `/voice/:sessionId` afterwards correctly falls into the same "can't be recovered" state (there's nothing to resume — matches Module 3's behavior exactly).
- **In-progress session, same tab** → state restores `currentIndex` and every already-graded question, so a refresh lands back on the right question with prior feedback intact.

No new sessionStorage key scheme or endpoint was introduced — voice sessions live in the exact same storage format as text sessions, because they're the exact same backend session type.

## Audio cleanup strategy (`useAudioRecorder.ts`)

- `stopRecording()` calls `mediaRecorder.stop()`; the `onstop` handler stops every `MediaStreamTrack` on the underlying stream (`stream.getTracks().forEach(track => track.stop())`) so the browser's mic-in-use indicator turns off immediately after each recording — the mic is only "live" while actively recording, not for the whole session.
- Starting a new recording (including a retake) re-runs `getUserMedia` if the previous stream's tracks have all ended, rather than assuming a stopped stream is reusable.
- Every previous object URL is revoked with `URL.revokeObjectURL` before a new one is created (`revokeAudioUrl()`), and again on unmount, so object URLs never leak across retakes or navigations.
- `mediaRecorder.ondataavailable` / `onstop` / `onerror` handlers are set to `null` before teardown to guarantee no stale closures fire after unmount.
- The interval timer is always cleared via `clearInterval` in both `onstop` and the unmount effect, never left running.
- `startRecording()` no-ops if already `recording`, preventing two concurrent `MediaRecorder` instances.
- An empty recording (zero total chunk bytes) is rejected with a user-facing error and never produces an `audioBlob`/`audioUrl`, so it can't be accidentally submitted.
- The unmount `useEffect` cleanup runs all four steps above unconditionally (clear timer → detach handlers → stop tracks → revoke URL), covering the case where a person navigates away mid-recording.

## Manual tests performed

Same sandbox constraint as Module 4: no outbound network access here, so `npm install`/`npm run build`/`npm run lint` were intentionally **not** run for this checkpoint (the task instructions reserve that for the final build stage). In their place:

- Re-verified `app/api/v1/voice.py` and `app/schemas/voice.py` line-by-line against `voiceApi.ts` and `types/voice.ts` (path, HTTP method, multipart field names `question_number`/`audio`, response shape).
- Confirmed `backend/app/main.py` mounts the voice router with `prefix="/voice"` and no `/api/v1` prefix, matching the existing `interviewApi.ts`/`reportApi.ts` pattern already in this codebase.
- Traced every prop passed into reused Module 3 components (`QuestionCard`, `AnswerFeedback`, `InterviewProgress`, `InterviewTimer`, `ExitInterviewDialog`) against their existing prop types — no changes needed, contracts fit as-is.
- Checked `tsconfig.json` (`strict: true`, `isolatedModules: true`) and used `import type` for every type-only import in all new/modified files.
- Confirmed there is **no** ESLint config or ESLint devDependency anywhere in this project (`grep -n "lint" package.json` → `"eslint ."`, but `eslint` is absent from `devDependencies` and no `.eslintrc*`/`eslint.config.*` file exists) — this is a **pre-existing gap**, not something introduced by Module 4 or Module 5. `npm run lint` will fail with "command not found" until ESLint is added to the project; see `BUILD_REPORT_MODULE_5.md`.
- Grepped every new/modified Module 5 file for `any`, `console.log`, `TODO`, `FIXME` — none found.
- Caught and fixed one real bug during self-review: `VoiceInterviewCompletePage` initially referenced a fabricated `interview.number_of_questions` field that does not exist on `InterviewHistoryItem` (types/interview.ts only has `interview_id, job_role, experience_level, average_score, completed, created_at`) — removed before this checkpoint; the completion page now only reads fields that actually exist on that type.

## Known limitations

- No ESLint is configured in this project at all (pre-existing, not a Module 5 regression) — `npm run lint` cannot succeed until an ESLint config + dependency is added, which is out of scope for "do not invent" here since Module 5 didn't introduce this gap.
- `VoiceInterviewCompletePage` can only show the overall average score and job role/level (from `GET /interview/history`), not a per-question voice summary, because — same as Module 3 — there's no endpoint that returns full question detail for a finished session outside of the Reports module. The "View report" link covers that gap by pointing at the Module 4 report for the same `interview_id`.
- `useAudioRecorder` picks the *first* browser-supported MIME type from a fixed candidate list (`webm/opus`, `webm`, `ogg/opus`, `ogg`, `mp4`); it does not let the user choose a format, matching the "reuse existing conventions, don't over-engineer" instruction.
- Not yet verified by an actual TypeScript/Vite compile — see `BUILD_REPORT_MODULE_5.md`.

## Remaining work

`npm install`, `npm run build`, `npm run lint` (final stage only, per instructions), fixing any errors those surface, then the final `AI-Interview-Coach-Module5-Final.zip`.
