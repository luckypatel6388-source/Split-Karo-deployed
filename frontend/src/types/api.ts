// ============================================================
// TypeScript types mirroring the SplitKaro FastAPI schemas.
// All Decimal fields come over the wire as strings from JSON.
// Never perform arithmetic on these — display only.
// ============================================================

// ── Auth ────────────────────────────────────────────────────

export interface UserResponse {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  is_verified: boolean;
  is_active: boolean;
}

export interface AuthResponse {
  user: UserResponse;
}

export interface RegisterRequest {
  email: string;
  name: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

// ── Groups ──────────────────────────────────────────────────

export interface GroupMemberResponse {
  id: string;
  user_id: string;
  name: string;
  email: string;
  role: "admin" | "member";
  is_active: boolean;
}

export interface GroupResponse {
  id: string;
  name: string;
  description: string | null;
  created_by: string;
  members: GroupMemberResponse[];
}

export interface CreateGroupRequest {
  name: string;
  description?: string | null;
}

export interface CreateInviteResponse {
  token: string;
  invite_url: string;
}

export interface InvitePreviewResponse {
  group_id: string;
  group_name: string;
  group_description: string | null;
  expires_at: string | null;
}

export interface JoinGroupResponse {
  message: string;
  group_id: string;
  group_name: string;
}

// ── Expenses ────────────────────────────────────────────────

export type SplitType = "equal" | "custom";

export interface ExpenseParticipant {
  user_id: string;
  user_name: string;
  share_amount: string; // Decimal as string
}

export interface CustomShare {
  user_id: string;
  share_amount: string | null;
}

export interface CreateExpenseRequest {
  title: string;
  description?: string | null;
  amount: string; // send as string, backend parses Decimal
  paid_by: string;
  split_type: SplitType;
  participant_user_ids: string[];
  custom_shares?: CustomShare[] | null;
}

export interface ExpenseResponse {
  id: string;
  group_id: string;
  title: string;
  description: string | null;
  amount: string;
  paid_by: string;
  split_type: SplitType;
  participants: ExpenseParticipant[];
}

export interface ExpenseItemParticipant {
  user_id: string;
  user_name: string;
  share_amount: string;
}

export interface ExpenseItem {
  id: string;
  name: string;
  quantity: string;
  unit_price: string;
  total_price: string;
  participants: ExpenseItemParticipant[];
}

export interface CreateExpenseItemRequest {
  name: string;
  quantity?: string;
  unit_price: string;
  participants: Array<{
    user_id: string;
    share_amount: string;
  }>;
}

export interface ExpenseDetailResponse extends ExpenseResponse {
  payer_name: string;
  items: ExpenseItem[];
  update_logs: ExpenseUpdateLog[];
}

export interface ExpenseUpdateLog {
  id: string;
  updated_by: string;
  updated_by_name: string;
  previous_amount: string | null;
  updated_amount: string | null;
  previous_title: string | null;
  updated_title: string | null;
  previous_description: string | null;
  updated_description: string | null;
  changed_at: string;
}

export interface ExpenseHistoryItem {
  expense_id: string;
  title: string;
  amount: string;
  paid_by: string;
  payer_name: string;
  split_type: SplitType;
  participants: ExpenseParticipant[];
}

// ── Balances ────────────────────────────────────────────────

export interface UserBalance {
  user_id: string;
  user_name: string;
  balance: string; // signed Decimal string — positive = owed, negative = owes
}

export interface GroupBalanceResponse {
  group_id: string;
  balances: UserBalance[];
}

// ── Settlements ─────────────────────────────────────────────

export type SettlementStatus = "pending" | "paid";

export interface SettlementSuggestion {
  from_user_id: string;
  from_user_name: string;
  to_user_id: string;
  to_user_name: string;
  amount: string;
}

export interface SettlementListResponse {
  group_id: string;
  settlements: SettlementSuggestion[];
}

export interface SettlementRecord {
  id: string;
  group_id: string;
  from_user_id: string;
  from_user_name: string;
  to_user_id: string;
  to_user_name: string;
  amount: string;
  status: SettlementStatus;
  payment_method: string | null;
  payment_reference: string | null;
  paid_at: string | null;
}

export interface CreateSettlementRequest {
  from_user_id: string;
  to_user_id: string;
  amount: string;
  payment_method?: string | null;
}

export interface MarkSettlementPaidRequest {
  payment_reference?: string | null;
}

// ── Payments ────────────────────────────────────────────────

export interface PaymentInitiateRequest {
  settlement_id: string;
  idempotency_key: string;
}

export interface PaymentInitiateResponse {
  payment_id: string;
  settlement_id: string;
  payer_user_id: string;
  receiver_user_id: string;
  amount: string;
  currency: string;
  status: string;
  payment_method: string;
  receiver_upi_id: string | null;
  upi_uri: string | null;
  message: string;
  idempotent_replay: boolean;
}

export interface PaymentConfirmationRequest {
  payment_reference: string;
}

export interface PaymentConfirmationResponse {
  payment_id: string;
  settlement_id: string;
  status: string;
  settlement_status: string;
  payment_reference: string | null;
  message: string;
}

// ── Bill Scanner ────────────────────────────────────────────

export interface BillItem {
  name: string;
  quantity: string;
  unit_price: string;
  total_price: string;
}

export interface BillScanResult {
  merchant_name: string | null;
  bill_date: string | null;
  subtotal: string | null;
  tax: string | null;
  discount: string | null;
  total: string | null;
  items: BillItem[];
  confidence: number; // 0–1
  warnings: string[];
  raw_text: string | null;
}

export interface BillScanResponse {
  success: boolean;
  message: string;
  result: BillScanResult;
}

// ── Users ───────────────────────────────────────────────────

export interface UpdateUPIRequest {
  upi_id: string;
}

export interface UpdateUPIResponse {
  user_id: string;
  upi_id: string;
  upi_verified: boolean;
  message: string;
}

// ── API Error ───────────────────────────────────────────────

export interface ApiError {
  status: number;
  detail: string | Record<string, unknown>;
}
