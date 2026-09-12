import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { groupsApi } from "@/api/groups";
import { expensesApi } from "@/api/expenses";
import { ApiRequestError } from "@/api/client";
import { formatINR } from "@/lib/formatters";
import { useAuthStore } from "@/store/authStore";
import type { GroupMemberResponse } from "@/types/api";

interface LocationState {
  prefill?: {
    title: string;
    amount: string;
  };
}

export function CreateExpensePage() {
  const { groupId } = useParams<{ groupId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const currentUser = useAuthStore((s) => s.user);
  const state = location.state as LocationState | null;

  const [members, setMembers] = useState<GroupMemberResponse[]>([]);
  const [title, setTitle] = useState(state?.prefill?.title ?? "");
  const [amount, setAmount] = useState(state?.prefill?.amount ?? "");
  const [paidBy, setPaidBy] = useState("");
  const [splitType, setSplitType] = useState<"equal" | "custom">("equal");
  const [selectedParticipants, setSelectedParticipants] = useState<string[]>([]);
  const [customShares, setCustomShares] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [loadingMembers, setLoadingMembers] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!groupId) return;
    groupsApi.getGroup(groupId).then((g) => {
      setMembers(g.members);
      // Default payer = current user if they are a member
      const me = g.members.find((m) => m.user_id === currentUser?.id);
      if (me) setPaidBy(me.user_id);
      // Default: select all members
      setSelectedParticipants(g.members.map((m) => m.user_id));
      setLoadingMembers(false);
    }).catch(() => setLoadingMembers(false));
  }, [groupId, currentUser?.id]);

  const toggleParticipant = (userId: string) => {
    setSelectedParticipants((prev) =>
      prev.includes(userId) ? prev.filter((id) => id !== userId) : [...prev, userId]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!title.trim()) { setError("Title is required."); return; }
    if (!amount || parseFloat(amount) <= 0) { setError("Enter a valid amount."); return; }
    if (!paidBy) { setError("Select who paid."); return; }
    if (selectedParticipants.length === 0) { setError("Select at least one participant."); return; }

    if (splitType === "custom") {
      const total = selectedParticipants.reduce((sum, uid) => sum + parseFloat(customShares[uid] ?? "0"), 0);
      const diff = Math.abs(total - parseFloat(amount));
      if (diff > 0.01) {
        setError(`Custom shares sum to ${formatINR(total.toFixed(2))} but expense is ${formatINR(parseFloat(amount).toFixed(2))}. They must match exactly.`);
        return;
      }
    }

    setLoading(true);
    try {
      await expensesApi.createExpense(groupId!, {
        title: title.trim(),
        amount: parseFloat(amount).toFixed(2),
        paid_by: paidBy,
        split_type: splitType,
        participant_user_ids: selectedParticipants,
        custom_shares:
          splitType === "custom"
            ? selectedParticipants.map((uid) => ({
                user_id: uid,
                share_amount: parseFloat(customShares[uid] ?? "0").toFixed(2),
              }))
            : null,
      });
      navigate(`/groups/${groupId}`, { replace: true });
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.detail : "Failed to create expense.");
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title="Add Expense" showBack />
      <form onSubmit={handleSubmit} className="px-5 pt-5 flex flex-col gap-5 pb-safe">
        {error && (
          <div className="rounded-xl bg-red-50 border border-red-100 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="title">Title *</Label>
          <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)}
            placeholder="Dinner, Cab, Groceries…" required />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="amount">Total amount (₹) *</Label>
          <Input id="amount" type="number" min="0.01" step="0.01"
            value={amount} onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00" required />
        </div>

        {/* Paid by */}
        {!loadingMembers && (
          <div className="flex flex-col gap-1.5">
            <Label>Paid by *</Label>
            <div className="flex flex-wrap gap-2">
              {members.map((m) => (
                <button key={m.user_id} type="button"
                  onClick={() => setPaidBy(m.user_id)}
                  className={`px-3 py-1.5 rounded-xl text-sm font-medium border transition-colors ${
                    paidBy === m.user_id
                      ? "bg-brand-600 text-white border-brand-600"
                      : "bg-surface-card border-border text-ink"
                  }`}>
                  {m.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Split type */}
        <div className="flex flex-col gap-1.5">
          <Label>Split type</Label>
          <div className="flex gap-2">
            {(["equal", "custom"] as const).map((t) => (
              <button key={t} type="button" onClick={() => setSplitType(t)}
                className={`flex-1 py-2 rounded-xl text-sm font-medium border transition-colors ${
                  splitType === t
                    ? "bg-brand-600 text-white border-brand-600"
                    : "bg-surface-card border-border text-ink"
                }`}>
                {t === "equal" ? "Equal" : "Custom"}
              </button>
            ))}
          </div>
        </div>

        {/* Participants */}
        {!loadingMembers && (
          <div className="flex flex-col gap-2">
            <Label>Participants *</Label>
            <Card>
              <CardContent className="pt-4 pb-2">
                {members.map((m) => (
                  <div key={m.user_id} className="flex items-center justify-between py-2 border-b border-border/30 last:border-0">
                    <div className="flex items-center gap-2">
                      <input type="checkbox" id={`p-${m.user_id}`}
                        checked={selectedParticipants.includes(m.user_id)}
                        onChange={() => toggleParticipant(m.user_id)}
                        className="h-4 w-4 accent-brand-600" />
                      <label htmlFor={`p-${m.user_id}`} className="text-sm text-ink">{m.name}</label>
                    </div>
                    {splitType === "custom" && selectedParticipants.includes(m.user_id) && (
                      <Input
                        type="number" min="0" step="0.01"
                        value={customShares[m.user_id] ?? ""}
                        onChange={(e) => setCustomShares((prev) => ({ ...prev, [m.user_id]: e.target.value }))}
                        placeholder="0.00"
                        className="w-24 h-8 text-sm"
                      />
                    )}
                    {splitType === "equal" && selectedParticipants.includes(m.user_id) && amount && selectedParticipants.length > 0 && (
                      <span className="text-xs text-ink-muted">
                        {formatINR((parseFloat(amount) / selectedParticipants.length).toFixed(2))}
                      </span>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        )}

        <Button type="submit" size="lg" className="w-full" disabled={loading || loadingMembers}>
          {loading ? "Creating…" : "Add Expense"}
        </Button>
      </form>
    </div>
  );
}
