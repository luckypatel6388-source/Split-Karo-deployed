import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowRight, RefreshCw } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { settlementsApi } from "@/api/settlements";
import { formatINR } from "@/lib/formatters";
import { useAuthStore } from "@/store/authStore";
import type { SettlementRecord } from "@/types/api";
import { ApiRequestError } from "@/api/client";

export function SettlementsPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const navigate = useNavigate();
  const currentUser = useAuthStore((s) => s.user);

  const [settlements, setSettlements] = useState<SettlementRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);

  const loadSettlements = async () => {
    if (!groupId) return;
    setLoading(true);
    setError(null);
    try {
      const records = await settlementsApi.createOptimizedSettlements(groupId);
      setSettlements(records);
      setLoaded(true);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.detail : "Failed to calculate settlements.");
    } finally {
      setLoading(false);
    }
  };

  const myPending = settlements.filter(
    (s) => s.from_user_id === currentUser?.id && s.status === "pending"
  );
  const othersInvolved = settlements.filter(
    (s) => s.from_user_id !== currentUser?.id || s.status !== "pending"
  );

  return (
    <div>
      <PageHeader title="Settle Up" showBack />
      <div className="px-5 pt-5 flex flex-col gap-5 pb-safe">

        {!loaded && !loading && (
          <div className="flex flex-col items-center gap-4 py-10 text-center">
            <p className="text-sm text-ink-muted max-w-xs">
              Calculate the minimum number of payments needed to settle all balances in this group.
            </p>
            <Button onClick={loadSettlements} size="lg" className="w-full">
              <RefreshCw className="h-4 w-4" aria-hidden />
              Calculate Settlements
            </Button>
          </div>
        )}

        {loading && (
          <div className="flex justify-center py-10">
            <div className="h-8 w-8 rounded-full border-2 border-brand-200 border-t-brand-600 animate-spin" />
          </div>
        )}

        {error && (
          <div className="rounded-xl bg-red-50 border border-red-100 p-4 text-sm text-red-700">{error}</div>
        )}

        {loaded && !loading && settlements.length === 0 && (
          <div className="flex flex-col items-center gap-3 py-10 text-center">
            <p className="text-lg font-bold text-brand-600">All settled up! 🎉</p>
            <p className="text-sm text-ink-muted">No outstanding balances in this group.</p>
          </div>
        )}

        {loaded && settlements.length > 0 && (
          <>
            {myPending.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-ink-muted uppercase tracking-wide mb-2">You need to pay</p>
                <div className="flex flex-col gap-3">
                  {myPending.map((s) => (
                    <Card key={s.id} className="border-amber-200 bg-amber-50/30">
                      <CardContent className="pt-4 pb-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-semibold text-ink">{s.from_user_name}</span>
                            <ArrowRight className="h-3 w-3 text-ink-muted" aria-hidden />
                            <span className="text-sm font-semibold text-ink">{s.to_user_name}</span>
                          </div>
                          <span className="text-base font-bold text-amber-700">{formatINR(s.amount)}</span>
                        </div>
                        <div className="mt-3">
                          <Button
                            size="sm"
                            className="w-full"
                            onClick={() => navigate(`/groups/${groupId}/payment/${s.id}`)}
                          >
                            Pay {formatINR(s.amount)}
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {othersInvolved.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-ink-muted uppercase tracking-wide mb-2">Other settlements</p>
                <div className="flex flex-col gap-2">
                  {othersInvolved.map((s) => (
                    <Card key={s.id}>
                      <CardContent className="pt-4 pb-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-ink">{s.from_user_name}</span>
                            <ArrowRight className="h-3 w-3 text-ink-muted" aria-hidden />
                            <span className="text-sm font-medium text-ink">{s.to_user_name}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-semibold text-ink">{formatINR(s.amount)}</span>
                            <span className={`text-xs px-2 py-0.5 rounded-full ${s.status === "paid" ? "bg-brand-50 text-brand-700" : "bg-amber-50 text-amber-700"}`}>
                              {s.status}
                            </span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            <Button variant="outline" size="sm" className="w-full" onClick={loadSettlements}>
              <RefreshCw className="h-4 w-4" aria-hidden />
              Recalculate
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
