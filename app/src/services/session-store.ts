import * as SecureStore from "expo-secure-store";

/**
 * Celular: el refresh token se guarda cifrado en el llavero del sistema (expo-secure-store) y
 * viaja en el cuerpo de las peticiones (`session_mode: "body"`). Nunca en AsyncStorage.
 * La versión web está en `session-store.web.ts`.
 */
const KEY = "circuitos.refresh_token";

export const sessionStore = {
  mode: "body" as const,
  load: (): Promise<string | null> => SecureStore.getItemAsync(KEY),
  save: async (token: string | null): Promise<void> => {
    if (token) {
      await SecureStore.setItemAsync(KEY, token);
    } else {
      await SecureStore.deleteItemAsync(KEY);
    }
  },
};
