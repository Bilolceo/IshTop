/**
 * =============================================================================
 * AUTH STORE - Zustand State Management
 * =============================================================================
 *
 * Handles authentication state:
 * - User data
 * - Tokens (access + refresh)
 * - Login/Logout actions
 * - Auth status
 */

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { immer } from "zustand/middleware/immer";
import type { User } from "@/types/api";
import { getApiBaseUrl } from "@/lib/runtime-config";

// =============================================================================
// API CONFIG
// =============================================================================

const API_BASE_URL = getApiBaseUrl();

async function parseApiError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data?.detail === "string") return data.detail;
    if (typeof data?.message === "string") return data.message;
    if (typeof data?.error?.message === "string") return data.error.message;
    return `Request failed (${res.status})`;
  } catch {
    return `Request failed (${res.status})`;
  }
}

type UnknownRecord = Record<string, unknown>;

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isUserLike(value: unknown): value is User {
  if (!isRecord(value)) {
    return false;
  }

  const hasEmail = typeof value.email === "string";
  const hasIdentity =
    typeof value.full_name === "string" ||
    typeof value.role === "string" ||
    typeof value.id === "string";

  return hasEmail && hasIdentity;
}

function unwrapPayload(payload: unknown): UnknownRecord {
  if (!isRecord(payload)) {
    return {};
  }

  const nested = isRecord(payload.data) ? payload.data : null;
  return nested ?? payload;
}

function extractUser(payload: unknown): User | null {
  const root = unwrapPayload(payload);
  const nestedUser = isUserLike(root.user) ? root.user : null;
  if (nestedUser) {
    return nestedUser;
  }

  if (isUserLike(payload)) {
    return payload;
  }

  if (isRecord(payload) && isUserLike(payload.user)) {
    return payload.user;
  }

  return null;
}

function sanitizeUserForClient(user: User | null): User | null {
  if (!user) return null;
  return {
    id: user.id,
    full_name: user.full_name,
    role: user.role,
    email: user.email,
    phone: user.phone ?? null,
    avatar_url: user.avatar_url ?? null,
    company_name: user.company_name ?? null,
    company_website: user.company_website ?? null,
    company_cover_photo_url: user.company_cover_photo_url ?? null,
    company_gallery_images: Array.isArray(user.company_gallery_images) ? user.company_gallery_images : [],
    company_culture: user.company_culture ?? null,
    company_linkedin_url: user.company_linkedin_url ?? null,
    company_telegram_url: user.company_telegram_url ?? null,
    company_instagram_url: user.company_instagram_url ?? null,
    company_facebook_url: user.company_facebook_url ?? null,
    company_founded_year: user.company_founded_year ?? null,
    company_video_url: user.company_video_url ?? null,
    verification_state: user.verification_state ?? null,
    bio: user.bio ?? null,
    location: user.location ?? null,
    created_at: user.created_at,
    updated_at: user.updated_at ?? null,
    is_active: user.is_active ?? true,
    is_verified: user.is_verified ?? false,
  } as User;
}

function extractTokens(payload: unknown): { accessToken: string | null; refreshToken: string | null } {
  const root = unwrapPayload(payload);
  const nestedTokens = isRecord(root.tokens) ? root.tokens : null;

  const accessToken =
    (typeof root.access_token === "string" ? root.access_token : null) ??
    (typeof nestedTokens?.access_token === "string" ? nestedTokens.access_token : null);
  const refreshToken =
    (typeof root.refresh_token === "string" ? root.refresh_token : null) ??
    (typeof nestedTokens?.refresh_token === "string" ? nestedTokens.refresh_token : null);

  return { accessToken, refreshToken };
}

function applyAuthResponse(
  set: (updater: (state: AuthState) => void) => void,
  payload: unknown,
  options?: { requireTokens?: boolean }
) {
  const user = extractUser(payload);
  const { accessToken, refreshToken } = extractTokens(payload);
  const requireTokens = options?.requireTokens ?? false;

  if (requireTokens && (!accessToken || !refreshToken)) {
    throw new Error("Authentication response is missing access or refresh token");
  }

  set((state) => {
    state.user = sanitizeUserForClient(user);
    state.accessToken = accessToken;
    state.refreshToken = refreshToken;
    state.isAuthenticated = !!user || !!accessToken;
    state.isLoading = false;
  });

  return { user: sanitizeUserForClient(user), accessToken, refreshToken };
}

function extractMeUser(payload: unknown): User | null {
  return extractUser(payload);
}

// =============================================================================
// TYPES
// =============================================================================

interface AuthState {
  // State
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  hasHydrated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setUser: (user: User | null) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  setHasHydrated: (value: boolean) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<string | null>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  clearError: () => void;
  bootstrapSession: () => Promise<void>;
}

interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
  role?: "student" | "company";
  company_name?: string;
  company_website?: string;
}

// =============================================================================
// STORE
// =============================================================================

export const useAuthStore = create<AuthState>()(
  persist(
    immer((set, get) => ({
      // Initial state
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      hasHydrated: false,
      isLoading: false,
      error: null,

      // Set user
      setUser: (user) =>
        set((state) => {
          state.user = sanitizeUserForClient(user);
          state.isAuthenticated = !!user;
        }),

      // Set tokens
      setTokens: (accessToken, refreshToken) =>
        set((state) => {
          state.accessToken = accessToken;
          state.refreshToken = refreshToken;
          state.isAuthenticated = true;
        }),

      // Persist hydration gate (prevents redirect-to-login flashes on refresh).
      setHasHydrated: (value) =>
        set((state) => {
          state.hasHydrated = value;
        }),

      // Login
      login: async (email, password) => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
        });

        try {
          const res = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ email, password }),
          });

          if (!res.ok) {
            const msg = await parseApiError(res);
            throw new Error(msg);
          }

          const data = await res.json();
          applyAuthResponse(set, data);
        } catch (error: any) {
          set((state) => {
            state.isLoading = false;
            state.error = error.message || "Login failed";
          });
          throw error;
        }
      },

      // Register
      register: async (data) => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
        });

        try {
          const res = await fetch(`${API_BASE_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify(data),
          });

          if (!res.ok) {
            const msg = await parseApiError(res);
            throw new Error(msg);
          }

          const resp = await res.json();
          applyAuthResponse(set, resp);
        } catch (error: any) {
          set((state) => {
            state.isLoading = false;
            state.error = error.message || "Registration failed";
          });
          throw error;
        }
      },

      // Logout
      logout: async () => {
        const { accessToken, refreshToken } = get();
        set((state) => {
          state.isLoading = true;
          state.error = null;
        });

        try {
          // Best-effort server logout (token blacklist). Even if it fails,
          // we still clear local state.
          const headers: Record<string, string> = {
            "Content-Type": "application/json",
          };
          if (accessToken) {
            headers.Authorization = `Bearer ${accessToken}`;
          }

          await fetch(`${API_BASE_URL}/auth/logout`, {
            method: "POST",
            headers,
            credentials: "include",
            body: JSON.stringify(refreshToken ? { refresh_token: refreshToken } : {}),
          });
        } catch {
          // ignore
        } finally {
          set((state) => {
            state.user = null;
            state.accessToken = null;
            state.refreshToken = null;
            state.isAuthenticated = false;
            state.isLoading = false;
            state.error = null;
          });
        }
      },

      // Refresh access token
      refreshAccessToken: async () => {
        const { refreshToken } = get();

        try {
          const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify(refreshToken ? { refresh_token: refreshToken } : {}),
          });

          if (!res.ok) {
            const msg = await parseApiError(res);
            throw new Error(msg);
          }

          const data = await res.json();
          const { accessToken } = applyAuthResponse(set, data);

          return accessToken;
        } catch (error) {
          // If refresh fails, logout
          await get().logout();
          return null;
        }
      },

      // Update profile
      updateProfile: async (data) => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
        });

        try {
          const { accessToken } = get();
          const headers: Record<string, string> = {
            "Content-Type": "application/json",
          };
          if (accessToken) {
            headers.Authorization = `Bearer ${accessToken}`;
          }

          const res = await fetch(`${API_BASE_URL}/users/me`, {
            method: "PUT",
            headers,
            credentials: "include",
            body: JSON.stringify(data),
          });

          if (!res.ok) {
            const msg = await parseApiError(res);
            throw new Error(msg);
          }

          const updated = await res.json();
          const user = sanitizeUserForClient(
            (extractMeUser(updated) ?? extractUser(updated) ?? updated) as User
          );

          set((state) => {
            state.user = user;
            state.isLoading = false;
          });
        } catch (error: any) {
          set((state) => {
            state.isLoading = false;
            state.error = error.message || "Update failed";
          });
          throw error;
        }
      },

      // Clear error
      clearError: () =>
        set((state) => {
          state.error = null;
        }),

      bootstrapSession: async () => {
        const { isAuthenticated } = get();
        if (isAuthenticated) return;
        try {
          const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: "{}",
          });
          if (!res.ok) return;
          const data = await res.json();
          applyAuthResponse(set, data, { requireTokens: false });
        } catch {
          // ignore bootstrap failures
        }
      },
    })),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: sanitizeUserForClient(state.user),
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        const finalizeHydration = async () => {
          // Attempt silent cookie-based session restore before auth-gated redirects run.
          await state?.bootstrapSession();
          state?.setHasHydrated(true);
        };
        void finalizeHydration();
      },
    }
  )
);

// =============================================================================
// SELECTORS
// =============================================================================

export const selectUser = (state: AuthState) => state.user;
export const selectIsAuthenticated = (state: AuthState) => state.isAuthenticated;
export const selectIsLoading = (state: AuthState) => state.isLoading;
export const selectError = (state: AuthState) => state.error;
export const selectAccessToken = (state: AuthState) => state.accessToken;
