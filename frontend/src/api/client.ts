// ============================================================
// Centralised API client.
//
// Rules:
//  • All requests go through `apiRequest` — never raw fetch.
//  • credentials: 'include' is always set (HttpOnly session cookie).
//  • 401 → redirect to /login.
//  • Errors are normalised to ApiError.
// ============================================================

import type { ApiError } from "@/types/api";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export class ApiRequestError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiRequestError";
    this.status = status;
    this.detail = detail;
  }
}

async function parseError(res: Response): Promise<ApiRequestError> {
  let detail = `HTTP ${res.status}`;
  try {
    const json = (await res.json()) as { detail?: unknown };
    if (typeof json.detail === "string") {
      detail = json.detail;
    } else if (Array.isArray(json.detail)) {
      // Pydantic validation errors
      detail = (json.detail as Array<{ msg?: string }>)
        .map((e) => e.msg ?? "Validation error")
        .join(", ");
    }
  } catch {
    // non-JSON body — use status text
    detail = res.statusText || detail;
  }
  return new ApiRequestError(res.status, detail);
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${path}`;

  const res = await fetch(url, {
    ...options,
    credentials: "include", // always send session cookie
    headers: {
      // Only set Content-Type for non-FormData bodies
      ...(options.body && !(options.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...options.headers,
    },
  });

  if (res.status === 401) {
    // Only redirect to /login if we are NOT already on an auth page.
    // Redirecting unconditionally causes an infinite reload loop:
    //   AuthBootstrap calls /auth/me → 401 → replace("/login") → reload
    //   → AuthBootstrap fires again → 401 → replace("/login") → ...
    const onAuthPage = ["/login", "/register", "/join/"].some((p) =>
      window.location.pathname.startsWith(p)
    );
    if (!onAuthPage) {
      window.location.replace("/login");
    }
    throw new ApiRequestError(401, "Session expired. Please log in again.");
  }

  if (!res.ok) {
    throw await parseError(res);
  }

  // 204 No Content
  if (res.status === 204) {
    return undefined as unknown as T;
  }

  return res.json() as Promise<T>;
}

// Convenience wrappers
export const api = {
  get: <T>(path: string) => apiRequest<T>(path, { method: "GET" }),

  post: <T>(path: string, body?: unknown) =>
    apiRequest<T>(path, {
      method: "POST",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(path: string, body?: unknown) =>
    apiRequest<T>(path, {
      method: "PATCH",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(path: string) => apiRequest<T>(path, { method: "DELETE" }),

  upload: <T>(path: string, formData: FormData) =>
    apiRequest<T>(path, { method: "POST", body: formData }),
};

export type { ApiError };
