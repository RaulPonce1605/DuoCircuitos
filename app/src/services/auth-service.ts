import type { components } from "@/api/schema";
import { api, ApiError, unwrap } from "@/services/api-client";
import { sessionStore } from "@/services/session-store";
import { tokenStore } from "@/services/token-store";

export type User = components["schemas"]["UserRead"];
type AuthRead = components["schemas"]["AuthRead"];
type SessionListener = (user: User | null) => void;

export type RegisterInput = { email: string; password: string; displayName: string };

const listeners = new Set<SessionListener>();
let refreshInFlight: Promise<User | null> | null = null;

function emit(user: User | null): void {
  listeners.forEach((listener) => listener(user));
}

/** Zona horaria IANA del dispositivo: define el "día" de la racha en el backend. */
export function deviceTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  } catch {
    return "UTC";
  }
}

async function startSession(auth: AuthRead): Promise<User> {
  tokenStore.set(auth.access_token);
  // En web llega null (va en la cookie httpOnly) y no se guarda nada.
  if (sessionStore.mode === "body") {
    await sessionStore.save(auth.refresh_token);
  }
  emit(auth.user);
  return auth.user;
}

async function clearSession(): Promise<void> {
  tokenStore.set(null);
  await sessionStore.save(null);
  emit(null);
}

async function doRefresh(): Promise<User | null> {
  const stored = await sessionStore.load();
  if (sessionStore.mode === "body" && !stored) {
    return null;
  }
  try {
    const auth = await unwrap(() =>
      api.POST("/auth/refresh", {
        body: { refresh_token: stored, session_mode: sessionStore.mode },
      }),
    );
    return await startSession(auth);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      await clearSession();
      return null;
    }
    throw error; // sin red: se conserva la sesión guardada para intentar después
  }
}

export const authService = {
  async register(input: RegisterInput): Promise<User> {
    const auth = await unwrap(() =>
      api.POST("/auth/register", {
        body: {
          email: input.email.trim(),
          password: input.password,
          display_name: input.displayName.trim(),
          timezone: deviceTimezone(),
          session_mode: sessionStore.mode,
        },
      }),
    );
    return startSession(auth);
  },

  async login(email: string, password: string): Promise<User> {
    const auth = await unwrap(() =>
      api.POST("/auth/login", {
        body: { email: email.trim(), password, session_mode: sessionStore.mode },
      }),
    );
    return startSession(auth);
  },

  /** Renueva la sesión. Si varias peticiones lo piden a la vez, comparten un solo refresh. */
  refresh(): Promise<User | null> {
    refreshInFlight ??= doRefresh().finally(() => {
      refreshInFlight = null;
    });
    return refreshInFlight;
  },

  /** Al abrir la app: recupera la sesión guardada, si hay. */
  restore(): Promise<User | null> {
    return authService.refresh();
  },

  async logout(): Promise<void> {
    const stored = await sessionStore.load();
    try {
      await api.POST("/auth/logout", { body: { refresh_token: stored } });
    } catch {
      // Sin red: igual se cierra la sesión en este dispositivo.
    }
    await clearSession();
  },

  /** Ejecuta una petición autenticada; si el access token venció, renueva y reintenta una vez. */
  async authed<T>(
    call: () => Promise<{ data?: T; error?: unknown; response: Response }>,
  ): Promise<T> {
    try {
      return await unwrap(call);
    } catch (error) {
      if (!(error instanceof ApiError) || error.status !== 401) {
        throw error;
      }
      const user = await authService.refresh();
      if (!user) {
        throw error;
      }
      return unwrap(call);
    }
  },

  getCurrentUser(): Promise<User> {
    return authService.authed(() => api.GET("/me"));
  },

  subscribe(listener: SessionListener): () => void {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  },
};
