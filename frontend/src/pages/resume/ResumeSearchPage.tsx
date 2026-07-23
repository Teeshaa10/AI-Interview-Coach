import { useState } from "react";
import { AlertTriangle } from "lucide-react";

import { ResumeSearchForm } from "@/components/resume/ResumeSearchForm";
import { ResumeSearchResults } from "@/components/resume/ResumeSearchResults";
import { Card, CardBody } from "@/components/common/Card";
import { resumeApi } from "@/api/resumeApi";
import { getApiErrorMessage } from "@/api/client";
import type { SemanticSearchResultChunk } from "@/types/resume";

export function ResumeSearchPage() {
  const [results, setResults] = useState<SemanticSearchResultChunk[] | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    setIsSearching(true);
    setErrorMessage(null);
    try {
      const response = await resumeApi.semanticSearch({ query, top_k: 5 });
      setResults(response.results);
    } catch (error) {
      setResults(null);
      setErrorMessage(getApiErrorMessage(error, "Search failed."));
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Resume search</h1>
        <p className="mt-1 text-sm text-slate-400">
          Semantic search over your resume content, powered by embeddings.
        </p>
      </div>

      <ResumeSearchForm onSearch={handleSearch} isLoading={isSearching} />

      {errorMessage && (
        <Card>
          <CardBody className="flex items-start gap-3 pt-5">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-400" />
            <div>
              <p className="text-sm font-medium text-slate-100">Search is currently unavailable</p>
              <p className="mt-1 text-sm text-slate-400">
                {errorMessage} This backend's embeddings router is not yet registered on the running
                API (see CHECKPOINT.md) - once it is, this page will work without any frontend changes.
              </p>
            </div>
          </CardBody>
        </Card>
      )}

      {results && !errorMessage && <ResumeSearchResults results={results} />}
    </div>
  );
}
