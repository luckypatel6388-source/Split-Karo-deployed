import { api } from "./client";
import type {
  CreateSettlementRequest,
  MarkSettlementPaidRequest,
  SettlementListResponse,
  SettlementRecord,
} from "@/types/api";

export const settlementsApi = {
  // GET /groups/:groupId/settlements — preview (not persisted)
  getSettlementSuggestions: (groupId: string) =>
    api.get<SettlementListResponse>(`/groups/${groupId}/settlements`),

  // POST /groups/:groupId/settlements/optimized — persist optimized settlements
  createOptimizedSettlements: (groupId: string) =>
    api.post<SettlementRecord[]>(`/groups/${groupId}/settlements/optimized`),

  // POST /groups/:groupId/settlements
  createSettlement: (groupId: string, data: CreateSettlementRequest) =>
    api.post<SettlementRecord>(`/groups/${groupId}/settlements`, data),

  // GET /groups/:groupId/settlements/records/:settlementId
  getSettlementRecord: (groupId: string, settlementId: string) =>
    api.get<SettlementRecord>(
      `/groups/${groupId}/settlements/records/${settlementId}`
    ),

  // PATCH /groups/:groupId/settlements/:settlementId/paid
  markSettlementPaid: (
    groupId: string,
    settlementId: string,
    data: MarkSettlementPaidRequest
  ) =>
    api.patch<SettlementRecord>(
      `/groups/${groupId}/settlements/${settlementId}/paid`,
      data
    ),
};
