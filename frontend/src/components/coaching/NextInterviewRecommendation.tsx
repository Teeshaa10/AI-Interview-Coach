import { Link } from "react-router-dom";
import { ArrowRight, Clock, Code2, ListChecks, MessagesSquare, Mic } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { Card, CardBody, CardHeader } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import type {
  CoachingDifficulty,
  CoachingInterviewType,
  NextInterviewRecommendation as NextInterviewRecommendationData,
} from "@/types/coaching";

const TYPE_ICON: Record<CoachingInterviewType, LucideIcon> = {
  text: MessagesSquare,
  voice: Mic,
  coding: Code2,
};

const DIFFICULTY_TONE: Record<CoachingDifficulty, "success" | "warning" | "danger"> = {
  easy: "success",
  medium: "warning",
  hard: "danger",
};

export function NextInterviewRecommendation({
  recommendation,
}: {
  recommendation: NextInterviewRecommendationData;
}) {
  const Icon = TYPE_ICON[recommendation.interview_type];

  return (
    <Card>
      <CardHeader>
        <h3 className="text-sm font-semibold text-slate-100">Recommended next session</h3>
      </CardHeader>
      <CardBody className="space-y-4">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-500/10">
            <Icon className="h-5 w-5 text-brand-400" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium capitalize text-slate-100">
              {recommendation.interview_type} interview &middot; {recommendation.topic}
            </p>
            <div className="mt-1 flex flex-wrap items-center gap-2">
              <Badge tone={DIFFICULTY_TONE[recommendation.difficulty]}>{recommendation.difficulty}</Badge>
              <span className="flex items-center gap-1 text-xs text-slate-500">
                <Clock className="h-3.5 w-3.5" />
                {recommendation.suggested_duration_minutes} min
              </span>
              <span className="flex items-center gap-1 text-xs text-slate-500">
                <ListChecks className="h-3.5 w-3.5" />
                {recommendation.suggested_number_of_questions} questions
              </span>
            </div>
          </div>
        </div>

        <p className="text-sm text-slate-400">{recommendation.reason}</p>

        <Link to={recommendation.setup_path}>
          <Button variant="primary" className="w-full sm:w-auto">
            Start this session
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
      </CardBody>
    </Card>
  );
}
