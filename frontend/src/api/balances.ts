import { api } from "./client";
import type { GroupBalanceResponse } from "@/types/api";

export const balancesApi = {
  // GET /groups/:groupId/balances
  getGroupBalances: (groupId: string) =>
    api.get<GroupBalanceResponse>(`/groups/${groupId}/balances`),
};
