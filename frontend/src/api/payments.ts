import { api } from "./client";
import type { PaymentInitiateRequest, PaymentInitiateResponse } from "@/types/api";

export const paymentsApi = {
  // POST /groups/:groupId/payments/initiate
  initiatePayment: (groupId: string, data: PaymentInitiateRequest) =>
    api.post<PaymentInitiateResponse>(
      `/groups/${groupId}/payments/initiate`,
      data
    ),

};
