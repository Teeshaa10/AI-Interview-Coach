import { useState, type FormEvent } from "react";
import { Search } from "lucide-react";

import { Input } from "@/components/common/FormControls";
import { Button } from "@/components/common/Button";

interface ResumeSearchFormProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
}

export function ResumeSearchForm({ onSearch, isLoading }: ResumeSearchFormProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (trimmed) onSearch(trimmed);
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row">
      <div className="flex-1">
        <Input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="e.g. experience with distributed systems"
          aria-label="Search your resume"
        />
      </div>
      <Button type="submit" isLoading={isLoading} disabled={!query.trim()}>
        <Search className="h-4 w-4" />
        Search
      </Button>
    </form>
  );
}
