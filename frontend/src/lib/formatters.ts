// ============================================================
// Display-only formatters.
// These functions convert backend Decimal strings to human-
// readable INR strings.  NO arithmetic is performed here.
// Backend is the authoritative source of all financial values.
// ============================================================

/**
 * Format a Decimal string from the backend as "₹ 1,250.00".
 * Accepts positive and negative values.
 */
export function formatINR(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "₹ 0.00";

  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "₹ 0.00";

  const abs = Math.abs(num);
  const formatted = abs.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return num < 0 ? `-₹ ${formatted}` : `₹ ${formatted}`;
}

/**
 * Return the sign of a balance string:
 *  positive → "receive"
 *  negative → "owe"
 *  zero     → "settled"
 */
export function balanceDirection(
  value: string | null | undefined
): "receive" | "owe" | "settled" {
  if (!value) return "settled";
  const num = parseFloat(value);
  if (isNaN(num) || num === 0) return "settled";
  return num > 0 ? "receive" : "owe";
}

/**
 * Format an ISO date string as "15 Aug 2026".
 */
export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

/**
 * Generate a cryptographically random idempotency key (UUID v4).
 * Used for payment initiation to prevent double-submission.
 */
export function generateIdempotencyKey(): string {
  return crypto.randomUUID();
}
