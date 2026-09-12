import { Activity, ArrowRight, Receipt, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { groupsApi } from "@/api/groups";
import { expensesApi } from "@/api/expenses";
import { formatINR } from "@/lib/formatters";
import type { ExpenseHistoryItem } from "@/types/api";

interface ActivityItem extends ExpenseHistoryItem {
  groupId: string;
  groupName: string;
}

export function ActivityPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadActivity = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    setError(null);
    try {
      const groups = await groupsApi.listMyGroups();
      const results = await Promise.allSettled(groups.map(async (group) => {
        const expenses = await expensesApi.listGroupExpenses(group.id);
        return expenses.map((expense) => ({ ...expense, groupId: group.id, groupName: group.name }));
      }));
      const activity = results.flatMap((result) => result.status === "fulfilled" ? result.value : []);
      setItems(activity);
      if (activity.length === 0 && results.some((result) => result.status === "rejected")) setError("Could not load activity right now.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load activity right now.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { void loadActivity(); }, [loadActivity]);

  useEffect(() => {
    const refresh = () => {
      if (!document.hidden) void loadActivity(true);
    };
    const interval = window.setInterval(refresh, 30_000);
    return () => window.clearInterval(interval);
  }, [loadActivity]);

  return (
    <div>
      <PageHeader title="Activity" right={<Button variant="ghost" size="icon" onClick={() => void loadActivity(true)} disabled={refreshing} aria-label="Refresh activity"><RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} aria-hidden /></Button>} />
      <div className="px-5 pt-4 pb-safe">
        {loading && <div className="flex justify-center py-12"><div className="h-7 w-7 rounded-full border-2 border-brand-200 border-t-brand-600 animate-spin" /></div>}
        {error && <div className="rounded-xl bg-red-50 border border-red-100 p-4 text-sm text-red-700">{error}</div>}
        {!loading && !error && items.length === 0 && <div className="flex flex-col items-center gap-3 py-12 text-center"><Activity className="h-10 w-10 text-ink-subtle" aria-hidden /><p className="text-sm font-semibold text-ink">No activity yet</p><p className="text-xs text-ink-muted">Your group expenses will appear here.</p></div>}
        {!loading && items.length > 0 && <div className="flex flex-col gap-3">{items.map((item) => <Card key={`${item.groupId}-${item.expense_id}`}><CardContent className="p-4"><button className="flex w-full items-center gap-3 text-left" onClick={() => navigate(`/expenses/${item.expense_id}`)}><span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-600"><Receipt className="h-5 w-5" aria-hidden /></span><span className="min-w-0 flex-1"><span className="block truncate text-sm font-semibold text-ink">{item.title}</span><span className="mt-1 block truncate text-xs text-ink-muted">{item.groupName} · Paid by {item.payer_name}</span></span><span className="flex items-center gap-2 text-sm font-semibold text-ink">{formatINR(item.amount)}<ArrowRight className="h-4 w-4 text-ink-subtle" aria-hidden /></span></button></CardContent></Card>)}</div>}
      </div>
    </div>
  );
}
