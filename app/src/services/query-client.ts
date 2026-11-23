import { QueryClient } from "@tanstack/react-query";

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        retry: 2,
      },
      mutations: {
        // Comprobar una respuesta no se reintenta solo: el usuario decide.
        retry: false,
      },
    },
  });
}
