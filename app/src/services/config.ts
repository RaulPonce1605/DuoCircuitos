/** URL del backend. Expo inyecta las variables EXPO_PUBLIC_* al compilar (ver app/.env.example). */
export const API_URL = (process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
