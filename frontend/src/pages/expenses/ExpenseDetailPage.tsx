import { useEffect, useState } from "react";
import { Pencil, Save } from "lucide-react";
import { useParams } from "react-router-dom";
import { expensesApi } from "@/api/expenses";
import { ApiRequestError } from "@/api/client";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { formatINR } from "@/lib/formatters";
import type { ExpenseDetailResponse } from "@/types/api";

export function ExpenseDetailPage() {
  const { expenseId } = useParams<{ expenseId: string }>();
  const [expense, setExpense] = useState<ExpenseDetailResponse | null>(null);
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!expenseId) return;
    expensesApi.getExpense(expenseId)
      .then((result) => {
        setExpense(result);
        setTitle(result.title);
        setDescription(result.description ?? "");
        setAmount(result.amount);
      })
      .catch((err) => setError(err instanceof ApiRequestError ? err.detail : "Failed to load expense."))
      .finally(() => setLoading(false));
  }, [expenseId]);

  const save = async () => {
    if (!expenseId || !title.trim() || !amount.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await expensesApi.updateExpense(expenseId, { title: title.trim(), description: description.trim(), amount: amount.trim() });
      setExpense((current) => current ? { ...current, title: title.trim(), description: description.trim() || null, amount: amount.trim() } : current);
      setEditing(false);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.detail : "Failed to update expense.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <><PageHeader title="Expense" showBack /><div className="flex justify-center py-16"><div className="h-8 w-8 rounded-full border-2 border-brand-200 border-t-brand-600 animate-spin" /></div></>;
  if (error && !expense) return <><PageHeader title="Expense" showBack /><p className="mx-5 mt-5 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</p></>;
  if (!expense) return null;

  return (
    <div className="pb-safe">
      <PageHeader title="Expense details" showBack right={<Button variant="ghost" size="icon" onClick={() => setEditing((value) => !value)} aria-label="Edit expense"><Pencil className="h-4 w-4" aria-hidden /></Button>} />
      <div className="px-5 pt-5 flex flex-col gap-5">
        {error && <p className="rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</p>}
        <Card><CardContent className="pt-5 pb-5">
          {editing ? <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5"><Label htmlFor="expense-title">Title</Label><Input id="expense-title" value={title} onChange={(event) => setTitle(event.target.value)} maxLength={150} /></div>
            <div className="flex flex-col gap-1.5"><Label htmlFor="expense-description">Description</Label><textarea id="expense-description" value={description} onChange={(event) => setDescription(event.target.value)} maxLength={2000} className="min-h-24 w-full rounded-xl border border-border bg-surface-card px-4 py-3 text-sm text-ink outline-none focus:ring-2 focus:ring-brand-600" /></div>
            <div className="flex flex-col gap-1.5"><Label htmlFor="expense-amount">Amount</Label><Input id="expense-amount" value={amount} onChange={(event) => setAmount(event.target.value)} inputMode="decimal" /></div>
            <Button onClick={save} disabled={saving || !title.trim() || !amount.trim()}><Save className="h-4 w-4" aria-hidden />{saving ? "Saving…" : "Save changes"}</Button>
          </div> : <>
            <p className="text-xs font-semibold uppercase tracking-wide text-ink-muted">{expense.split_type} split</p>
            <h2 className="mt-2 text-xl font-bold text-ink">{expense.title}</h2>
            <p className="mt-1 text-sm text-ink-muted">Paid by {expense.payer_name}</p>
            <p className="mt-5 text-3xl font-bold text-ink">{formatINR(expense.amount)}</p>
            {expense.description && <p className="mt-3 text-sm text-ink-muted">{expense.description}</p>}
          </>}
        </CardContent></Card>
        <Card><CardContent className="pt-5 pb-3"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">Participants</p>{expense.participants.map((participant) => <div key={participant.user_id} className="flex justify-between border-b border-border/30 py-2 last:border-0"><span className="text-sm text-ink">{participant.user_name}</span><span className="text-sm font-medium text-ink">{formatINR(participant.share_amount)}</span></div>)}</CardContent></Card>
        {expense.items.length > 0 && <Card><CardContent className="pt-5 pb-3"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">Items</p>{expense.items.map((item) => <div key={item.id} className="flex justify-between border-b border-border/30 py-2 last:border-0"><span className="text-sm text-ink">{item.name} x {item.quantity}</span><span className="text-sm font-medium text-ink">{formatINR(item.total_price)}</span></div>)}</CardContent></Card>}
        {expense.update_logs.length > 0 && <Card><CardContent className="pt-5 pb-3"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">Update history</p>{expense.update_logs.map((log) => <div key={log.id} className="border-b border-border/30 py-3 last:border-0"><p className="text-sm font-medium text-ink">Updated by {log.updated_by_name}</p><p className="mt-1 text-xs text-ink-muted">{new Date(log.changed_at).toLocaleString()}</p><div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-muted">{log.previous_amount !== log.updated_amount && <span>Amount: {formatINR(log.previous_amount)} to {formatINR(log.updated_amount)}</span>}{log.previous_title !== log.updated_title && <span>Title: {log.previous_title || "(empty)"} to {log.updated_title || "(empty)"}</span>}{log.previous_description !== log.updated_description && <span>Description updated</span>}</div></div>)}</CardContent></Card>}
      </div>
    </div>
  );
}