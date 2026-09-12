import { api } from "./client";
import type { BillScanResponse } from "@/types/api";

export const billScanApi = {
  // POST /bill-scan — multipart/form-data with field "file"
  scanBill: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api.upload<BillScanResponse>("/bill-scan", form);
  },
};
