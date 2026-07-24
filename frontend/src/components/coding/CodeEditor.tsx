import type { KeyboardEvent } from "react";

/**
 * Textarea-based code editor. @monaco-editor/react could not be installed
 * in the sandbox used to build this (no network access), so per the
 * project's own fallback instruction this is a well-designed textarea
 * editor instead - monospace, tab-aware, with a language badge. Swapping
 * in Monaco later only requires replacing this component's internals;
 * its props are already Monaco-shaped (value/onChange/language).
 */
interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: string;
  disabled?: boolean;
}

export function CodeEditor({ value, onChange, language, disabled }: CodeEditorProps) {
  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    // Let Tab insert a tab character instead of moving focus, like a real
    // code editor would.
    if (event.key === "Tab") {
      event.preventDefault();
      const target = event.currentTarget;
      const { selectionStart, selectionEnd } = target;
      const next = `${value.slice(0, selectionStart)}\t${value.slice(selectionEnd)}`;
      onChange(next);
      requestAnimationFrame(() => {
        target.selectionStart = target.selectionEnd = selectionStart + 1;
      });
    }
  };

  return (
    <div className="overflow-hidden rounded-lg border border-surface-600 bg-surface-950">
      <div className="flex items-center justify-between border-b border-surface-700 bg-surface-900 px-3 py-1.5">
        <span className="text-xs font-medium uppercase tracking-wide text-slate-400">{language}</span>
      </div>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        spellCheck={false}
        className="h-80 w-full resize-y bg-transparent p-4 font-mono text-sm text-slate-100 placeholder:text-slate-600 focus:outline-none disabled:opacity-60"
        placeholder="Write your solution here..."
      />
    </div>
  );
}
