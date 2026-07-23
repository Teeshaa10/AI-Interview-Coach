import { Modal } from "@/components/common/Modal";
import { Button } from "@/components/common/Button";

interface ExitInterviewDialogProps {
  isOpen: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

export function ExitInterviewDialog({ isOpen, onCancel, onConfirm }: ExitInterviewDialogProps) {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onCancel}
      title="Leave this interview?"
      footer={
        <>
          <Button variant="secondary" onClick={onCancel}>
            Stay
          </Button>
          <Button variant="danger" onClick={onConfirm}>
            Leave anyway
          </Button>
        </>
      }
    >
      Your progress on this question won&apos;t be saved if you leave now. Answers you&apos;ve already
      submitted are safe.
    </Modal>
  );
}
