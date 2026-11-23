import i18n from "@/i18n";
import es from "@/i18n/es.json";
import { ApiError } from "@/services/api-client";

type ErrorCode = keyof typeof es.errors;

function isKnownCode(code: string): code is ErrorCode {
  return Object.prototype.hasOwnProperty.call(es.errors, code);
}

/**
 * Mensaje para el usuario a partir de un error. Usa `errors.<code>` del backend; nunca muestra
 * el mensaje crudo del servidor (app/CLAUDE.md 4.3).
 */
export function errorMessage(error: unknown): string {
  const code = error instanceof ApiError ? error.code : "unknown";
  return i18n.t(`errors.${isKnownCode(code) ? code : "unknown"}`);
}
