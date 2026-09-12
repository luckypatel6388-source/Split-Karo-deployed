import { api } from "./client";
import type { UpdateUPIRequest, UpdateUPIResponse } from "@/types/api";

export const usersApi = {
  // PATCH /users/me/upi
  updateUpi: (data: UpdateUPIRequest) =>
    api.patch<UpdateUPIResponse>("/users/me/upi", data),
};
