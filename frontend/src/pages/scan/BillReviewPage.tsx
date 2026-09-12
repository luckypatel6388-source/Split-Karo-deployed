import { useState, useEffect } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { AlertTriangle, CheckCircle } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { groupsApi } from "@/api/groups";
import { expensesApi } from "@/api/expenses";
import { ApiRequestError } from "@/api/client";
import { formatINR } from "@/lib/formatters";
import { useAuthStore } from "@/store/authStore";
import type { BillScanResponse, GroupMemberResponse } from "@/types/api";

interface LocationState {
  scanResult: BillScanResponse;
  groupId: string | null;
}

export function BillReviewPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { groupId: paramGroupId } = useParams<{ groupId?: string }>();
  const currentUser = useAuthStore((s) => s.user);

  const state = location.state as LocationState | null;
  const scanResult = state?.scanResult;
  const groupId = paramGroupId ?? state?.groupId ?? null;

  const [title, setTitle] = useState("");
  const [total, setTotal] = useState("");
  const [members, setMembers] = useState<GroupMemberResponse[]>([]);
  const [paidBy, setPaidBy] = useState("");
  const [selectedParticipants, setSelectedParticipants] = useState<string[]>([]);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  // If no scan result, redirect back
  useEffect(() => {
    if (!scanResult) {
      navigate(groupId ? `/groups/${groupId}/scan` : "/scan", { replace: true });
      return;
    }
    // Pre-fill from scan result
    setTitle(scanResult.result.merchant_name ?? "");
    setTotal(scanResult.result.total ?? "");
  }, [scanResult, navigate, groupId]);

  useEffect(() => {
    if (!groupId) return;
    groupsApi.getGroup(groupId).then((g) => {
      setMembers(g.members);
      const me = g.members.find((m) => m.user_id === currentUser?.id);
      if (me) setPaidBy(me.user_id);
      setSelectedParticipants(g.members.map((m) => m.user_id));
    }).catch(() => {});
  }, [groupId, currentUser?.id]);

  const toggleParticipant = (uid: string) =>
    setSelectedParticipants((p) => p.includes(uid) ? p.filter((x) => x !== uid) : [...p, uid]);

  const handleConfirm = async () => {
    if (!groupId) {
      // No group context — go to group selection flow
      navigate("/groups", { state: { pendingExpense: { title, amount: total } } });
      return;
    }
    if (!title.trim()) { setError("Enter a title for this expense."); return; }
    if (!total || parseFloat(total) <= 0) { setError("Enter a valid total amount."); return; }
    if (!paidBy) { setError("Select who paid."); return; }
    if (selectedParticipants.length === 0) { setError("Select at least one participant."); return; }

    setError(null);
    setCreating(true);
    try {
      await expensesApi.createExpense(groupId, {
        title: title.trim(),
        amount: parseFloat(total).toFixed(2),
        paid_by: paidBy,
        split_type: "equal",
        participant_user_ids: selectedParticipants,
      });
      setDone(true);
      setTimeout(() => navigate(`/groups/${groupId}`, { replace: true }), 1200);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.detail : "Failed to create expense.");
      setCreating(false);
    }
  };

  if (!scanResult) return null;

  const { result } = scanResult;
  const lowConfidence = result.confidence < 0.5;

  if (done) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 px-5">
        <CheckCircle className="h-16 w-16 text-brand-600" aria-hidden />
        <p className="text-lg font-bold text-ink">Expense created!</p>
        <p className="text-sm text-ink-muted">Redirecting to group…</p>
      </div>
    );
  }

  return (
    <div>
      <PageHeader title="Review Bill" showBack />
      <div className="px-5 pt-4 flex flex-col gap-5 pb-safe">

        {/* Confidence warning */}
        {(lowConfidence || result.warnings.length > 0) && (
          <div className="rounded-xl bg-amber-50 border border-amber-200 p-4 flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-700 shrink-0 mt-0.5" aria-hidden />
            <div className="text-sm text-amber-800">
              <p className="font-semibold">Please review carefully</p>
              {lowConfidence && <p>AI confidence is low ({Math.round(result.confidence * 100)}%). Verify all values.</p>}
              {result.warnings.map((w, i) => <p key={i}>{w}</p>)}
            </div>
          </div>
        )}

        {/* Extracted summary */}
        <Card>
          <CardContent className="pt-4 pb-4 flex flex-col gap-3">
            <p className="text-xs font-semibold text-ink-muted uppercase tracking-wide">Extracted from bill</p>
            {result.merchant_name && (
              <div className="flex justify-between text-sm">
                <span className="text-ink-muted">Merchant</span>
                <span className="font-medium text-ink">{result.merchant_name}</span>
              </div>
            )}
            {result.bill_date && (
              <div className="flex justify-between text-sm">
                <span className="text-ink-muted">Date</span>
                <span className="text-ink">{result.bill_date}</span>
              </div>
            )}
            {result.subtotal && (
              <div className="flex justify-between text-sm">
                <span className="text-ink-muted">Subtotal</span>
                <span className="text-ink">{formatINR(result.subtotal)}</span>
              </div>
            )}
            {result.tax && (
              <div className="flex justify-between text-sm">
                <span className="text-ink-muted">Tax</span>
                <span className="text-ink">{formatINR(result.tax)}</span>
              </div>
            )}
            {result.discount && (
              <div className="flex justify-between text-sm">
                <span className="text-ink-muted">Discount</span>
                <span className="text-ink">-{formatINR(result.discount)}</span>
              </div>
            )}
            <div className="flex justify-between text-sm font-semibold border-t border-border/40 pt-2 mt-1">
              <span className="text-ink">Total</span>
              <span className="text-ink">{result.total ? formatINR(result.total) : "—"}</span>
            </div>
          </CardContent>
        </Card>

        {/* Items */}
        {result.items.length > 0 && (
          <Card>
            <CardContent className="pt-4 pb-2">
              <p className="text-xs font-semibold text-ink-muted uppercase tracking-wide mb-3">Items</p>
              {result.items.map((item, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-border/30 last:border-0">
                  <div>
                    <p className="text-sm text-ink">{item.name}</p>
                    <p className="text-xs text-ink-muted">
                      {item.quantity} × {formatINR(item.unit_price)}
                    </p>
                  </div>
                  <p className="text-sm font-medium text-ink">{formatINR(item.total_price)}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Editable fields for expense creation */}
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="exp-title">Expense title *</Label>
          <Input id="exp-title" value={title} onChange={(e) => setTitle(e.target.value)}
            placeholder="Merchant or description" />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="exp-total">Total amount (₹) *</Label>
          <Input id="exp-total" type="number" min="0.01" step="0.01"
            value={total} onChange={(e) => setTotal(e.target.value)} placeholder="0.00" />
        </div>

        {/* Paid by (only shown when groupId is available) */}
        {groupId && members.length > 0 && (
          <div className="flex flex-col gap-1.5">
            <Label>Paid by *</Label>
            <div className="flex flex-wrap gap-2">
              {members.map((m) => (
                <button key={m.user_id} type="button" onClick={() => setPaidBy(m.user_id)}
                  className={`px-3 py-1.5 rounded-xl text-sm font-medium border transition-colors ${
                    paidBy === m.user_id ? "bg-brand-600 text-white border-brand-600" : "bg-surface-card border-border text-ink"
                  }`}>
                  {m.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Participants */}
        {groupId && members.length > 0 && (
          <div className="flex flex-col gap-2">
            <Label>Split equally among</Label>
            <Card>
              <CardContent className="pt-3 pb-2">
                {members.map((m) => (
                  <div key={m.user_id} className="flex items-center gap-2 py-2 border-b border-border/30 last:border-0">
                    <input type="checkbox" id={`rp-${m.user_id}`}
                      checked={selectedParticipants.includes(m.user_id)}
                      onChange={() => toggleParticipant(m.user_id)}
                      className="h-4 w-4 accent-brand-600" />
                    <label htmlFor={`rp-${m.user_id}`} className="text-sm text-ink">{m.name}</label>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        )}

        {error && (
          <div className="rounded-xl bg-red-50 border border-red-100 p-4 text-sm text-red-700">{error}</div>
        )}

        {/* Confirm CTA */}
        <div className="flex flex-col gap-2 pt-2">
          <Button size="lg" className="w-full" onClick={handleConfirm} disabled={creating}>
            {creating ? "Creating expense…" : groupId ? "Confirm & Create Expense" : "Confirm & Select Group"}
          </Button>
          <p className="text-xs text-ink-muted text-center">
            Review all amounts before confirming. This will create an expense.
          </p>
        </div>
      </div>
    </div>
  );
}
