import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Plus, ScanLine, ArrowRightLeft, Receipt, Share2, Link2, QrCode, X, Check } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { groupsApi } from "@/api/groups";
import { expensesApi } from "@/api/expenses";
import { balancesApi } from "@/api/balances";
import { formatINR, balanceDirection } from "@/lib/formatters";
import { useAuthStore } from "@/store/authStore";
import type { GroupResponse, ExpenseHistoryItem, UserBalance } from "@/types/api";
import type { CreateInviteResponse } from "@/types/api";
import { ApiRequestError } from "@/api/client";
import { QRCodeSVG } from "qrcode.react";

export function GroupDetailPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const navigate = useNavigate();
  const currentUser = useAuthStore((s) => s.user);

  const [group, setGroup] = useState<GroupResponse | null>(null);
  const [expenses, setExpenses] = useState<ExpenseHistoryItem[]>([]);
  const [balances, setBalances] = useState<UserBalance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [invite, setInvite] = useState<CreateInviteResponse | null>(null);
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteError, setInviteError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const load = useCallback(async () => {
    if (!groupId) return;
    setLoading(true);
    setError(null);
    try {
      const [g, e, b] = await Promise.all([
        groupsApi.getGroup(groupId),
        expensesApi.listGroupExpenses(groupId),
        balancesApi.getGroupBalances(groupId),
      ]);
      setGroup(g);
      setExpenses(e);
      setBalances(b.balances);
    } catch (err: unknown) {
      const msg = err instanceof Error ? (err as { detail?: string }).detail ?? err.message : "Failed to load group.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => { load(); }, [load]);

  const handleCreateInvite = async () => {
    if (!groupId) return;
    setInviteLoading(true);
    setInviteError(null);
    try {
      setInvite(await groupsApi.createInvite(groupId));
    } catch (err) {
      setInviteError(err instanceof ApiRequestError ? err.detail : "Could not create invite.");
    } finally {
      setInviteLoading(false);
    }
  };

  const inviteLink = invite
    ? `${window.location.origin}/#${invite.invite_url}`
    : "";

  const copyInvite = async () => {
    await navigator.clipboard.writeText(inviteLink);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  };

  const shareInvite = async () => {
    try {
      if (navigator.share) {
        await navigator.share({ title: `Join ${group?.name ?? "our group"}`, url: inviteLink });
      } else {
        await copyInvite();
      }
    } catch {
      // Sharing can be cancelled by the user; the invite remains available to copy.
    }
  };

  if (loading) return (
    <div className="flex justify-center items-center min-h-[60vh]">
      <div className="h-8 w-8 rounded-full border-2 border-brand-200 border-t-brand-600 animate-spin" />
    </div>
  );

  if (error) return (
    <div>
      <PageHeader title="Group" showBack />
      <div className="px-5 pt-4 rounded-xl bg-red-50 border border-red-100 p-4 text-sm text-red-700 mx-5 mt-4">{error}</div>
    </div>
  );

  if (!group) return null;

  const myBalance = balances.find((b) => b.user_id === currentUser?.id);
  const dir = balanceDirection(myBalance?.balance);

  return (
    <div className="pb-safe">
      <PageHeader title={group.name} showBack />

      <div className="px-5 pt-4 flex flex-col gap-5">
        {currentUser?.id === group.created_by && (
          <Card className="border-brand-200 bg-brand-50/40">
            <CardContent className="pt-5 pb-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-ink">Invite people</p>
                  <p className="text-xs text-ink-muted mt-1">Share a link or QR code to add members.</p>
                </div>
                {invite && (
                  <Button variant="ghost" size="icon" onClick={() => setInvite(null)} aria-label="Close invite">
                    <X className="h-4 w-4" aria-hidden />
                  </Button>
                )}
              </div>

              {!invite && (
                <Button size="sm" className="mt-4" onClick={handleCreateInvite} disabled={inviteLoading}>
                  <QrCode className="h-4 w-4" aria-hidden />
                  {inviteLoading ? "Creating link…" : "Create invite link"}
                </Button>
              )}

              {inviteError && <p className="mt-3 text-xs text-red-600">{inviteError}</p>}

              {invite && (
                <div className="mt-4 flex flex-col gap-4">
                  <div className="flex justify-center rounded-2xl bg-white p-4">
                    <QRCodeSVG value={inviteLink} size={176} includeMargin aria-label="Group invite QR code" />
                  </div>
                  <div className="rounded-xl bg-white/80 border border-brand-100 p-3">
                    <p className="text-[11px] text-ink-muted mb-1">Invite link</p>
                    <p className="text-xs text-ink break-all">{inviteLink}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <Button variant="outline" size="sm" onClick={copyInvite}>
                      {copied ? <Check className="h-4 w-4" aria-hidden /> : <Link2 className="h-4 w-4" aria-hidden />}
                      {copied ? "Copied" : "Copy link"}
                    </Button>
                    <Button variant="outline" size="sm" onClick={shareInvite}>
                      <Share2 className="h-4 w-4" aria-hidden />
                      Share
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* My balance card */}
        <Card>
          <CardContent className="pt-5 pb-4">
            <p className="text-xs text-ink-muted font-medium mb-1">Your balance</p>
            {myBalance ? (
              <div className="flex items-baseline gap-2">
                <span className={`text-2xl font-bold ${dir === "receive" ? "text-brand-600" : dir === "owe" ? "text-amber-700" : "text-ink"}`}>
                  {formatINR(myBalance.balance)}
                </span>
                <span className="text-sm text-ink-muted">
                  {dir === "receive" ? "you're owed" : dir === "owe" ? "you owe" : "settled up"}
                </span>
              </div>
            ) : (
              <p className="text-sm text-ink-muted">No balance data</p>
            )}
          </CardContent>
        </Card>

        {/* Action buttons */}
        <div className="grid grid-cols-3 gap-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-col h-16 gap-1"
            onClick={() => navigate(`/groups/${groupId}/scan`)}
          >
            <ScanLine className="h-4 w-4" aria-hidden />
            <span className="text-xs">Scan Bill</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="flex-col h-16 gap-1"
            onClick={() => navigate(`/groups/${groupId}/expense`)}
          >
            <Plus className="h-4 w-4" aria-hidden />
            <span className="text-xs">Add Expense</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="flex-col h-16 gap-1"
            onClick={() => navigate(`/groups/${groupId}/settlements`)}
          >
            <ArrowRightLeft className="h-4 w-4" aria-hidden />
            <span className="text-xs">Settle Up</span>
          </Button>
        </div>

        {/* All balances */}
        {balances.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-ink-muted uppercase tracking-wide mb-2">Balances</p>
            <Card>
              <CardContent className="pt-4 pb-2">
                {balances.map((b) => {
                  const d = balanceDirection(b.balance);
                  return (
                    <div key={b.user_id} className="flex items-center justify-between py-2 border-b border-border/30 last:border-0">
                      <span className="text-sm text-ink">{b.user_name}</span>
                      <span className={`text-sm font-semibold ${d === "receive" ? "text-brand-600" : d === "owe" ? "text-amber-700" : "text-ink-muted"}`}>
                        {d === "settled" ? "Settled" : formatINR(b.balance)}
                      </span>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Members */}
        <div>
          <p className="text-xs font-semibold text-ink-muted uppercase tracking-wide mb-2">
            Members ({group.members.length})
          </p>
          <Card>
            <CardContent className="pt-4 pb-2">
              {group.members.map((m) => (
                <div key={m.id} className="flex items-center justify-between py-2 border-b border-border/30 last:border-0">
                  <div className="flex items-center gap-2">
                    <span className="h-7 w-7 rounded-full bg-brand-50 flex items-center justify-center text-brand-700 text-xs font-semibold">
                      {m.name.charAt(0).toUpperCase()}
                    </span>
                    <span className="text-sm text-ink">{m.name}</span>
                  </div>
                  <span className="text-xs text-ink-subtle capitalize">{m.role}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Expenses */}
        <div>
          <p className="text-xs font-semibold text-ink-muted uppercase tracking-wide mb-2">
            Expenses ({expenses.length})
          </p>
          {expenses.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-8 text-center">
              <Receipt className="h-8 w-8 text-ink-subtle" aria-hidden />
              <p className="text-sm text-ink-muted">No expenses yet</p>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              {expenses.map((e) => (
                <Card key={e.expense_id}>
                  <CardContent className="pt-4 pb-4">
                    <button
                      className="flex items-center justify-between w-full text-left"
                      onClick={() => navigate(`/expenses/${e.expense_id}`)}
                    >
                      <div>
                        <p className="text-sm font-semibold text-ink">{e.title}</p>
                        <p className="text-xs text-ink-muted">
                          Paid by {e.payer_name}
                        </p>
                      </div>
                      <p className="text-sm font-semibold text-ink">{formatINR(e.amount)}</p>
                    </button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
