import "@/i18n";

import {
  SpaceGrotesk_600SemiBold,
  SpaceGrotesk_700Bold,
  useFonts,
} from "@expo-google-fonts/space-grotesk";
import { QueryClientProvider } from "@tanstack/react-query";
import * as SplashScreen from "expo-splash-screen";
import { type ReactNode, useEffect, useState } from "react";

import { createQueryClient } from "@/services/query-client";

void SplashScreen.preventAutoHideAsync().catch(() => {
  // En web o si ya se ocultó, no hay nada que hacer.
});

export function AppProviders({ children }: { children: ReactNode }) {
  const [queryClient] = useState(createQueryClient);
  const [fontsLoaded, fontError] = useFonts({ SpaceGrotesk_600SemiBold, SpaceGrotesk_700Bold });
  const ready = fontsLoaded || fontError !== null;

  useEffect(() => {
    if (ready) {
      void SplashScreen.hideAsync().catch(() => undefined);
    }
  }, [ready]);

  // Si la fuente falla, se sigue con la del sistema en lugar de dejar la app en blanco.
  if (!ready) {
    return null;
  }
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
