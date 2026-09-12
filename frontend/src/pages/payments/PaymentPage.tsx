import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ExternalLink, CheckCircle, AlertCircle, ArrowRight } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { settlementsApi } from "@/api/settlements";
import { paymentsApi } from "@/api/payments";
import { formatINR } from "@/lib/formatters";
import { generateIdempotencyKey } from "@/lib/formatters";
import type { SettlementRecord, PaymentInitiateResponse } from "@/types/api";
import { ApiRequestError } from "@/api/client";

type Step = "loading" | "ready" | "initiated" | "confirmed" | "error";

export function PaymentPage() {
  const { groupId, settlementId } = useParams<{ groupId: string; settlementId: string }>();
  const navigate = useNavigate();

  const [settlement, setSettlement] = useState<SettlementRecord | null>(null);
  const [payment, setPayment] = useState<PaymentInitiateResponse | null>(null);
  const [step, setStep] = useState<Step>("loading");
  const [error, setError] = useState<string | null>(null);
  const [upiOpened, setUpiOpened] = useState(false);

  // Generate idempotency key ONCE — never regenerate on re-render
  const idempotencyKey = useRef(generateIdempotencyKey());

  useEffect(() => {
    if (!groupId || !settlementId) return;
    const pendingKey = `splitkaro:pending-payment:${settlementId}`;
    const storedPayment = sessionStorage.getItem(pendingKey);
    settlementsApi
      .getSettlementRecord(groupId, settlementId)
      .then((s) => {
        setSettlement(s);
        if (s.status === "paid") {
          sessionStorage.removeItem(pendingKey);
          setStep("confirmed");
          return;
        }
        if (storedPayment) {
          try {
            setPayment(JSON.parse(storedPayment) as PaymentInitiateResponse);
            setStep("initiated");
            setUpiOpened(true);
            return;
          } catch {
            sessionStorage.removeItem(pendingKey);
          }
        }
        setStep("ready");
      })
      .catch((err) => {
        setError(err instanceof ApiRequestError ? err.detail : "Failed to load settlement.");
        setStep("error");
      });
  }, [groupId, settlementId]);

  useEffect(() => {
    if (!groupId || !settlementId || !payment || settlement?.status === "paid") return;

    const poll = window.setInterval(async () => {
      try {
        const updated = await settlementsApi.getSettlementRecord(groupId, settlementId);
        setSettlement(updated);
        if (updated.status === "paid") {
          sessionStorage.removeItem(`splitkaro:pending-payment:${settlementId}`);
          setStep("confirmed");
        }
      } catch {
        // Keep the payment pending if a status check temporarily fails.
      }
    }, 5000);

    return () => window.clearInterval(poll);
  }, [groupId, settlementId, payment, settlement?.status]);

  const handleInitiatePayment = async () => {
    if (!groupId || !settlementId || !settlement) return;
    setError(null);
    setStep("initiated");
    try {
      const p = await paymentsApi.initiatePayment(groupId, {
        settlement_id: settlementId,
        idempotency_key: idempotencyKey.current,
      });
      setPayment(p);
      if (p.upi_uri) {
        sessionStorage.setItem(`splitkaro:pending-payment:${settlementId}`, JSON.stringify(p));
        window.location.href = p.upi_uri;
        setUpiOpened(true);
      }
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.detail : "Payment initiation failed.");
      setStep("ready");
    }
  };

  if (step === "loading") {
    return (
      <div>
        <PageHeader title="Payment" showBack />
        <div className="flex justify-center items-center py-20">
          <div className="h-8 w-8 rounded-full border-2 border-brand-200 border-t-brand-600 animate-spin" />
        </div>
      </div>
    );
  }

  if (step === "confirmed") {
    return (
      <div>
        <PageHeader title="Payment" showBack />
        <div className="flex flex-col items-center justify-center gap-4 px-5 py-16 text-center">
          <CheckCircle className="h-16 w-16 text-brand-600" aria-hidden />
          <p className="text-xl font-bold text-ink">Payment Confirmed</p>
          <p className="text-sm text-ink-muted">
            The settlement has been marked as paid.
          </p>
          <Button onClick={() => navigate(`/groups/${groupId}/settlements`, { replace: true })}>
            Back to Settlements
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader title="Payment" showBack />
      <div className="px-5 pt-5 flex flex-col gap-5 pb-safe">

        {/* Settlement summary */}
        {settlement && (
          <Card>
            <CardContent className="pt-5 pb-5">
              <p className="text-xs font-semibold text-ink-muted uppercase tracking-wide mb-3">Settlement</p>
              <div className="flex items-center justify-center gap-3 mb-4">
                <span className="text-sm font-semibold text-ink">{settlement.from_user_name}</span>
                <ArrowRight className="h-4 w-4 text-ink-muted" aria-hidden />
                <span className="text-sm font-semibold text-ink">{settlement.to_user_name}</span>
              </div>
              <p className="text-3xl font-bold text-center text-ink">{formatINR(settlement.amount)}</p>
              <p className="text-xs text-center text-ink-muted mt-1">
                Settlement ID: <span className="font-mono">{settlement.id.slice(0, 8)}…</span>
              </p>
            </CardContent>
          </Card>
        )}

        {error && (
          <div className="rounded-xl bg-red-50 border border-red-100 p-4 flex items-start gap-2 text-sm text-red-700">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" aria-hidden />
            <span>{error}</span>
          </div>
        )}

        {/* Step: ready to initiate */}
        {step === "ready" && settlement?.status === "pending" && (
          <Button size="lg" className="w-full" onClick={handleInitiatePayment}>Pay {formatINR(settlement.amount)} with UPI</Button>
        )}

        {settlement?.status === "paid" && (
          <div className="rounded-xl bg-brand-50 border border-brand-200 p-4 text-sm text-brand-700 text-center font-medium">
            This settlement is already paid.
          </div>
        )}

        {/* Step: payment initiated — show UPI info */}
        {step === "initiated" && !payment && (
          <div className="flex justify-center py-4">
            <div className="h-8 w-8 rounded-full border-2 border-brand-200 border-t-brand-600 animate-spin" />
          </div>
        )}

        {step === "initiated" && payment && (
          <div className="flex flex-col gap-4">
            {payment.idempotent_replay && (
              <div className="rounded-xl bg-amber-50 border border-amber-200 p-3 text-xs text-amber-800">
                A payment for this settlement was already initiated. Showing previous payment details.
              </div>
            )}

            <Card>
              <CardContent className="pt-5 pb-5 flex flex-col gap-3">
                <p className="text-xs font-semibold text-ink-muted uppercase tracking-wide">Payment details</p>
                <div className="flex justify-between text-sm">
                  <span className="text-ink-muted">Amount</span>
                  <span className="font-semibold text-ink">{formatINR(payment.amount)} {payment.currency}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-ink-muted">To</span>
                  <span className="text-ink">{settlement?.to_user_name}</span>
                </div>
                {payment.receiver_upi_id && (
                  <div className="flex justify-between text-sm">
                    <span className="text-ink-muted">UPI ID</span>
                    <span className="font-mono text-ink">{payment.receiver_upi_id}</span>
                  </div>
                )}
                {!payment.receiver_upi_id && (
                  <div className="rounded-lg bg-amber-50 p-3 text-xs text-amber-800">
                    Receiver has not set a UPI ID. Ask them to add one in their profile, or settle cash.
                  </div>
                )}
                <div className="flex justify-between text-sm">
                  <span className="text-ink-muted">Status</span>
                  <span className="text-ink capitalize">{payment.status}</span>
                </div>
              </CardContent>
            </Card>

            {payment.upi_uri && (
              <a
                href={payment.upi_uri}
                className="flex items-center justify-center gap-2 w-full h-12 rounded-2xl bg-brand-600 text-white font-semibold text-sm active:scale-[0.97] transition-transform"
              >
                <ExternalLink className="h-4 w-4" aria-hidden />
                {upiOpened ? "Open UPI App Again" : "Open in UPI App"}
              </a>
            )}

            <div className="flex flex-col gap-2">
              <div className="rounded-xl bg-amber-50 border border-amber-200 p-4 text-center">
                <p className="text-sm font-semibold text-amber-800">Waiting for payment confirmation</p>
                <p className="mt-1 text-xs text-amber-700">The settlement will update automatically after the payment provider confirms the transaction.</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
