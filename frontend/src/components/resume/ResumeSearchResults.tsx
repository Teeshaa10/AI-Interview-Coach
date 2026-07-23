import { Card, CardBody } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { EmptyState } from "@/components/common/EmptyState";
import { SearchX } from "lucide-react";
import type { SemanticSearchResultChunk } from "@/types/resume";

export function ResumeSearchResults({ results }: { results: SemanticSearchResultChunk[] }) {
  if (results.length === 0) {
    return (
      <EmptyState
        icon={SearchX}
        title="No matches found"
        description="Try a different phrase, or a broader topic from your resume."
      />
    );
  }

  return (
    <div className="space-y-3">
      {results.map((result) => (
        <Card key={result.chunk_id}>
          <CardBody className="pt-5">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs text-slate-500">{result.filename}</span>
              <Badge tone="brand">{Math.round(result.similarity_score * 100)}% match</Badge>
            </div>
            <p className="text-sm leading-relaxed text-slate-200">{result.chunk_text}</p>
          </CardBody>
        </Card>
      ))}
    </div>
  );
}
