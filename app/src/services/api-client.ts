import createClient from "openapi-fetch";
import { Platform } from "react-native";

import type { paths } from "@/api/schema";
import { API_URL } from "@/services/config";
import { tokenStore } from "@/services/token-store";

/**
 * Cliente tipado generado desde el OpenAPI (app/CLAUDE.md 4.2). Solo los servicios lo usan.
 * En web manda cookies (`credentials: "include"`) para que el backend lea la del refresh token.
 */
export const api = createClient<paths>({
  baseUrl: API_URL,
  credentials: Platform.OS === "web" ? "include" : "same-origin",
  // Se busca `fetch` en cada llamada (no una vez al crear el cliente): así las pruebas lo simulan.
  fetch: (request) => globalThis.fetch(request),
});

api.use({
  onRequest({ request }) {
    const token = tokenStore.get();
    if (token) {
      request.headers.set("Authorization", `Bearer ${token}`);
    }
    return request;
  },
});

/** Error del backend con su `code` estable (se traduce con `errors.<code>`). */
export class ApiError extends Error {
  constructor(
    readonly code: string,
    readonly status: number,
  ) {
    super(code);
    this.name = "ApiError";
  }
}

type ApiResult<T> = { data?: T; error?: unknown; response: Response };

/** Devuelve `data` o lanza `ApiError`; un fallo de red se vuelve `ApiError("network", 0)`. */
export async function unwrap<T>(call: () => Promise<ApiResult<T>>): Promise<T> {
  let result: ApiResult<T>;
  try {
    result = await call();
  } catch {
    throw new ApiError("network", 0);
  }
  if (result.response.ok && result.data !== undefined) {
    return result.data;
  }
  throw new ApiError(errorCode(result.error), result.response.status);
}

function errorCode(error: unknown): string {
  if (typeof error === "object" && error !== null && "code" in error) {
    const { code } = error;
    if (typeof code === "string") {
      return code;
    }
  }
  return "unknown";
}
