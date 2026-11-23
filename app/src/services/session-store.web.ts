/**
 * Web: el refresh token vive en una cookie httpOnly que pone el backend (`session_mode:
 * "cookie"`). JavaScript no puede leerla, así que aquí no se guarda nada.
 */
export const sessionStore = {
  mode: "cookie" as const,
  load: async (): Promise<string | null> => null,
  save: async (_token: string | null): Promise<void> => undefined,
};
