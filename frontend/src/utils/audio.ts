/**
 * Backend allow-list (VoiceService.ALLOWED_AUDIO_EXTENSIONS in
 * backend/app/services/voice_service.py): .wav .mp3 .m4a .ogg .webm
 * .flac .aac. Browsers only ever produce webm, ogg or mp4 containers via
 * MediaRecorder, so this only needs to cover those - mp4 audio is
 * uploaded with the .m4a extension the backend expects for that codec
 * family.
 */
export function getAudioFileExtension(mimeType: string): string {
  const type = mimeType.toLowerCase();
  if (type.includes("webm")) return "webm";
  if (type.includes("ogg")) return "ogg";
  if (type.includes("mp4")) return "m4a";
  if (type.includes("mpeg")) return "mp3";
  if (type.includes("wav")) return "wav";
  return "webm";
}
