import { api } from "./client";
import type {
  CreateExpenseRequest,
  CreateExpenseItemRequest,
  ExpenseItem,
  ExpenseDetailResponse,
  ExpenseHistoryItem,
  ExpenseResponse,
} from "@/types/api";

export const expensesApi = {
  // GET /groups/:groupId/expenses
  listGroupExpenses: (groupId: string) =>
    api.get<ExpenseHistoryItem[]>(`/groups/${groupId}/expenses`),

  // POST /groups/:groupId/expenses
  createExpense: (groupId: string, data: CreateExpenseRequest) =>
    api.post<ExpenseResponse>(`/groups/${groupId}/expenses`, data),

  // GET /expenses/:expenseId
  getExpense: (expenseId: string) =>
    api.get<ExpenseDetailResponse>(`/expenses/${expenseId}`),

  // PATCH /expenses/:expenseId
  updateExpense: (
    expenseId: string,
    data: { title?: string; description?: string; amount?: string }
  ) => api.patch<{ message: string; expense_id: string }>(`/expenses/${expenseId}`, data),

  // DELETE /expenses/:expenseId
  deleteExpense: (expenseId: string) =>
    api.delete<{ message: string; expense_id: string }>(`/expenses/${expenseId}`),

  // POST /expenses/:expenseId/items
  createExpenseItem: (expenseId: string, data: CreateExpenseItemRequest) =>
    api.post<ExpenseItem>(`/expenses/${expenseId}/items`, data),
};
