import { useState } from "react";

import { Textarea } from "@/components/common/FormControls";
import { Button } from "@/components/common/Button";

interface AnswerEditorProps {
  onSubmit: (answer: string) => void;
  isSubmitting?: boolean;
  disabled?: boolean;
}

export function AnswerEditor({ onSubmit, isSubmitting, disabled }: AnswerEditorProps) {
  const [answer, setAnswer] = useState("");
  const [touched, setTouched] = useState(false);

  const trimmedLength = answer.trim().length;
  const error = touched && trimmedLength === 0 ? "An answer is required." : undefined;

  const handleSubmit = () => {
    setTouched(true);
    if (trimmedLength === 0) return;
    onSubmit(answer.trim());
  };

  return (
    <div className="space-y-3">
      <Textarea
        label="Your answer"
        placeholder="Type your answer here..."
        value={answer}
        onChange={(event) => setAnswer(event.target.value)}
        error={error}
        disabled={disabled || isSubmitting}
        rows={8}
      />
      <div className="flex justify-end">
        <Button onClick={handleSubmit} isLoading={isSubmitting} disabled={disabled}>
          Submit answer
        </Button>
      </div>
    </div>
  );
}
