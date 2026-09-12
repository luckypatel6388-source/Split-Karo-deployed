import { api } from "./client";
import type {
  CreateGroupRequest,
  CreateInviteResponse,
  GroupResponse,
  InvitePreviewResponse,
  JoinGroupResponse,
} from "@/types/api";

export const groupsApi = {
  // GET /users/me/groups — list all groups for current user
  listMyGroups: () => api.get<GroupResponse[]>("/users/me/groups"),

  // GET /groups/:id
  getGroup: (groupId: string) =>
    api.get<GroupResponse>(`/groups/${groupId}`),

  // POST /groups
  createGroup: (data: CreateGroupRequest) =>
    api.post<GroupResponse>("/groups", data),

  // POST /groups/:id/invite
  createInvite: (groupId: string) =>
    api.post<CreateInviteResponse>(`/groups/${groupId}/invite`),

  // GET /invites/:token  (no auth required)
  getInvitePreview: (token: string) =>
    api.get<InvitePreviewResponse>(`/invites/${token}`),

  // POST /invites/:token/join
  joinGroup: (token: string) =>
    api.post<JoinGroupResponse>(`/invites/${token}/join`),
};
