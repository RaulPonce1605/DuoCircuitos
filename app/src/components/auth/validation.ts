/** Validación rápida para dar mensajes al usuario. La validación real la hace el backend. */
export const MIN_PASSWORD_LENGTH = 8;

export function looksLikeEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}
