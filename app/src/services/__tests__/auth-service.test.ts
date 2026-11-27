import * as SecureStore from "expo-secure-store";

import { errorMessage } from "@/i18n/error-message";
import { ApiError } from "@/services/api-client";
import { authService, type User } from "@/services/auth-service";
import { tokenStore } from "@/services/token-store";

jest.mock("expo-secure-store", () => {
  const store = new Map<string, string>();
  return {
    getItemAsync: jest.fn(async (key: string) => store.get(key) ?? null),
    setItemAsync: jest.fn(async (key: string, value: string) => {
      store.set(key, value);
    }),
    deleteItemAsync: jest.fn(async (key: string) => {
      store.delete(key);
    }),
  };
});

const USER: User = {
  id: "00000000-0000-0000-0000-000000000001",
  email: "ana@example.com",
  display_name: "Ana",
  timezone: "America/Mexico_City",
  xp_total: 0,
  streak_current: 0,
  streak_longest: 0,
  created_at: "2026-11-23T00:00:00Z",
  energy: { current: 5, max: 5, next_refill_at: null },
};

function auth(access: string, refresh: string | null = `refresh-${access}`) {
  return { access_token: access, token_type: "bearer", expires_in: 900, refresh_token: refresh, user: USER };
}

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

type Route = (request: Request) => Response | Promise<Response>;
let routes: Record<string, Route>;
const calls: { path: string; auth: string | null; body: unknown }[] = [];

beforeEach(async () => {
  calls.length = 0;
  routes = {};
  tokenStore.set(null);
  await SecureStore.deleteItemAsync("circuitos.refresh_token");
  globalThis.fetch = jest.fn(async (input: RequestInfo | URL) => {
    const request = input instanceof Request ? input : new Request(String(input));
    const path = new URL(request.url).pathname;
    const text = await request.clone().text();
    calls.push({
      path,
      auth: request.headers.get("Authorization"),
      body: text ? JSON.parse(text) : null,
    });
    const route = routes[`${request.method} ${path}`];
    if (!route) {
      throw new Error(`ruta no simulada: ${request.method} ${path}`);
    }
    return route(request);
  }) as typeof fetch;
});

describe("login y registro", () => {
  it("login guarda el access token en memoria y el refresh en el llavero (móvil)", async () => {
    routes["POST /auth/login"] = () => json(200, auth("a1"));
    const listener = jest.fn();
    const unsubscribe = authService.subscribe(listener);

    const user = await authService.login("  ana@example.com ", "contraseña-segura");

    expect(user.display_name).toBe("Ana");
    expect(tokenStore.get()).toBe("a1");
    expect(await SecureStore.getItemAsync("circuitos.refresh_token")).toBe("refresh-a1");
    expect(calls[0].body).toEqual({
      email: "ana@example.com",
      password: "contraseña-segura",
      session_mode: "body",
    });
    expect(listener).toHaveBeenCalledWith(USER);
    unsubscribe();
  });

  it("registro manda la zona horaria del dispositivo", async () => {
    routes["POST /auth/register"] = () => json(201, auth("a1"));

    await authService.register({ email: "ana@example.com", password: "x".repeat(8), displayName: " Ana " });

    const body = calls[0].body as Record<string, string>;
    expect(body.display_name).toBe("Ana");
    expect(typeof body.timezone).toBe("string");
    expect(body.timezone.length).toBeGreaterThan(0);
  });

  it("credenciales incorrectas → ApiError con el código del backend", async () => {
    routes["POST /auth/login"] = () => json(401, { code: "invalid_credentials" });

    await expect(authService.login("ana@example.com", "mal")).rejects.toMatchObject({
      code: "invalid_credentials",
      status: 401,
    });
    expect(tokenStore.get()).toBeNull();
  });

  it("sin red → ApiError('network')", async () => {
    globalThis.fetch = jest.fn(async () => {
      throw new TypeError("Network request failed");
    }) as typeof fetch;

    await expect(authService.login("ana@example.com", "x")).rejects.toMatchObject({ code: "network" });
  });
});

describe("peticiones autenticadas", () => {
  beforeEach(async () => {
    routes["POST /auth/login"] = () => json(200, auth("viejo"));
    await authService.login("ana@example.com", "contraseña-segura");
    calls.length = 0;
  });

  it("manda el access token en Authorization", async () => {
    routes["GET /me"] = () => json(200, USER);

    await authService.getCurrentUser();

    expect(calls[0].auth).toBe("Bearer viejo");
  });

  it("si el token venció, renueva una vez y reintenta con el nuevo", async () => {
    routes["GET /me"] = (request) =>
      request.headers.get("Authorization") === "Bearer nuevo"
        ? json(200, USER)
        : json(401, { code: "invalid_token" });
    routes["POST /auth/refresh"] = () => json(200, auth("nuevo"));

    const user = await authService.getCurrentUser();

    expect(user.email).toBe("ana@example.com");
    expect(calls.map((c) => c.path)).toEqual(["/me", "/auth/refresh", "/me"]);
    expect(calls[1].body).toEqual({ refresh_token: "refresh-viejo", session_mode: "body" });
    expect(await SecureStore.getItemAsync("circuitos.refresh_token")).toBe("refresh-nuevo");
  });

  it("varias peticiones con 401 a la vez comparten UN solo refresh", async () => {
    routes["GET /me"] = (request) =>
      request.headers.get("Authorization") === "Bearer nuevo"
        ? json(200, USER)
        : json(401, { code: "invalid_token" });
    routes["POST /auth/refresh"] = () => json(200, auth("nuevo"));

    await Promise.all([authService.getCurrentUser(), authService.getCurrentUser(), authService.getCurrentUser()]);

    expect(calls.filter((c) => c.path === "/auth/refresh")).toHaveLength(1);
  });

  it("si el refresh también falla, cierra la sesión en el dispositivo", async () => {
    routes["GET /me"] = () => json(401, { code: "invalid_token" });
    routes["POST /auth/refresh"] = () => json(401, { code: "invalid_token" });
    const listener = jest.fn();
    authService.subscribe(listener);

    await expect(authService.getCurrentUser()).rejects.toBeInstanceOf(ApiError);

    expect(tokenStore.get()).toBeNull();
    expect(await SecureStore.getItemAsync("circuitos.refresh_token")).toBeNull();
    expect(listener).toHaveBeenLastCalledWith(null);
  });

  it("logout borra la sesión aunque no haya red", async () => {
    globalThis.fetch = jest.fn(async () => {
      throw new TypeError("Network request failed");
    }) as typeof fetch;

    await authService.logout();

    expect(tokenStore.get()).toBeNull();
    expect(await SecureStore.getItemAsync("circuitos.refresh_token")).toBeNull();
  });
});

describe("restaurar la sesión al abrir la app", () => {
  it("sin refresh guardado no llama al backend", async () => {
    expect(await authService.restore()).toBeNull();
    expect(calls).toHaveLength(0);
  });

  it("con refresh guardado recupera al usuario", async () => {
    await SecureStore.setItemAsync("circuitos.refresh_token", "guardado");
    routes["POST /auth/refresh"] = () => json(200, auth("a2"));

    expect(await authService.restore()).toEqual(USER);
    expect(tokenStore.get()).toBe("a2");
  });
});

describe("mensajes de error", () => {
  it.each([
    [new ApiError("invalid_credentials", 401), "El correo o la contraseña no son correctos."],
    [new ApiError("email_taken", 409), "Ya existe una cuenta con ese correo."],
    [new ApiError("network", 0), "No hay conexión con el servidor. Revisa tu internet e intenta de nuevo."],
    [new ApiError("codigo_que_no_existe", 500), "Algo salió mal. Intenta de nuevo."],
    [new Error("cualquier cosa"), "Algo salió mal. Intenta de nuevo."],
  ])("%p → %p", (error, message) => {
    expect(errorMessage(error)).toBe(message);
  });
});
