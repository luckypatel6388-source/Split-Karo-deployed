import { useState, useEffect } from "react";
import { ScanLine, Users, Plus, ChevronRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { groupsApi } from "@/api/groups";
import { formatINR, balanceDirection } from "@/lib/formatters";
import { balancesApi } from "@/api/balances";
import type { GroupResponse, UserBalance } from "@/types/api";

/** Fetch a group's balance for the current user and return it. */
function useGroupBalance(groupId: string, userId: string) {
  const [balance, setBalance] = useState<UserBalance | null>(null);
  useEffect(() => {
    balancesApi
      .getGroupBalances(groupId)
      .then((res) => {
        const me = res.balances.find((b) => b.user_id === userId);
        setBalance(me ?? null);
      })
      .catch(() => setBalance(null));
  }, [groupId, userId]);
  return balance;
}

function GroupCard({ group, userId }: { group: GroupResponse; userId: string }) {
  const navigate = useNavigate();
  const balance = useGroupBalance(group.id, userId);
  const dir = balanceDirection(balance?.balance);

  return (
    <button
      onClick={() => navigate(`/groups/${group.id}`)}
      className="flex items-center justify-between w-full rounded-2xl bg-surface-card border border-border/40 shadow-card px-4 py-4 active:scale-[0.98] transition-transform text-left"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-700 font-bold text-sm shrink-0">
          {group.name.charAt(0).toUpperCase()}
        </span>
        <div>
          <p className="text-sm font-semibold text-ink">{group.name}</p>
          <p className="text-xs text-ink-muted">{group.members.length} member{group.members.length !== 1 ? "s" : ""}</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {balance && dir !== "settled" && (
          <span className={dir === "receive" ? "balance-positive" : "balance-negative"}>
            {dir === "receive" ? "+" : "-"}{formatINR(Math.abs(parseFloat(balance.balance)).toString())}
          </span>
        )}
        {dir === "settled" && <span className="text-xs text-ink-subtle">Settled</span>}
        <ChevronRight className="h-4 w-4 text-ink-subtle" aria-hidden />
      </div>
    </button>
  );
}

export function HomePage() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const [groups, setGroups] = useState<GroupResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  useEffect(() => {
    groupsApi
      .listMyGroups()
      .then((g) => { setGroups(g); setLoading(false); })
      .catch((e) => { setError(e?.detail ?? "Failed to load groups"); setLoading(false); });
  }, []);

  return (
    <div className="flex flex-col min-h-dvh bg-surface pb-safe">
      {/* Top bar */}
      <header className="flex items-center justify-between px-5 pt-5 pb-2">
        <div>
          <p className="text-xs text-ink-muted font-medium">{greeting},</p>
          <h1 className="text-xl font-bold text-ink">
            {user?.name?.split(" ")[0] ?? "there"} 👋
          </h1>
        </div>
        <button
          onClick={() => navigate("/profile")}
          className="h-9 w-9 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 font-semibold text-sm"
          aria-label="Profile"
        >
          {user?.name?.charAt(0)?.toUpperCase() ?? "?"}
        </button>
      </header>

      {/* Hero — Scan Bill */}
      <section className="px-5 pt-3 pb-2">
        <Card className="relative overflow-hidden bg-gradient-to-br from-brand-600 to-brand-700 border-0 text-white p-6">
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <ScanLine className="h-5 w-5 opacity-80" aria-hidden />
              <span className="text-sm font-medium opacity-80">AI Bill Scanner</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold leading-tight">
                Scan a bill.<br />Split in seconds.
              </h2>
              <p className="text-sm opacity-75 mt-1">
                AI extracts every item — you review, confirm, done.
              </p>
            </div>
            <Button
              size="sm"
              className="bg-white text-brand-700 hover:bg-brand-50 rounded-xl font-semibold w-fit"
              onClick={() => navigate("/scan")}
            >
              <ScanLine className="h-4 w-4" aria-hidden />
              Scan Bill
            </Button>
          </div>
          <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-white/10" />
          <div className="absolute -right-4 -bottom-10 h-24 w-24 rounded-full bg-white/5" />
        </Card>
      </section>

      {/* My Groups */}
      <section className="px-5 pt-5 flex-1">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-semibold text-ink">My Groups</p>
          <button
            onClick={() => navigate("/groups/new")}
            className="flex items-center gap-1 text-xs text-brand-600 font-medium"
          >
            <Plus className="h-3.5 w-3.5" aria-hidden />
            New Group
          </button>
        </div>

        {loading && (
          <div className="flex justify-center py-10">
            <div className="h-6 w-6 rounded-full border-2 border-brand-200 border-t-brand-600 animate-spin" />
          </div>
        )}

        {!loading && error && (
          <div className="rounded-xl bg-red-50 border border-red-100 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && groups.length === 0 && (
          <div className="flex flex-col items-center gap-3 py-10 text-center">
            <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50">
              <Users className="h-7 w-7 text-brand-600" aria-hidden />
            </span>
            <p className="text-sm font-semibold text-ink">No groups yet</p>
            <p className="text-xs text-ink-muted">Create a group to start splitting expenses.</p>
            <Button size="sm" onClick={() => navigate("/groups/new")}>
              <Plus className="h-4 w-4" aria-hidden />
              Create Group
            </Button>
          </div>
        )}

        {!loading && !error && groups.length > 0 && (
          <div className="flex flex-col gap-3">
            {groups.map((g) => (
              <GroupCard key={g.id} group={g} userId={user?.id ?? ""} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
