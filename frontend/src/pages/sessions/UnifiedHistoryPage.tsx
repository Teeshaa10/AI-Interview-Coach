import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Code2, History, MessagesSquare, Mic, Star, Trash2 } from "lucide-react";
import toast from "react-hot-toast";
import clsx from "clsx";

import { getApiErrorMessage } from "@/api/client";
import { sessionsApi } from "@/api/sessionsApi";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Card, CardBody } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { Spinner } from "@/components/common/Spinner";
import type { HistoryQueryParams, SessionType, UnifiedSessionItem } from "@/types/sessions";
import { formatDate } from "@/utils/format";
import { scoreTone } from "@/utils/score";

const TYPE_ICON: Record<SessionType, typeof MessagesSquare> = {
  text: MessagesSquare,
  voice: Mic,
  coding: Code2,
};

const TYPE_LABEL: Record<SessionType, string> = {
  text: "Text",
  voice: "Voice",
  coding: "Coding",
};

const LIMIT = 20;

export function UnifiedHistoryPage() {
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [type, setType] = useState<HistoryQueryParams["type"]>("all");
  const [status, setStatus] = useState<HistoryQueryParams["status"]>("all");
  const [favoriteOnly, setFavoriteOnly] = useState(false);
  const [sortBy, setSortBy] = useState<HistoryQueryParams["sort_by"]>("created_at");
  const [sortDir, setSortDir] = useState<HistoryQueryParams["sort_dir"]>("desc");
  const [page, setPage] = useState(1);

  const params: HistoryQueryParams = {
    type,
    status,
    search: search || undefined,
    favorite_only: favoriteOnly,
    sort_by: sortBy,
    sort_dir: sortDir,
    page,
    limit: LIMIT,
  };

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ["sessions", "history", params],
    queryFn: () => sessionsApi.history(params),
    placeholderData: (previous) => previous,
  });

  const favoriteMutation = useMutation({
    mutationFn: ({ item, favorite }: { item: UnifiedSessionItem; favorite: boolean }) =>
      sessionsApi.setFavorite(item.type, item.session_id, favorite),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sessions", "history"] });
    },
    onError: (error: unknown) => {
      toast.error(getApiErrorMessage(error, "Could not update favorite."));
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (item: UnifiedSessionItem) => sessionsApi.deleteSession(item.type, item.session_id),
    onSuccess: () => {
      toast.success("Session deleted.");
      queryClient.invalidateQueries({ queryKey: ["sessions", "history"] });
      queryClient.invalidateQueries({ queryKey: ["sessions", "analytics"] });
    },
    onError: (error: unknown) => {
      toast.error(getApiErrorMessage(error, "Could not delete session."));
    },
  });

  const sessions = data?.sessions ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / LIMIT));

  function updateFilter<K extends keyof HistoryQueryParams>(setter: (value: HistoryQueryParams[K]) => void) {
    return (value: HistoryQueryParams[K]) => {
      setter(value);
      setPage(1);
    };
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Interview history</h1>
        <p className="mt-1 text-sm text-slate-400">
          Every text, voice, and coding session in one place - search, filter, resume, or clean up.
        </p>
      </div>

      <Card>
        <CardBody className="flex flex-wrap items-center gap-3 pt-5">
          <input
            type="search"
            value={search}
            onChange={(event) => {
              setSearch(event.target.value);
              setPage(1);
            }}
            placeholder="Search by role or topic..."
            className="w-full min-w-[200px] flex-1 rounded-lg border border-surface-600 bg-surface-800 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-brand-400 focus:outline-none"
          />

          <select
            value={type}
            onChange={(event) => updateFilter<"type">(setType)(event.target.value as HistoryQueryParams["type"])}
            className="rounded-lg border border-surface-600 bg-surface-800 px-3 py-2 text-sm text-slate-100 focus:border-brand-400 focus:outline-none"
          >
            <option value="all">All types</option>
            <option value="text">Text</option>
            <option value="voice">Voice</option>
            <option value="coding">Coding</option>
          </select>

          <select
            value={status}
            onChange={(event) => updateFilter<"status">(setStatus)(event.target.value as HistoryQueryParams["status"])}
            className="rounded-lg border border-surface-600 bg-surface-800 px-3 py-2 text-sm text-slate-100 focus:border-brand-400 focus:outline-none"
          >
            <option value="all">All statuses</option>
            <option value="in_progress">In progress</option>
            <option value="completed">Completed</option>
          </select>

          <select
            value={`${sortBy}:${sortDir}`}
            onChange={(event) => {
              const [nextSortBy, nextSortDir] = event.target.value.split(":") as [
                HistoryQueryParams["sort_by"],
                HistoryQueryParams["sort_dir"],
              ];
              setSortBy(nextSortBy);
              setSortDir(nextSortDir);
              setPage(1);
            }}
            className="rounded-lg border border-surface-600 bg-surface-800 px-3 py-2 text-sm text-slate-100 focus:border-brand-400 focus:outline-none"
          >
            <option value="created_at:desc">Newest first</option>
            <option value="created_at:asc">Oldest first</option>
            <option value="score:desc">Highest score</option>
            <option value="score:asc">Lowest score</option>
            <option value="title:asc">Title A-Z</option>
          </select>

          <button
            type="button"
            onClick={() => {
              setFavoriteOnly((prev) => !prev);
              setPage(1);
            }}
            className={clsx(
              "inline-flex items-center gap-1.5 rounded-lg border px-3 py-2 text-sm font-medium transition-colors",
              favoriteOnly
                ? "border-amber-500/40 bg-amber-500/10 text-amber-300"
                : "border-surface-600 bg-surface-800 text-slate-300 hover:text-slate-100",
            )}
          >
            <Star className={clsx("h-4 w-4", favoriteOnly && "fill-amber-400")} />
            Favorites
          </button>
        </CardBody>
      </Card>

      {isLoading && <Spinner label="Loading history..." />}

      {!isLoading && sessions.length === 0 && (
        <EmptyState
          icon={History}
          title="No sessions match these filters"
          description="Try clearing a filter, or start a new practice session."
        />
      )}

      {!isLoading && sessions.length > 0 && (
        <div className={clsx("space-y-3", isFetching && "opacity-60")}>
          {sessions.map((item) => {
            const Icon = TYPE_ICON[item.type];
            return (
              <Card key={`${item.type}-${item.session_id}`}>
                <CardBody className="flex flex-wrap items-center justify-between gap-4 pt-5">
                  <div className="flex min-w-0 items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-surface-800">
                      <Icon className="h-4.5 w-4.5 text-slate-300" />
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-slate-100">{item.title}</p>
                      <p className="mt-0.5 text-xs text-slate-500">
                        {TYPE_LABEL[item.type]} &middot; {item.subtitle} &middot; {formatDate(item.created_at)}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    {item.status === "completed" ? (
                      <Badge tone={scoreTone(item.score ?? 0)}>{(item.score ?? 0).toFixed(1)} avg</Badge>
                    ) : (
                      <Badge tone="warning">In progress</Badge>
                    )}
                    {item.has_report && <Badge tone="brand">Report ready</Badge>}

                    <button
                      type="button"
                      title={item.favorite ? "Remove favorite" : "Mark favorite"}
                      onClick={() => favoriteMutation.mutate({ item, favorite: !item.favorite })}
                      className="rounded-lg p-2 text-slate-400 hover:bg-surface-800 hover:text-amber-300"
                    >
                      <Star className={clsx("h-4 w-4", item.favorite && "fill-amber-400 text-amber-400")} />
                    </button>

                    {item.resumable && item.resume_path ? (
                      <Link to={item.resume_path}>
                        <Button variant="secondary" size="sm">
                          {item.status === "completed" ? "View report" : "Resume"}
                        </Button>
                      </Link>
                    ) : (
                      <Button variant="secondary" size="sm" disabled>
                        {item.status === "completed" ? "No report yet" : "Not resumable"}
                      </Button>
                    )}

                    <button
                      type="button"
                      title="Delete session"
                      onClick={() => {
                        if (window.confirm(`Delete this ${TYPE_LABEL[item.type].toLowerCase()} session? This can't be undone.`)) {
                          deleteMutation.mutate(item);
                        }
                      }}
                      className="rounded-lg p-2 text-slate-400 hover:bg-red-500/10 hover:text-red-400"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </CardBody>
              </Card>
            );
          })}
        </div>
      )}

      {!isLoading && totalPages > 1 && (
        <div className="flex items-center justify-between text-sm text-slate-400">
          <span>
            Page {page} of {totalPages} &middot; {total} session{total === 1 ? "" : "s"}
          </span>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              Previous
            </Button>
            <Button variant="secondary" size="sm" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
