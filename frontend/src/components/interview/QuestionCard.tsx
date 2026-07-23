import { Card, CardBody } from "@/components/common/Card";

export function QuestionCard({ question }: { question: string }) {
  return (
    <Card>
      <CardBody className="pt-6">
        <p className="text-base leading-relaxed text-slate-100">{question}</p>
      </CardBody>
    </Card>
  );
}
