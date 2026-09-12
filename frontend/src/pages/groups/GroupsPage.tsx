import { useState, useEffect } from "react";
import { Users, Plus, ChevronRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { groupsApi } from "@/api/groups";
import type { GroupResponse } from "@/types/api";

export function GroupsPage() {
  const navigate = useNavigate();
  const [groups, setGroups] = useState<GroupResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    groupsApi
      .listMyGroups()
      .then((g) => { setGroups(g); setLoading(false); })
      .catch((e) => { setError(e?.detail ?? "Failed to load groups."); setLoading(false); });
  }, []);

  return (
    <div>
      <PageHeader
        title="Groups"
        right={
          <Button size="sm" variant="ghost" onClick={() => navigate("/groups/new")} aria-label="Create group">
            <Plus className="h-5 w-5" aria-hidden />
          </Button>
        }
      />
      <div className="px-5 pt-4 flex flex-col gap-3">
        {loading && (
          <div className="flex justify-center py-12">
            <div className="h-6 w-6 rounded-full border-2 border-brand-200 border-t-brand-600 animate-spin" />
          </div>
        )}

        {!loading && error && (
          <div className="rounded-xl bg-red-50 border border-red-100 p-4 text-sm text-red-700">{error}</div>
        )}

        {!loading && !error && groups.length === 0 && (
          <div className="flex flex-col items-center gap-3 py-12 text-center">
            <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50">
              <Users className="h-7 w-7 text-brand-600" aria-hidden />
            </span>
            <p className="text-sm font-semibold text-ink">No groups yet</p>
            <p className="text-xs text-ink-muted">Create a group to start splitting expenses with friends.</p>
            <Button onClick={() => navigate("/groups/new")}>
              <Plus className="h-4 w-4" aria-hidden />
              Create Group
            </Button>
          </div>
        )}

        {!loading && !error && groups.map((g) => (
          <button
            key={g.id}
            onClick={() => navigate(`/groups/${g.id}`)}
            className="flex items-center justify-between w-full rounded-2xl bg-surface-card border border-border/40 shadow-card px-4 py-4 active:scale-[0.98] transition-transform text-left"
          >
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-700 font-bold text-sm shrink-0">
                {g.name.charAt(0).toUpperCase()}
              </span>
              <div>
                <p className="text-sm font-semibold text-ink">{g.name}</p>
                <p className="text-xs text-ink-muted">{g.members.length} member{g.members.length !== 1 ? "s" : ""}</p>
              </div>
            </div>
            <ChevronRight className="h-4 w-4 text-ink-subtle" aria-hidden />
          </button>
        ))}
      </div>
    </div>
  );
}
